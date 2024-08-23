from django import forms
from userauth.models import Account, Librarian


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['lrn', 'fname', 'lname', 'address','birthday','age', 'email',] 

class LibrarianForm(forms.ModelForm):
    class Meta:
        model = Librarian
        fields = ['Username', 'fname', 'lname', 'email', 'Bday']
