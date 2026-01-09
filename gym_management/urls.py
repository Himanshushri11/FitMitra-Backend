from django.urls import path
from .views import (
    GymOwnerDashboardOverview, 
    MemberListView, 
    CreateRazorpayOrder, 
    VerifyPayment
)

urlpatterns = [
    path('dashboard/overview/', GymOwnerDashboardOverview.as_view(), name='gym_dashboard_overview'),
    path('members/', MemberListView.as_view(), name='gym_members'),
    path('payment/create-order/', CreateRazorpayOrder.as_view(), name='razorpay_create_order'),
    path('payment/verify/', VerifyPayment.as_view(), name='razorpay_verify_payment'),
]
