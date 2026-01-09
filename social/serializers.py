"""
FitMitra Social Serializers
Production-ready DRF serializers for social features
Optimized for performance with select_related and prefetch_related
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Post, Like, Comment, Follow, 
    Message, Notification, Report, Block
)


# ============================================================
# USER PROFILE SERIALIZERS
# ============================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Public user profile serializer
    Used for displaying user info in posts, comments, etc.
    """
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()
    join_date = serializers.DateTimeField(source='created_at', read_only=True)
    is_following = serializers.SerializerMethodField()
    follows_you = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'full_name', 'email', 'bio',
            'profile_picture', 'profile_picture_url', 'fitness_goal',
            'followers_count', 'following_count', 'posts_count',
            'is_private', 'join_date', 'is_following', 'follows_you'
        ]
        read_only_fields = [
            'followers_count', 'following_count', 'posts_count'
        ]
    
    def get_profile_picture_url(self, obj):
        return obj.get_profile_picture_url()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from social.models import Follow
            return Follow.objects.filter(
                follower=request.user,
                following=obj.user,
                status='accepted'
            ).exists()
        return False

    def get_follows_you(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from social.models import Follow
            return Follow.objects.filter(
                follower=obj.user,
                following=request.user,
                status='accepted'
            ).exists()
        return False


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'profile_picture', 'fitness_goal',
            'is_private', 'allow_messages'
        ]


class UserMiniSerializer(serializers.ModelSerializer):
    """
    Minimal user info for nested serialization
    Used in posts, comments, etc. to avoid circular references
    """
    username = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'is_following']
    
    def get_username(self, obj):
        if hasattr(obj, 'social_profile') and obj.social_profile:
            return obj.social_profile.username
        return obj.username or f"user_{obj.id}"

    def get_profile_picture(self, obj):
        if hasattr(obj, 'social_profile') and obj.social_profile:
            return obj.social_profile.get_profile_picture_url()
        return None

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from social.models import Follow
            return Follow.objects.filter(
                follower=request.user,
                following=obj,
                status='accepted'
            ).exists()
        return False


# ============================================================
# POST SERIALIZERS
# ============================================================

class PostSerializer(serializers.ModelSerializer):
    """
    Main post serializer with author info and engagement stats
    """
    author = UserMiniSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'post_type', 'caption', 'image', 'image_url',
            'likes_count', 'comments_count', 'shares_count',
            'is_liked', 'can_edit', 'can_delete',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'author', 'likes_count', 'comments_count', 
            'shares_count', 'created_at', 'updated_at'
        ]
    
    def get_is_liked(self, obj):
        """Check if current user has liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def get_can_edit(self, obj):
        """Check if current user can edit this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False
    
    def get_can_delete(self, obj):
        """Check if current user can delete this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False
    
    def get_image_url(self, obj):
        """Get absolute URL for post image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating posts
    """
    class Meta:
        model = Post
        fields = ['post_type', 'caption', 'image']
    
    def validate_caption(self, value):
        """Ensure caption is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Caption cannot be empty")
        return value.strip()
    
    def create(self, validated_data):
        """Create post and update user's post count"""
        user = self.context['request'].user
        post = Post.objects.create(author=user, **validated_data)
        
        # Update user's post count
        if hasattr(user, 'social_profile'):
            user.social_profile.posts_count += 1
            user.social_profile.save(update_fields=['posts_count'])
        
        return post


# ============================================================
# COMMENT SERIALIZERS
# ============================================================

class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer with nested replies support
    """
    author = UserMiniSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'text', 'parent',
            'likes_count', 'replies', 'can_delete',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'likes_count', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """Get nested replies (limit depth to avoid recursion)"""
        if obj.parent is None:  # Only get replies for top-level comments
            replies = obj.replies.filter(is_active=True).select_related(
                'author', 'author__social_profile'
            )[:5]  # Limit to 5 replies
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_can_delete(self, obj):
        """Check if current user can delete this comment"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user or obj.post.author == request.user
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments
    """
    class Meta:
        model = Comment
        fields = ['post', 'text', 'parent']
    
    def validate(self, data):
        """Validate comment data"""
        # Ensure parent comment belongs to the same post
        if data.get('parent') and data['parent'].post != data['post']:
            raise serializers.ValidationError(
                "Parent comment must belong to the same post"
            )
        return data
    
    def create(self, validated_data):
        """Create comment and update post's comment count"""
        user = self.context['request'].user
        comment = Comment.objects.create(author=user, **validated_data)
        
        # Update post's comment count
        post = validated_data['post']
        post.comments_count += 1
        post.save(update_fields=['comments_count'])
        
        return comment


