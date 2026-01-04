from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Value, FloatField
from .models import Gym
from .serializers import GymSerializer

class GymViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing gym details and listing/filtering gyms.
    """
    queryset = Gym.objects.filter(is_active=True)
    serializer_class = GymSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'city', 'address']
    ordering_fields = ['rating', 'price_range_min', 'distance']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        city = self.request.query_params.get('city')

        if city:
            queryset = queryset.filter(city__icontains=city)

        # In a real-world scenario with PostGIS:
        # from django.contrib.gis.db.models.functions import Distance
        # from django.contrib.gis.geos import Point
        # if lat and lng:
        #     user_location = Point(float(lng), float(lat), srid=4326)
        #     queryset = queryset.annotate(distance=Distance('location', user_location)).order_by('distance')

        # For this implementation, we annotate a default distance.
        # Sorting by distance can be handled in frontend for smaller datasets
        # or via custom SQL expressions if PostGIS isn't available.
        queryset = queryset.annotate(distance=Value(0.0, output_field=FloatField()))
        
        return queryset

    @action(detail=False, methods=['post'], permission_classes=[])
    def seed_data(self, request):
        """Seed initial gym data for testing."""
        sample_gyms = [
            {
                "name": "PowerHouse Gym",
                "address": "123 Fitness Ave, Mumbai",
                "city": "Mumbai",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "rating": 4.5,
                "price_range_min": 1200,
                "price_range_max": 2500,
                "facilities": ["Cardio", "Weights", "Yoga", "Steam Room"]
            },
            {
                "name": "The Iron Room",
                "address": "45 Strength St, Delhi",
                "city": "Delhi",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "rating": 4.8,
                "price_range_min": 1500,
                "price_range_max": 3000,
                "facilities": ["Heavy Lifting", "Personal Training", "Protein Bar"]
            },
            {
                "name": "FitLife Studio",
                "address": "78 Wellness Rd, Bangalore",
                "city": "Bangalore",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "rating": 4.2,
                "price_range_min": 999,
                "price_range_max": 1999,
                "facilities": ["Zumba", "Pilates", "Shower"]
            },
            {
                "name": "Evolution Fitness",
                "address": "10 Crossfit Lane, Mumbai",
                "city": "Mumbai",
                "latitude": 19.0800,
                "longitude": 72.8800,
                "rating": 4.7,
                "price_range_min": 2000,
                "price_range_max": 5000,
                "facilities": ["Crossfit", "Swimming Pool", "Parking"]
            },
            {
                "name": "Zen Yoga & Gym",
                "address": "22 Tranquil Path, Pune",
                "city": "Pune",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "rating": 4.4,
                "price_range_min": 899,
                "price_range_max": 1500,
                "facilities": ["Yoga", "Meditation", "Cafe"]
            }
        ]
        
        created_count = 0
        for data in sample_gyms:
            gym, created = Gym.objects.get_or_create(name=data['name'], defaults=data)
            if created:
                created_count += 1
        
        return Response({"message": f"Successfully seeded {created_count} gyms."}, status=status.HTTP_201_CREATED)
