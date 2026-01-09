from rest_framework import serializers
from .models import GymOwnerProfile, Member

class GymOwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymOwnerProfile
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['gym_owner']
