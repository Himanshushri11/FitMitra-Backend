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
            "workouts_completed", "calories_burned", "current_streak", "achievements_count",
            "role"
        ]
        read_only_fields = ['id', 'username', 'email', 'profile_pic', 'workouts_completed', 'calories_burned', 'current_streak', 'achievements_count', 'role']

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
    gym_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser', 'profile', 'gym_profile']

    def get_gym_profile(self, obj):
        try:
            from gym_management.models import GymOwnerProfile
            profile = GymOwnerProfile.objects.get(user=obj)
            return {
                "gym_name": profile.gym_name,
                "payment_status": profile.payment_status
            }
        except:
            return None
class GymOwnerRegisterSerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "gym_name"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        gym_name = validated_data.pop("gym_name")
        
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        from .models import Profile
        from gym_management.models import GymOwnerProfile

        # Update Profile Role
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = 'GYM_OWNER'
        profile.save()

        # Create GymOwnerProfile
        GymOwnerProfile.objects.create(
            user=user,
            gym_name=gym_name
        )

        return user

