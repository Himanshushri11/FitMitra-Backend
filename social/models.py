"""
FitMitra Social Models
Production-ready social graph & content models for community-driven fitness platform
Designed for 100k+ users with optimized queries and indexing
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.utils import timezone


# ============================================================
# USER PROFILE EXTENSION (Social Layer)
# ============================================================

class UserProfile(models.Model):
    """
    Extended user profile for social features
    Separate from accounts.Profile to maintain separation of concerns
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='social_profile'
    )
    
    # Social Identity
    username = models.CharField(
        max_length=30, 
        unique=True, 
        db_index=True,
        validators=[MinLengthValidator(3)],
        help_text="Unique username for social features"
    )
    bio = models.TextField(
        max_length=500, 
        blank=True,
        help_text="User bio/description"
    )
    profile_picture = models.ImageField(
        upload_to='social/profiles/', 
        null=True, 
        blank=True,
        help_text="Social profile picture (can differ from main profile)"
    )
    
    # Fitness Identity
    fitness_goal = models.CharField(
        max_length=100,
        blank=True,
        help_text="Primary fitness goal (fat loss, muscle gain, endurance, etc.)"
    )
    
    # Social Stats (Denormalized for performance)
    followers_count = models.PositiveIntegerField(default=0, db_index=True)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    
    # Privacy & Settings
    is_private = models.BooleanField(
        default=False,
        help_text="Private accounts require follow approval"
    )
    allow_messages = models.BooleanField(
        default=True,
        help_text="Allow direct messages from followers"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_user_profile'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['-followers_count']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'User Social Profile'
        verbose_name_plural = 'User Social Profiles'
    
    def __str__(self):
        return f"@{self.username}"
    
    def get_profile_picture_url(self):
        """Return profile picture URL or default"""
        if self.profile_picture:
            return self.profile_picture.url
        # Fallback to main profile picture if exists
        if hasattr(self.user, 'profile') and self.user.profile.profile_pic:
            return self.user.profile.profile_pic.url
        return None


# ============================================================
# POST MODEL (User Generated Content)
# ============================================================

class Post(models.Model):
    """
    User-generated fitness content
    Core of the social feed
    """
    POST_TYPE_CHOICES = [
        ('text', 'Text Post'),
        ('image', 'Image Post'),
        ('workout', 'Workout Update'),
        ('achievement', 'Achievement'),
        ('tip', 'Fitness Tip'),
    ]
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    
    # Content
    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPE_CHOICES,
        default='text'
    )
    caption = models.TextField(
        max_length=2200,
        help_text="Post caption/text content"
    )
    image = models.ImageField(
        upload_to='social/posts/%Y/%m/',
        null=True,
        blank=True,
        help_text="Optional post image"
    )
    
    # Engagement Stats (Denormalized)
    likes_count = models.PositiveIntegerField(default=0, db_index=True)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    
    # Visibility
    is_active = models.BooleanField(
        default=True,
        help_text="Soft delete flag"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_post'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['-likes_count']),
            models.Index(fields=['is_active', '-created_at']),
        ]
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
    
    def __str__(self):
        return f"Post by @{self.author.social_profile.username} - {self.created_at.strftime('%Y-%m-%d')}"


# ============================================================
# LIKE MODEL
# ============================================================

class Like(models.Model):
    """
    Post likes with unique constraint to prevent duplicates
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'social_like'
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
    
    def __str__(self):
        return f"@{self.user.social_profile.username} liked Post #{self.post.id}"


# ============================================================
# COMMENT MODEL (Nested Comments Ready)
# ============================================================

class Comment(models.Model):
    """
    Comments on posts with support for nested replies
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    # Content
    text = models.TextField(
        max_length=1000,
        validators=[MinLengthValidator(1)]
    )
    
    # Nested Comments Support
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'social_comment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent']),
        ]
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
    
    def __str__(self):
        return f"Comment by @{self.author.social_profile.username} on Post #{self.post.id}"


# ============================================================
# FOLLOW MODEL (Social Graph)
# ============================================================

class Follow(models.Model):
    """
    Follow relationships between users
    Optimized for feed generation and social graph queries
    """
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    
    # Status (for private accounts)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='accepted'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'social_follow'
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'status']),
            models.Index(fields=['following', 'status']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
    
    def __str__(self):
        return f"@{self.follower.social_profile.username} → @{self.following.social_profile.username}"


# ============================================================
# MESSAGE MODEL (Direct Messaging)
# ============================================================

class Message(models.Model):
    """
    1-to-1 direct messages between users
    WebSocket-ready for real-time chat
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    
    # Content
    text = models.TextField(max_length=5000)
    
    # Status
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'social_message'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"Message from @{self.sender.social_profile.username} to @{self.recipient.social_profile.username}"
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


# ============================================================
# NOTIFICATION MODEL
# ============================================================

class Notification(models.Model):
    """
    User notifications for social interactions
    """
    NOTIFICATION_TYPES = [
        ('follow', 'New Follower'),
        ('like', 'Post Liked'),
        ('comment', 'New Comment'),
        ('mention', 'Mentioned in Post'),
        ('message', 'New Message'),
    ]
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='actions',
        help_text="User who triggered the notification"
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    
    # Related Objects (Generic approach)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Status
    is_read = models.BooleanField(default=False, db_index=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'social_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.notification_type} for @{self.recipient.social_profile.username}"


# ============================================================
# REPORT MODEL (Content Moderation)
# ============================================================

class Report(models.Model):
    """
    User reports for content moderation
    """
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake Account'),
        ('other', 'Other'),
    ]
    
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_made'
    )
    
    # Reported Content
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports'
    )
    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports_received'
    )
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES
    )
    description = models.TextField(max_length=1000, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'social_report'
        ordering = ['-created_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
    
    def __str__(self):
        return f"Report by @{self.reporter.social_profile.username} - {self.report_type}"


# ============================================================
# BLOCK MODEL (User Blocking)
# ============================================================

class Block(models.Model):
    """
    User blocking for safety
    """
    blocker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocking'
    )
    blocked = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'social_block'
        unique_together = ('blocker', 'blocked')
        indexes = [
            models.Index(fields=['blocker']),
            models.Index(fields=['blocked']),
        ]
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'
    
    def __str__(self):
        return f"@{self.blocker.social_profile.username} blocked @{self.blocked.social_profile.username}"
