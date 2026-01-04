from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ContactMessageSerializer
from .models import ContactMessage
import logging

logger = logging.getLogger(__name__)

class ContactUsView(APIView):
    authentication_classes = []  # Allow public access
    permission_classes = []

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            # 1. Save to Database
            contact_msg = serializer.save()

            # 2. Prepare Email Content
            admin_email = "fitmitra11@gmail.com"
            subject = f"New Contact Message: {contact_msg.subject or 'No Subject'}"
            message_body = f"""
            You have received a new message from the FitMitra Contact Form:

            --------------------------------------------------
            Sender Name: {contact_msg.name}
            Sender Email: {contact_msg.email}
            Timestamp: {contact_msg.created_at}
            --------------------------------------------------

            Message:
            {contact_msg.message}

            --------------------------------------------------
            Reply directly to this email to contact the user.
            """

            try:
                # 3. Send Email to Admin
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )

                # 4. Optional: Auto-reply to User
                auto_reply_subject = "We received your message - FitMitra"
                auto_reply_body = f"""
                Hi {contact_msg.name},

                Thank you for reaching out to FitMitra! We have received your message and our team will get back to you as soon as possible.

                Your message:
                "{contact_msg.message}"

                Stay Fit,
                Team FitMitra
                """
                send_mail(
                    subject=auto_reply_subject,
                    message=auto_reply_body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[contact_msg.email],
                    fail_silently=True,
                )

                return Response({"success": "Your message has been sent successfully!"}, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"SMTP Error: {str(e)}")
                # Even if email fails, the message is saved in DB
                return Response({
                    "success": "Message saved, but email notification failed. We will still see your message in our records."
                }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
