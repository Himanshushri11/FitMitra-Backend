"""
FitMitra Social Views
Production-ready API views for social features
Optimized for performance with pagination, caching, and efficient queries
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Prefetch, Count, Exists, OuterRef
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone

from .models import (
    UserProfile, Post, Like, Comment, Follow,
    Message, Notification, Report, Block
)
from .serializers import (
    UserProfileSerializer, UserProfileUpdateSerializer,
    PostSerializer, PostCreateSerializer, FeedPostSerializer,
    CommentSerializer, CommentCreateSerializer,
    FollowSerializer, FollowActionSerializer,
    MessageSerializer, MessageCreateSerializer, ConversationSerializer,
    NotificationSerializer, ReportSerializer
)


# ============================================================
# PAGINATION CLASSES
# ============================================================

class StandardPagination(PageNumberPagination):
    """Standard pagination for lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class FeedPagination(PageNumberPagination):
    """Pagination for feed"""
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 50


# ============================================================
# USER PROFILE VIEWS
# ============================================================

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profiles
    Supports viewing, updating, and searching profiles
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'user__first_name', 'user__last_name', 'bio']
    lookup_field = 'username'
    
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get or update current user's social profile
        """
        # Try to get the profile, create if missing (failsafe for signals)
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'username': request.user.username}
        )
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
            
        # Handle Updates (PUT/PATCH)
        serializer = UserProfileUpdateSerializer(
            profile, 
            data=request.data, 
            partial=(request.method == 'PATCH'),
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(profile, context={'request': request}).data)
    
    def get_queryset(self):
        """Optimize query with select_related"""
        return UserProfile.objects.select_related('user').all()
    
    def get_serializer_class(self):
        """Use different serializer for updates"""
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer
    
    def retrieve(self, request, username=None):
        """
        Get user profile by username with additional stats
        """
        profile = get_object_or_404(UserProfile, username=username)
        serializer = self.get_serializer(profile)
        
        data = serializer.data
        
        # Add follow status if user is authenticated
        if request.user.is_authenticated:
            data['is_following'] = Follow.objects.filter(
                follower=request.user,
                following=profile.user,
                status='accepted'
            ).exists()
            
            data['follows_you'] = Follow.objects.filter(
                follower=profile.user,
                following=request.user,
                status='accepted'
            ).exists()
            
            data['is_blocked'] = Block.objects.filter(
                blocker=request.user,
                blocked=profile.user
            ).exists()
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, username=None):
        """Get all posts by a user"""
        profile = get_object_or_404(UserProfile, username=username)
        
        posts = Post.objects.filter(
            author=profile.user,
            is_active=True
        ).select_related(
            'author', 'author__social_profile'
        ).prefetch_related(
            'likes', 'comments'
        ).order_by('-created_at')
        
        paginator = StandardPagination()
        page = paginator.paginate_queryset(posts, request)
        
        serializer = PostSerializer(
            page, 
            many=True, 
            context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def followers(self, request, username=None):
        """Get user's followers"""
        profile = get_object_or_404(UserProfile, username=username)
        
        followers = Follow.objects.filter(
            following=profile.user,
            status='accepted'
        ).select_related(
            'follower', 'follower__social_profile'
        ).order_by('-created_at')
        
        paginator = StandardPagination()
        page = paginator.paginate_queryset(followers, request)
        
        serializer = FollowSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def following(self, request, username=None):
        """Get users that this user follows"""
        profile = get_object_or_404(UserProfile, username=username)
        
        following = Follow.objects.filter(
            follower=profile.user,
            status='accepted'
        ).select_related(
            'following', 'following__social_profile'
        ).order_by('-created_at')
        
        paginator = StandardPagination()
        page = paginator.paginate_queryset(following, request)
        
        serializer = FollowSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


# ============================================================
# POST VIEWS
# ============================================================

