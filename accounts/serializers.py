from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            "id", "username", "email", "profile_pic", "bio", 
            "age", "gender", "height", "weight", 
            "goal", "fitness_level", 
            "workouts_completed", "calories_burned", "current_streak"
        ]
        read_only_fields = ['username', 'email', 'workouts_completed', 'calories_burned', 'current_streak']

class RegisterSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(required=False)
    gender = serializers.CharField(required=False)
    goal = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "age", "gender", "goal"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        age = validated_data.pop("age", None)
        gender = validated_data.pop("gender", None)
        goal = validated_data.pop("goal", "")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        Profile.objects.create(
            user=user,
            age=age,
            gender=gender,
            goal=goal
        )

        return user

class UserSerializer(serializers.ModelSerializer):
    # Simplified User serializer that includes profile info
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser', 'profile']