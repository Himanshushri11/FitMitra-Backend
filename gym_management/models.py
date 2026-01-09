from django.db import models
from django.contrib.auth.models import User

class GymOwnerProfile(models.Model):
    PLAN_CHOICES = (
        ('FREE', 'Free'),
        ('STARTER', 'Starter'),
        ('PRO', 'Pro'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gym_profile')
    gym_name = models.CharField(max_length=255)
    payment_status = models.BooleanField(default=False) # Deprecated, use plan_type
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='FREE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gym_name} ({self.user.username}) - {self.plan_type}"

class Member(models.Model):
    FEES_STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
    )

    gym_owner = models.ForeignKey(GymOwnerProfile, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    join_date = models.DateField()
    fees_status = models.CharField(max_length=10, choices=FEES_STATUS_CHOICES, default='PENDING')
    fees_due_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.gym_owner.gym_name}"
