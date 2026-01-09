from django.http import JsonResponse
from django.urls import resolve

class GymOwnerPaymentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                role = request.user.profile.role
            except:
                role = 'USER'

            if role == 'GYM_OWNER':
                # Check payment status
                payment_status = False
                try:
                    payment_status = request.user.gym_profile.payment_status
                except:
                    pass

                if not payment_status:
                    # List of paths that are NOT locked for unpaid gym owners
                    # Dashboard (overview), profile, and payment related urls should be allowed.
                    allowed_paths = [
                        '/api/accounts/profile/',
                        '/api/gym/payment/',
                        '/api/gym/dashboard/overview/', # Maybe allow overview but with limited data
                    ]
                    
                    current_path = request.path
                    
                    # Lock functional features
                    locked_keywords = [
                        '/api/fitness/', 
                        '/api/ai/posture/', 
                        '/api/diet/', # if exists
                        '/api/gym/members/',
                        '/api/gym/candidates/',
                        '/api/gym/fees/',
                    ]

                    for kw in locked_keywords:
                        if current_path.startswith(kw):
                            return JsonResponse({
                                "error": "Payment Required",
                                "message": "Please upgrade to premium to access this feature.",
                                "payment_required": True
                            }, status=403)

        response = self.get_response(request)
        return response
