import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import GymOwnerProfile, Member
from .serializers import GymOwnerProfileSerializer, MemberSerializer
from django.utils import timezone
from dotenv import load_dotenv
load_dotenv()
# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class GymOwnerDashboardOverview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.gym_profile
        except GymOwnerProfile.DoesNotExist:
            return Response({"error": "Gym Owner Profile not found"}, status=404)

        members_count = profile.members.count()
        paid_members = profile.members.filter(fees_status='PAID').count()
        pending_members = members_count - paid_members

        return Response({
            "gym_name": profile.gym_name,
            "payment_status": profile.payment_status,
            "plan_type": profile.plan_type,
            "stats": {
                "total_members": members_count,
                "paid_members": paid_members,
                "pending_members": pending_members
            }
        })

class MemberListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.gym_profile
        except GymOwnerProfile.DoesNotExist:
            return Response({"error": "Gym Owner Profile not found"}, status=404)
        
        members = profile.members.all().order_by('-join_date')
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            profile = request.user.gym_profile
        except GymOwnerProfile.DoesNotExist:
            return Response({"error": "Gym Owner Profile not found"}, status=404)

        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(gym_owner=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.parsers import JSONParser

def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class CreateRazorpayOrder(APIView):
    """
    Creates a Razorpay order for Gym Owner premium activation.
    Amount should be in paise (e.g., 29900 for ₹299.00)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        # 1. Role validation
        try:
            profile = request.user.profile
            role = profile.role
        except Exception:
            role = 'USER'
        
        if role != 'GYM_OWNER':
            return Response({
                "error": "Access Denied",
                "message": "Only gym owners can activate premium plans."
            }, status=status.HTTP_403_FORBIDDEN)

        # 2. Get and validate amount
        amount = request.data.get('amount')
        if not amount:
            return Response({
                "error": "Missing Amount",
                "message": "Please specify the upgrade amount."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. Credentials Validation
            key_id = getattr(settings, 'RAZORPAY_KEY_ID', None)
            key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
            
            if not key_id or not key_secret or 'YourKeyHere' in key_id:
                print("CRITICAL: Razorpay keys are missing or using placeholders!")
                return Response({
                    "error": "Service Unavailable",
                    "message": "Payment gateway is not configured. Please contact support."
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # 4. Create Client & Order
            client = razorpay.Client(auth=(key_id, key_secret))
            
            gym_profile = getattr(request.user, 'gym_profile', None)
            gym_name = gym_profile.gym_name if gym_profile else "FitMitra Gym"
            
            order_data = {
                "amount": int(amount),
                "currency": "INR",
                "payment_capture": 1,
                "notes": {
                    "user_id": request.user.id,
                    "email": request.user.email,
                    "gym_name": gym_name,
                    "type": "membership_upgrade",
                    "plan": request.data.get('plan', 'STARTER') # Default to STARTER if not passed
                }
            }
            
            print(f"INFO: Creating Razorpay order for User {request.user.id}")
            order = client.order.create(order_data)
            
            return Response(order, status=status.HTTP_200_OK)
            
        except razorpay.errors.BadRequestError as e:
            print(f"RAZORPAY BAD REQUEST: {str(e)}")
            return Response({
                "error": "Gateway Error",
                "message": "Razorpay rejected the request. Please check the amount format."
            }, status=status.HTTP_400_BAD_REQUEST)
        except razorpay.errors.SignatureVerificationError:
             return Response({
                "error": "Security Error",
                "message": "Payment signature verification failed."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"CRITICAL RAZORPAY ERROR: {str(e)}")
            return Response({
                "error": "Internal Error",
                "message": "An unexpected error occurred while preparing your payment."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        client = get_razorpay_client()
        params_dict = {
            'razorpay_order_id': request.data.get('razorpay_order_id'),
            'razorpay_payment_id': request.data.get('razorpay_payment_id'),
            'razorpay_signature': request.data.get('razorpay_signature')
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            
            # Payment successful, update profile
            profile = request.user.gym_profile
            
            # Fetch order details to know which plan was bought
            order_id = request.data.get('razorpay_order_id')
            order = client.order.fetch(order_id)
            plan_bought = order.get('notes', {}).get('plan', 'STARTER')
            
            profile.payment_status = True
            profile.plan_type = plan_bought
            profile.save()
            
            return Response({"message": "Payment successful and verified"})
        except Exception as e:
            return Response({"error": "Payment verification failed"}, status=400)
