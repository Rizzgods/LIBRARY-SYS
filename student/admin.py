from django.contrib import admin

from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created_at', 'notification_type', 'read']
    list_filter = ['notification_type', 'read']
    search_fields = ['user__username', 'message']

admin.site.register(Notification, NotificationAdmin)