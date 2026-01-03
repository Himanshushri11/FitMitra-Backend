from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import send_contact_email


class ContactView(APIView):
    def post(self, request):
        send_contact_email(
            request.data["subject"],
            request.data["message"],
            request.data["email"]
        )
        return Response({"message": "Mail sent"})
