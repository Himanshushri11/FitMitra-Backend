from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import Profile
from explore.models import Gym
from .models import AdminAction, LoginLog

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio', 'age', 'gender', 'height', 'weight', 'goal', 'fitness_level']

class AdminUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'last_login', 'profile']

from explore.serializers import GymImageSerializer

class AdminGymSerializer(serializers.ModelSerializer):
    images = GymImageSerializer(many=True, read_only=True)
    class Meta:
        model = Gym
        fields = '__all__'

class AdminActionSerializer(serializers.ModelSerializer):
    admin_username = serializers.ReadOnlyField(source='admin.username')
    class Meta:
        model = AdminAction
        fields = '__all__'

class LoginLogSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    ip_address = serializers.CharField(read_only=True)
    class Meta:
        model = LoginLog
        fields = ['id', 'username', 'ip_address', 'user_agent', 'timestamp']
