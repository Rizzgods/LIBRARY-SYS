# custom_tags.py

from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='is_student')
def is_student(user):
    return user.groups.filter(name='Student').exists()


@register.filter(name='is_Librarian')
def is_student(user):
    return user.groups.filter(name='Librarian').exists()

