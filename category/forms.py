from django.db.models import fields
from django import forms
from django.forms import ModelForm
from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["category_name", "slug"]
        widgets = {
            'category_name':forms.TextInput(attrs={'class':'form-control'}),
            'slug':forms.TextInput(attrs={'class':'form-control',}),
        }
