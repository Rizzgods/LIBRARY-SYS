from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('reminder', 'Reminder'),
        # Add more types if necessary
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'  # Unique related name
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES, null=False, blank=False)

    def __str__(self):
        return self.message