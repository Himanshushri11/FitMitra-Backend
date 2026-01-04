from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from django.contrib.auth.models import User
from explore.models import Gym
from .models import AdminAction, LoginLog
from .serializers import AdminUserSerializer, AdminGymSerializer, AdminActionSerializer, LoginLogSerializer
from django.utils import timezone
from datetime import timedelta

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class AdminDashboardStatsView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        total_users = User.objects.count()
        total_gyms = Gym.objects.count()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        active_users = User.objects.filter(last_login__date=today).count()
        
        # Recent activity
        recent_logins = LoginLog.objects.order_by('-timestamp')[:5]
        recent_actions = AdminAction.objects.order_by('-timestamp')[:5]

        return Response({
            "stats": {
                "total_users": total_users,
                "total_gyms": total_gyms,
                "new_users_today": new_users_today,
                "active_users": active_users,
            },
            "recent_logins": LoginLogSerializer(recent_logins, many=True).data,
            "recent_actions": AdminActionSerializer(recent_actions, many=True).data
        })

class AdminUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer

    def perform_destroy(self, instance):
        # Soft delete could be implemented here
        AdminAction.objects.create(
            admin=self.request.user,
            action_type='DELETE',
            target_model='USER',
            target_id=str(instance.id),
            details=f"Deleted user {instance.username}"
        )
        instance.delete()

    def perform_update(self, serializer):
        instance = serializer.save()
        AdminAction.objects.create(
            admin=self.request.user,
            action_type='UPDATE',
            target_model='USER',
            target_id=str(instance.id),
            details=f"Updated user {instance.username}"
        )

class AdminGymViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Gym.objects.all().order_by('-created_at')
    serializer_class = AdminGymSerializer

    def create(self, request, *args, **kwargs):
        # Handle facilities being sent as a JSON string in multipart/form-data
        data = request.data.copy()
        if isinstance(data.get('facilities'), str):
            import json
            try:
                data['facilities'] = json.loads(data['facilities'])
            except:
                pass
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        instance = serializer.save()
        
        # Handle gallery images
        from explore.models import GymImage
        images = self.request.FILES.getlist('gallery_images')
        for img in images:
            GymImage.objects.create(gym=instance, image=img)

        AdminAction.objects.create(
            admin=self.request.user,
            action_type='CREATE',
            target_model='GYM',
            target_id=str(instance.id),
            details=f"Created gym {instance.name} with {len(images)} gallery images"
        )

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        if isinstance(data.get('facilities'), str):
            import json
            try:
                data['facilities'] = json.loads(data['facilities'])
            except:
                pass
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Handle new gallery images during update
        from explore.models import GymImage
        images = self.request.FILES.getlist('gallery_images')
        for img in images:
            GymImage.objects.create(gym=instance, image=img)
            
        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        AdminAction.objects.create(
            admin=self.request.user,
            action_type='UPDATE',
            target_model='GYM',
            target_id=str(instance.id),
            details=f"Updated gym {instance.name}"
        )

    def perform_destroy(self, instance):
        AdminAction.objects.create(
            admin=self.request.user,
            action_type='DELETE',
            target_model='GYM',
            target_id=str(instance.id),
            details=f"Deleted gym {instance.name}"
        )
        instance.delete()

class AdminActionListView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        actions = AdminAction.objects.all().order_by('-timestamp')
        serializer = AdminActionSerializer(actions, many=True)
        return Response(serializer.data)
