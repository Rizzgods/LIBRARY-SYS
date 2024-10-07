# custom_tags.py

from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='is_schoolAdmin')
def user_is_schoolAdmin(user):
    return user.groups.filter(name='SchoolAdmin').exists()



