from rest_framework import serializers
from .models import Gym, GymReview, GymImage

class GymImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymImage
        fields = ['id', 'image', 'created_at']

class GymReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymReview
        fields = '__all__'

class GymSerializer(serializers.ModelSerializer):
    reviews_count = serializers.IntegerField(source='reviews.count', read_only=True)
    distance = serializers.FloatField(read_only=True, required=False) # Annotated in view
    images = GymImageSerializer(many=True, read_only=True)

    class Meta:
        model = Gym
        fields = [
            'id', 'name', 'description', 'address', 'city', 
            'latitude', 'longitude', 'rating', 'price_range_min', 
            'price_range_max', 'thumbnail', 'images', 'facilities', 
            'contact_number', 'reviews_count', 'distance'
        ]
