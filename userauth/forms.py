from django import forms
from django.contrib.auth.models import User
from .models import AccountRequest

class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(label="Enter your email")

class AccountCreationForm(forms.ModelForm):
    class Meta:
        model = AccountRequest
        fields = ['lrn', 'fname', 'lname', 'address', 'birthday', 'age', 'email']