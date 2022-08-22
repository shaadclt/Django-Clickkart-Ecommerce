from django.shortcuts import render
from store.models import Product,ReviewRating

def home(request):
    products = Product.objects.all().filter(is_popular=True).order_by('created_date')
    for product in products:
        

    context = {
        'products':products,

    }
    return render(request,'home.html',context)