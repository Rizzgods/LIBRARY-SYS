from django import forms
from .models import Books
import json

class BookForm(forms.ModelForm):
    authors = forms.CharField(widget=forms.HiddenInput(), required=False)
    Author = forms.CharField(required=False)

    class Meta:
        model = Books
        fields = ['BookTitle', 'Author', 'Date', 'Language', 'Category', 'SubCategory', 'SubSection', 'BookFile', 'BookImage', 'Description', 'eBook', 'research_paper', 'hardCopy', 'stock']

def clean(self):
    cleaned_data = super().clean()
    authors_json = cleaned_data.get('authors')
    
    if authors_json:
        try:
            authors_list = json.loads(authors_json)
            if authors_list:
                cleaned_data['Author'] = ', '.join(authors_list)
            else:
                # If authors_list is empty, check if there's an existing Author value
                if not cleaned_data.get('Author'):
                    raise forms.ValidationError("At least one author is required.")
        except json.JSONDecodeError:
            # If JSON decoding fails, check if there's an existing Author value
            if not cleaned_data.get('Author'):
                raise forms.ValidationError("Invalid author data format.")
    elif not cleaned_data.get('Author'):
        raise forms.ValidationError("At least one author is required.")
    
    return cleaned_data