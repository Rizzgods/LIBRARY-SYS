# admin.py

from django.contrib import admin
from .models import  UserActivity

class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'logout_time']

admin.site.register(UserActivity, UserActivityAdmin)


