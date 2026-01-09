from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics, parsers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile
from .serializers import RegisterSerializer, ProfileSerializer, UserSerializer, GymOwnerRegisterSerializer

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Signup successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        }, status=201)

class GymOwnerSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GymOwnerRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Gym Owner Signup successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        }, status=201)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username_or_email = request.data.get("username")
        password = request.data.get("password")

        # Authenticate by username or email
        if '@' in username_or_email:
             # Try to find user by email
             try:
                 user_obj = User.objects.get(email=username_or_email)
                 username = user_obj.username
             except User.DoesNotExist:
                 # If email not found, keep as is, authenticate will fail gracefully
                 username = username_or_email
        else:
             username = username_or_email

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        # Record login log
        from admin_panel.models import LoginLog
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        LoginLog.objects.create(
            user=user,
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        })

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    GET: Retrieve current user's profile
    PUT/PATCH: Update current user's profile
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        # Ensure profile exists
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

class ProfilePictureUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        profile = request.user.profile
        if 'profile_pic' not in request.data:
            return Response({"error": "No image provided"}, status=400)
        
        profile.profile_pic = request.data['profile_pic']
        profile.save()
        return Response(ProfileSerializer(profile, context={"request": request}).data, status=200)
