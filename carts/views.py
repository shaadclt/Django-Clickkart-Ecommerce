from django.shortcuts import get_object_or_404, render,redirect
from store.models import Product, Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from accounts.models import Address
from django.views.decorators.cache import never_cache
from coupon.models import Coupon, ReviewCoupon
from datetime import date
from django.http import JsonResponse
from django.contrib import messages


def _cart_id(request): #Private function 
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request,product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) # Getting the product
    # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product = product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,user = current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # Increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
                item.save()

            else:
                # Create a new cart item
                item = CartItem.objects.create(product = product, quantity = 1,user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    # If the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product = product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        
        
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request)) # Getting the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,cart = cart)
            # existing variations -- database
            # current variations -- product variation list
            # item id -- database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # Increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
                item.save()

            else:
                # Create a new cart item
                item = CartItem.objects.create(product = product, quantity = 1,cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')


def remove_cart(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request,total =0,quantity=0,cart_items=None):
    try:
        GST = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        GST = (12 * total)/100
        grand_total = total + GST
    except ObjectDoesNotExist:
        pass 

    context = {
        'total':total,
        'quantity': quantity,
        'cart_items': cart_items,
        'GST':GST,
        'grand_total':grand_total,
    }

    return render(request,'store/cart.html',context)


@login_required(login_url='signin')
def checkout(request,total =0,quantity=0,cart_items=None):
    if "discount_price" in request.session:
        del request.session["discount_price"]
    try:
        GST = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        GST = (12 * total)/100
        grand_total = total + GST
        if "discount_price" in request.session:
            grand_total = request.session["discount_price"]
    except ObjectDoesNotExist:
        pass 
    
    
    addresses = Address.objects.filter(user=request.user)
    context = {
        'total':total,
        'quantity': quantity,
        'cart_items': cart_items,
        'GST':GST,
        'grand_total':grand_total,
        "addresses": addresses,
    }
    return render(request,'store/checkout.html',context)


@never_cache
@login_required(login_url="userlogin")
def Check_coupon(request):

    if "coupon_code" in request.session:
        del request.session["coupon_code"]
        del request.session["amount_pay"]
        
    flag = 0
    discount_price = 0
    amount_pay = 0
    coupon_code = request.POST.get("coupon_code")
    grand_total = float(request.POST.get("grand_total"))

    if Coupon.objects.filter(code=coupon_code, coupon_limit__gte=1).exists():
        coupon = Coupon.objects.get(code=coupon_code)
        
        
        if coupon.active == True:
            flag = 1
            if not ReviewCoupon.objects.filter(user=request.user, coupon=coupon):
                today = date.today()

                if coupon.valid_from <= today and coupon.valid_to >= today:
                    discount_price = grand_total - coupon.discount

                    amount_pay = grand_total - discount_price
                    flag = 2
                    request.session["amount_pay"] = amount_pay
                    request.session["coupon_code"] = coupon_code
                    request.session["discount_price"] = discount_price

                    # Reduce Coupon Limit
                    coupon.coupon_limit = coupon.coupon_limit - 1
                    coupon.save()

                    # Move to ReviewCoupon if all coupons are used
                    if coupon.coupon_limit == 0:
                        reviewcoupon = ReviewCoupon()
                        reviewcoupon.user = request.user
                        reviewcoupon.coupon = coupon
                        reviewcoupon.save()
                    
                    


    context = {
        "amount_pay": amount_pay,
        "flag": flag,
        "discount_price": discount_price,
        "coupon_code": coupon_code,
    }

    return JsonResponse(context)