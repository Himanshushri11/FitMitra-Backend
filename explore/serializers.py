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

from .models import Trainer, Event, Challenge, Article, UserEvent, UserChallenge

class TrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    trainer = TrainerSerializer(read_only=True)
    is_joined = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'banner', 'start_time', 'end_time', 
            'trainer', 'status', 'participants_count', 'is_joined'
        ]

    def get_is_joined(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserEvent.objects.filter(user=request.user, event=obj).exists()
        return False

class ChallengeSerializer(serializers.ModelSerializer):
    is_joined = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'banner', 'duration_days', 
            'difficulty', 'start_date', 'is_joined'
        ]

    def get_is_joined(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserChallenge.objects.filter(user=request.user, challenge=obj).exists()
        return False

class ArticleSerializer(serializers.ModelSerializer):
    author = TrainerSerializer(read_only=True)
    
    class Meta:
        model = Article
        fields = '__all__'