class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for posts (CRUD operations)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        """Optimize query with select_related and prefetch_related"""
        return Post.objects.filter(
            is_active=True
        ).select_related(
            'author', 'author__social_profile'
        ).prefetch_related(
            'likes', 'comments'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    def create(self, request, *args, **kwargs):
        """Create post and return full serialized data"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = self.perform_create(serializer)
        
        # Return full post data using PostSerializer
        return Response(
            PostSerializer(post, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        """Save post and return instance"""
        return serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete post"""
        if instance.author == self.request.user:
            instance.is_active = False
            instance.save()
            
            # Update user's post count
            if hasattr(instance.author, 'social_profile'):
                profile = instance.author.social_profile
                profile.posts_count = max(0, profile.posts_count - 1)
                profile.save(update_fields=['posts_count'])
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like a post"""
        post = self.get_object()
        
        # Check if already liked
        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )
        
        if created:
            # Update post's like count
            post.likes_count += 1
            post.save(update_fields=['likes_count'])
            
            # Create notification
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    notification_type='like',
                    post=post
                )
            
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        
        return Response({'status': 'already_liked'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        """Unlike a post"""
        post = self.get_object()
        
        try:
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            
            # Update post's like count
            post.likes_count = max(0, post.likes_count - 1)
            post.save(update_fields=['likes_count'])
            
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response(
                {'error': 'Post not liked'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all comments for a post"""
        post = self.get_object()
        
        comments = Comment.objects.filter(
            post=post,
            is_active=True,
            parent=None  # Only top-level comments
        ).select_related(
            'author', 'author__social_profile'
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=Comment.objects.filter(is_active=True).select_related(
                    'author', 'author__social_profile'
                )
            )
        ).order_by('-created_at')
        
        paginator = StandardPagination()
        page = paginator.paginate_queryset(comments, request)
        
        serializer = CommentSerializer(
            page,
            many=True,
            context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        """Add a comment to a post"""
        post = self.get_object()
        
        serializer = CommentCreateSerializer(
            data={**request.data, 'post': post.id},
            context={'request': request}
        )
        
        if serializer.is_valid():
            comment = serializer.save()
            
            # Create notification
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment
                )
            
            return Response(
                CommentSerializer(comment, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# FEED VIEW
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feed_view(request):
    """
    Main feed view - shows posts from followed users + trending content
    Optimized for performance
    """
    user = request.user
    
    # Get users that current user follows
    following_ids = Follow.objects.filter(
        follower=user,
        status='accepted'
    ).values_list('following_id', flat=True)
    
    # Get blocked users
    blocked_ids = Block.objects.filter(
        blocker=user
    ).values_list('blocked_id', flat=True)
    
    # Build feed query
    # If user follows few people, show more trending/recent content
    is_new_user = len(following_ids) < 5
    
    if is_new_user:
        # For new users, show followed users + most recent active posts
        feed_posts = Post.objects.filter(
            is_active=True
        ).exclude(
            author_id__in=blocked_ids
        ).select_related(
            'author', 'author__social_profile'
        ).prefetch_related(
            'likes', 'comments'
        ).order_by('-created_at')
    else:
        # For established users, prioritize followed users + trending
        feed_posts = Post.objects.filter(
            is_active=True
        ).exclude(
            author_id__in=blocked_ids
        ).filter(
            Q(author_id__in=following_ids) |
            Q(likes_count__gte=5) |  # Lowered trending threshold
            Q(created_at__gte=timezone.now() - timezone.timedelta(days=1)) # Recent posts
        ).select_related(
            'author', 'author__social_profile'
        ).prefetch_related(
            'likes', 'comments'
        ).distinct().order_by('-created_at')
    
    # Paginate
    paginator = FeedPagination()
    page = paginator.paginate_queryset(feed_posts, request)
    
    serializer = FeedPostSerializer(
        page,
        many=True,
        context={'request': request}
    )
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def explore_feed_view(request):
    """
    Explore feed - discover new content and users
    Shows trending posts from the entire community
    """
    user = request.user
    
    # Get blocked users
    blocked_ids = Block.objects.filter(
        blocker=user
    ).values_list('blocked_id', flat=True)
    
    # Get trending posts (high engagement, recent)
    explore_posts = Post.objects.filter(
        is_active=True
    ).exclude(
        author_id__in=blocked_ids
    ).exclude(
        author=user  # Don't show own posts
    ).select_related(
        'author', 'author__social_profile'
    ).prefetch_related(
        'likes', 'comments'
    ).order_by('-likes_count', '-created_at')
    
    # Paginate
    paginator = FeedPagination()
    page = paginator.paginate_queryset(explore_posts, request)
    
    serializer = FeedPostSerializer(
        page,
        many=True,
        context={'request': request}
    )
    
    return paginator.get_paginated_response(serializer.data)


# ============================================================
# FOLLOW VIEWS
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request):
    """Follow a user"""
    serializer = FollowActionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_to_follow = get_object_or_404(User, id=serializer.validated_data['user_id'])
    
    # Can't follow yourself
    if user_to_follow == request.user:
        return Response(
            {'error': 'Cannot follow yourself'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if blocked
    if Block.objects.filter(blocker=user_to_follow, blocked=request.user).exists():
        return Response(
            {'error': 'Cannot follow this user'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create or get follow relationship
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow,
        defaults={'status': 'accepted'}  # Auto-accept for now
    )
    
    if created:
        # Update follower/following counts
        if hasattr(request.user, 'social_profile'):
            request.user.social_profile.following_count += 1
            request.user.social_profile.save(update_fields=['following_count'])
        
        if hasattr(user_to_follow, 'social_profile'):
            user_to_follow.social_profile.followers_count += 1
            user_to_follow.social_profile.save(update_fields=['followers_count'])
        
        # Create notification
        Notification.objects.create(
            recipient=user_to_follow,
            actor=request.user,
            notification_type='follow'
        )
        
        return Response({'status': 'followed'}, status=status.HTTP_201_CREATED)
    
    return Response({'status': 'already_following'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request):
    """Unfollow a user"""
    serializer = FollowActionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_to_unfollow = get_object_or_404(User, id=serializer.validated_data['user_id'])
    
    try:
        follow = Follow.objects.get(
            follower=request.user,
            following=user_to_unfollow
        )
        follow.delete()
        
        # Update follower/following counts
        if hasattr(request.user, 'social_profile'):
            request.user.social_profile.following_count = max(
                0, request.user.social_profile.following_count - 1
            )
            request.user.social_profile.save(update_fields=['following_count'])
        
        if hasattr(user_to_unfollow, 'social_profile'):
            user_to_unfollow.social_profile.followers_count = max(
                0, user_to_unfollow.social_profile.followers_count - 1
            )
            user_to_unfollow.social_profile.save(update_fields=['followers_count'])
        
        return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)
    
    except Follow.DoesNotExist:
        return Response(
            {'error': 'Not following this user'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# MESSAGE VIEWS
# ============================================================

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for direct messages
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        """Get messages for current user"""
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).select_related(
            'sender', 'sender__social_profile',
            'recipient', 'recipient__social_profile'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Get list of conversations with last message and unread count"""
        user = request.user
        
        # Get all users with whom current user has conversations
        conversations_data = []
        
        # Get unique conversation partners
        sent_to = Message.objects.filter(sender=user).values_list('recipient', flat=True).distinct()
        received_from = Message.objects.filter(recipient=user).values_list('sender', flat=True).distinct()
        
        conversation_partners = set(list(sent_to) + list(received_from))
        
        for partner_id in conversation_partners:
            partner = User.objects.select_related('social_profile').get(id=partner_id)
            
            # Get last message
            last_message = Message.objects.filter(
                Q(sender=user, recipient=partner) |
                Q(sender=partner, recipient=user)
            ).select_related('sender', 'recipient').order_by('-created_at').first()
            
            # Get unread count
            unread_count = Message.objects.filter(
                sender=partner,
                recipient=user,
                is_read=False
            ).count()
            
            conversations_data.append({
                'user': partner,
                'last_message': last_message,
                'unread_count': unread_count
            })
        
        # Sort by last message time
        conversations_data.sort(
            key=lambda x: x['last_message'].created_at if x['last_message'] else timezone.now(),
            reverse=True
        )
        
        serializer = ConversationSerializer(conversations_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get conversation with a specific user"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        other_user = get_object_or_404(User, id=user_id)
        
        # Get messages between users
        messages = Message.objects.filter(
            Q(sender=request.user, recipient=other_user) |
            Q(sender=other_user, recipient=request.user)
        ).select_related(
            'sender', 'sender__social_profile',
            'recipient', 'recipient__social_profile'
        ).order_by('created_at')
        
        # Mark messages as read
        Message.objects.filter(
            sender=other_user,
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        paginator = StandardPagination()
        page = paginator.paginate_queryset(messages, request)
        
        serializer = MessageSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


# ============================================================
# NOTIFICATION VIEWS
# ============================================================

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for notifications (read-only)
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        """Get notifications for current user"""
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            'actor', 'actor__social_profile', 'post'
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({'status': 'marked_all_read'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        
        return Response({'status': 'marked_read'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return Response({'unread_count': count})


# ============================================================
# MODERATION VIEWS
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_content(request):
    """Report a post or user"""
    serializer = ReportSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'status': 'reported'},
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_user(request):
    """Block a user"""
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response(
            {'error': 'user_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_to_block = get_object_or_404(User, id=user_id)
    
    if user_to_block == request.user:
        return Response(
            {'error': 'Cannot block yourself'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    block, created = Block.objects.get_or_create(
        blocker=request.user,
        blocked=user_to_block
    )
    
    if created:
        # Remove follow relationships
        Follow.objects.filter(
            Q(follower=request.user, following=user_to_block) |
            Q(follower=user_to_block, following=request.user)
        ).delete()
        
        return Response({'status': 'blocked'}, status=status.HTTP_201_CREATED)
    
    return Response({'status': 'already_blocked'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unblock_user(request):
    """Unblock a user"""
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response(
            {'error': 'user_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_to_unblock = get_object_or_404(User, id=user_id)
    
    try:
        block = Block.objects.get(
            blocker=request.user,
            blocked=user_to_unblock
        )
        block.delete()
        return Response({'status': 'unblocked'}, status=status.HTTP_200_OK)
    
    except Block.DoesNotExist:
        return Response(
            {'error': 'User not blocked'},
            status=status.HTTP_400_BAD_REQUEST
        )
