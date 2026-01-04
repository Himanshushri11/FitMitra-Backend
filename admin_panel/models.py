from django.db import models
from django.contrib.auth.models import User

class AdminAction(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50) # CREATE, UPDATE, DELETE, BLOCK, UNBLOCK
    target_model = models.CharField(max_length=50) # USER, GYM
    target_id = models.CharField(max_length=50)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} - {self.action_type} on {self.target_model} ({self.target_id})"

class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} logged in at {self.timestamp}"
