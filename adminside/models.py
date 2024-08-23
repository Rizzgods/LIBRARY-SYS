from django.db import models

# models.py

from django.db import models
from django.contrib.auth.models import User



class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False)

