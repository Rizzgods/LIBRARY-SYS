# custom_tags.py

from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='is_librarian')
def is_librarian(user):
    return user.groups.filter(name='Librarian').exists()


