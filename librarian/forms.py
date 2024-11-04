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
        
        try:
            if authors_json:
                authors_list = json.loads(authors_json)
                if not authors_list:
                    raise forms.ValidationError("At least one author is required.")
                # Join authors with commas for storage in the Author field
                cleaned_data['Author'] = ', '.join(authors_list)
            else:
                raise forms.ValidationError("At least one author is required.")
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid author data format.")
        
        return cleaned_data