from django import forms
from django.db import models
from django.db.models import fields
from django.forms.fields import FileField
from django.forms.widgets import CheckboxInput, FileInput, TextInput
# from coupon.models import Coupon
# from offer.models import BrandOffer, CategoryOffer, ProductOffer
from category.models import Category

from store.models import Product, Variation
from coupon.models import Coupon
# from brands.models import Brand


class EditProduct(forms.ModelForm):
    product_name = forms.CharField(
        required=True,
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control"}),)

    description = forms.CharField(
        required=True,
        max_length=500,
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )
    price = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    # images = forms.ImageField(required=True,widget=FileInput)
    stock = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    is_available = forms.BooleanField(
        required=True, widget=CheckboxInput(attrs={"placeholder": "Status"})
    )


    class Meta:
        model = Product
        fields = [
            "product_name",
            "description",
            "price",
            "image",
            "stock",
            "is_available",
            "category",
        ]

    def _init_(self, *args, **kwargs):
        super(EditProduct, self)._init_(
            *args, **kwargs
        )  # images = forms.ImageField(required=True,widget=FileInput)


class EditVariation(forms.ModelForm):
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

       
class EditCategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["category_name", "slug"]
        widgets = {
            'category_name':forms.TextInput(attrs={'class':'form-control'}),
            'slug':forms.TextInput(attrs={'class':'form-control'}),
        }

class EditCoupon(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            "coupon_name",
            "code",
            "coupon_limit",
            "valid_from",
            "valid_to",
            "discount",
        ]
        widgets = {
            'coupon_name':forms.TextInput(attrs={'class':'form-control'}),
            'code':forms.TextInput(attrs={'class':'form-control'}),
            'coupon_limit':forms.NumberInput(attrs={'class':'form-control'}),
            'valid_from':forms.DateInput(attrs={'class':'form-control'}),
            'valid_to':forms.DateInput(attrs={'class':'form-control'}),
            'discount':forms.NumberInput(attrs={'class':'form-control'}),
        }



















# class EditBrand(forms.ModelForm):
#     class Meta:
#         model = Brand
#         fields = ["brand_name", "slug", "logo", "description"]







# class EditBrandOffer(forms.ModelForm):
#     class Meta:
#         model = BrandOffer
#         fields = ["brand_name", "discount"]


# class EditCategoryOffer(forms.ModelForm):
#     class Meta:
#         model = CategoryOffer
#         fields = ["category_name", "discount"]


# class EditProductOffer(forms.ModelForm):
#     class Meta:
#         model = ProductOffer
#         fields = ["product_name", "discount"]


# class EditBanner(forms.ModelForm):
#     class Meta:
#         model = Banners
#         fields = ["image", "product", "alt_text"]