# ============================================================
# FOLLOW SERIALIZERS
# ============================================================

class FollowSerializer(serializers.ModelSerializer):
    """
    Follow relationship serializer
    """
    follower = UserMiniSerializer(read_only=True)
    following = UserMiniSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']


class FollowActionSerializer(serializers.Serializer):
    """
    Serializer for follow/unfollow actions
    """
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        """Ensure user exists"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value


# ============================================================
# MESSAGE SERIALIZERS
# ============================================================

class MessageSerializer(serializers.ModelSerializer):
    """
    Message serializer for chat
    """
    sender = UserMiniSerializer(read_only=True)
    recipient = UserMiniSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient', 'text',
            'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['sender', 'is_read', 'read_at', 'created_at']


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for sending messages
    """
    recipient_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Message
        fields = ['recipient_id', 'text']
    
    def validate_recipient_id(self, value):
        """Validate recipient exists and is not the sender"""
        request = self.context['request']
        
        if value == request.user.id:
            raise serializers.ValidationError("Cannot send message to yourself")
        
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Recipient does not exist")
        
        return value
    
        # Relaxed logic: Allow messaging if user follows recipient 
        # OR if recipient has allow_messages=True
        is_following = Follow.objects.filter(
            follower=request.user,
            following_id=recipient_id,
            status='accepted'
        ).exists()
        
        recipient_profile = UserProfile.objects.filter(user_id=recipient_id).first()
        allow_messages = recipient_profile.allow_messages if recipient_profile else True
        
        if not (is_following or allow_messages):
            raise serializers.ValidationError(
                "Recipient must follow you back or have public messaging enabled"
            )
        
        return data
    
    def create(self, validated_data):
        """Create message"""
        recipient_id = validated_data.pop('recipient_id')
        recipient = User.objects.get(id=recipient_id)
        
        message = Message.objects.create(
            sender=self.context['request'].user,
            recipient=recipient,
            **validated_data
        )
        
        return message


class ConversationSerializer(serializers.Serializer):
    """
    Serializer for conversation list
    """
    user = UserMiniSerializer()
    last_message = MessageSerializer()
    unread_count = serializers.IntegerField()


# ============================================================
# NOTIFICATION SERIALIZERS
# ============================================================

class NotificationSerializer(serializers.ModelSerializer):
    """
    Notification serializer
    """
    actor = UserMiniSerializer(read_only=True)
    post_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'actor', 'notification_type', 'post_data',
            'is_read', 'created_at'
        ]
        read_only_fields = ['actor', 'notification_type', 'created_at']
    
    def get_post_data(self, obj):
        """Get minimal post data if notification is related to a post"""
        if obj.post:
            return {
                'id': obj.post.id,
                'caption': obj.post.caption[:100],  # Truncate
            }
        return None


# ============================================================
# REPORT SERIALIZERS
# ============================================================

class ReportSerializer(serializers.ModelSerializer):
    """
    Report serializer for content moderation
    """
    class Meta:
        model = Report
        fields = [
            'id', 'report_type', 'description',
            'post', 'reported_user', 'status', 'created_at'
        ]
        read_only_fields = ['reporter', 'status', 'created_at']
    
    def validate(self, data):
        """Ensure either post or user is being reported"""
        if not data.get('post') and not data.get('reported_user'):
            raise serializers.ValidationError(
                "Must report either a post or a user"
            )
        return data
    
    def create(self, validated_data):
        """Create report"""
        return Report.objects.create(
            reporter=self.context['request'].user,
            **validated_data
        )


# ============================================================
# FEED SERIALIZERS
# ============================================================

class FeedPostSerializer(PostSerializer):
    """
    Extended post serializer for feed with recent comments
    """
    recent_comments = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['recent_comments']
    
    def get_recent_comments(self, obj):
        """Get 2 most recent comments"""
        comments = obj.comments.filter(
            is_active=True,
            parent=None  # Only top-level comments
        ).select_related(
            'author', 'author__social_profile'
        ).order_by('-created_at')[:2]
        
        return CommentSerializer(comments, many=True, context=self.context).data
