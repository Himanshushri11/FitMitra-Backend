from django.core.mail import send_mail

def send_contact_email(subject, message, email):
    send_mail(
        subject,
        message,
        email,
        ["admin@fitmitra.com"],
        fail_silently=False
    )
