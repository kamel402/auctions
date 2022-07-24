from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'description', 'price', 'category', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title', 'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'placeholder': 'Description','class': 'form-control', 'required': True}),
            'price': forms.NumberInput(attrs={'placeholder': 'Starting Price', 'class': 'form-control', 'required': True}),
            'category': forms.Select(attrs={'placeholder': 'Category' ,'class': 'form-control'}),
            'image': forms.URLInput(attrs={'placeholder': 'Image URL', 'class': 'form-control'})
        }