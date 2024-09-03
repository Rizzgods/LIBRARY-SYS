from django import forms
from .models import Books


class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['BookTitle', 'Author', 'Date', 'Language','Category','SubCategory', 'SubSection','BookFile', 'BookImage', 'Description', 'eBook','research_paper', 'hardCopy', 'stock'] 
