from django import forms
from .models import ReviewRating, Product, Variation, ProductGallery
from django.forms.widgets import TextInput

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject','review','rating']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_name",
            "image",
            "description",
            "price",
            "category",
            "stock",
        ]
        widgets = {
            'product_name':forms.TextInput(attrs={'class':'form-control'}),
            'slug':forms.TextInput(attrs={'class':'form-control'}),
            'description':forms.TextInput(attrs={'class':'form-control'}),
            'price':forms.TextInput(attrs={'class':'form-control'}),
            'category':forms.Select(attrs={'class':'form-control'}),
            'stock':forms.TextInput(attrs={'class':'form-control'}),
        }


class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = [
            "product",
            "variation_category",
            "variation_value",
            "is_active",
        ]
        widgets = {
            'product':forms.Select(attrs={'class':'form-control'}),
            'variation_category':forms.Select(attrs={'class':'form-control'}),
            'variation_value':forms.TextInput(attrs={'class':'form-control'}),
        }


class ProductGalleryForm(forms.ModelForm):
    class Meta:
        model = ProductGallery
        fields = [
            "product",
            "image",
        ]
        widgets = {
            'product':forms.Select(attrs={'class':'form-control'}),
        }

