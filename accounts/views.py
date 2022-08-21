
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from . models import Account, UserProfile
from . forms import RegistrationForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderProduct


#Wishlist
from store.models import Product

# User Verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Cart
from carts.models import Cart, CartItem
from carts.views import _cart_id

import requests

# Razorpay
import razorpay
from django.conf import settings
from orders.models import Payment

# Address Management
from .models import Address
from .forms import AddressForm

# Twilio
from accounts.otp import sentOTP, checkOTP

import datetime


# User Registration
def usersignup(request):
    global phone_number
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            # user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            # user.phone_number = phone_number
            # user.save()

            # Create User Profile
            # profile = UserProfile()
            # profile.user_id = user.id
            # profile.profile_picture = 'default/default-user.png'
            # profile.save()

            # User Activation
            # current_site = get_current_site(request)
            # mail_subject = "Please activate your account"
            # message = render_to_string('accounts/account_verification_email.html',{
            #     'user':user,
            #     'domain':current_site,
            #     'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token':default_token_generator.make_token(user),
            # })
            # to_email = email
            # send_email = EmailMessage(mail_subject,message,to=[to_email])
            # send_email.send()

            # return redirect('/accounts/signin/?command=verification&email='+email)
            request.session["first_name"] = first_name
            request.session["last_name"] = last_name
            request.session["email"] = email
            request.session['checkmobile'] = phone_number
            request.session['password'] = password
            request.session['username'] = username
            sentOTP(phone_number)
            return redirect('confirm_signup')
    else:
        form = RegistrationForm()

    context = {
        'form':form
    }
    return render(request,'accounts/register.html',context)


def confirm_signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        otp = request.POST["otpcode"]
        phone_number = request.session["checkmobile"]
        if checkOTP(phone_number, otp):
            first_name = request.session["first_name"]
            last_name = request.session["last_name"]
            email = request.session["email"]
            phone_number = request.session["checkmobile"]
            password = request.session["password"]
            username = request.session["username"]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                username=username,
            )
            user.phone_number = phone_number
            # Create a user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = "static/default.png"
            profile.save()
            user.is_active = True
            user.save()
            
            messages.success(request, "Registered successfully")
            return redirect("usersignin")
        else:
            print("OTP not matching")
            return redirect("confirm_signup")
    return render(request, "accounts/confirm_signup.html")


# User Signin
def usersignin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # getting product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # get the cart items from the user to access his product variation
                    cart_item = CartItem.objects.filter(user = user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            login(request,user)
            messages.success(request,"You have successfully logged in!!!")
            url = request.META.get('HTTP_REFERER') # grabs previous url
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('home') 
        else:
            messages.error(request,"Wrong login credentials!!!")
            return redirect('usersignin')
    return render(request,'accounts/signin.html')


# User Signout
@login_required(login_url='usersignin')
def usersignout(request):
    logout(request)
    messages.success(request,"You have successfully logged out")
    return redirect('usersignin')


# User Activation 
# def activate(request,uidb64,token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = Account._default_manager.get(pk=uid)
#     except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
#         user = None
    
#     if user is not None and default_token_generator.check_token(user,token):
#         user.is_active = True
#         user.save()
#         messages.success(request,'Congratulations! Your Account is activated.')
#         return redirect('usersignin')
#     else:
#         messages.error(request,'Invalid Activation Link')
#         return redirect('usersignin')

def signinotp(request):
    if request.method == "POST":
        mobile = request.POST["phone"]
        try:
            if Account.objects.get(phone_number=mobile):
                sentOTP(mobile)
                request.session["checkmobile"] = mobile
                return redirect("otpcheck")
        except:
            messages.info(request, "User not registered")
            return redirect("signinotp")
    return render(request, "accounts/signinotp.html")


def otpcheck(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        otp = request.POST["otpcode"]
        mobile = request.session["checkmobile"]
        a = checkOTP(mobile, otp)
        if a:
            user = Account.objects.get(phone_number=mobile)
            login(request, user)
            messages.success(request, "Autheticated Successfully")
            return redirect("home")

        else:
            messages.info(request, "OTP not Valid")
            return redirect("otpcheck")

    return render(request, "accounts/otpcheck.html")


def resend_otp(request):
    mobile = request.session["checkmobile"]
    sentOTP(mobile)
    return redirect("otpcheck")


# User Dashboard
@login_required(login_url='usersignin')
def userdashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/userdashboard.html', context)


# Forgot Password
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset Password Email
            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,"Password reset email has been sent to your email address.")
            return redirect('usersignin')
        else:
            messages.error(request,"Account does not exist")
            return redirect('forgotPassword')

    return render(request,'accounts/forgotPassword.html')


# Reset Password Validation
def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password.')
        return redirect('resetPassword')
    else:
        messages.error(request,"This link has expired.")
        return redirect('usersignin')


# Reset Password
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user.password = Account.objects.get(password)
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password is set successfully")
            return redirect('usersignin')
        else:
            messages.error(request,"Passwords do not match")
            return redirect('resetPassword')
    else:
        return render(request,'accounts/resetPassword.html')


@login_required(login_url="usersignin")
def my_orders(request):
    orderproducts = OrderProduct.objects.filter(
        user=request.user,ordered=True).order_by("-created_at")
    orders = Order.objects.filter(
        user=request.user,is_ordered=True).order_by("-created_at")

    context = {"orders": orders,"orderproducts":orderproducts}
    return render(request, "accounts/my_orders.html", context)


# User Dashboard - My Orders
@login_required(login_url="usersignin")
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(
        order__order_number=order_id
    )  # with the '__' we can access foreign key objects
    order = Order.objects.get(order_number=order_id)
    subtotal = 0

    for i in order_detail:
        subtotal = subtotal + i.product_price * i.quantity

    

    context = {
        "order_detail": order_detail,
        "order": order,
        "subtotal": subtotal,
        
    }

    return render(request, "accounts/order_detail.html", context)


def cancel_order(request,pk):
    product = OrderProduct.objects.get(pk=pk)
    
    messages.success(request,"Order has been cancelled and refund initiated")
    
    payment_id = product.payment.id

    order = Order.objects.get(user=request.user,payment_id=payment_id)

    payment = product.payment


    if str(payment).__contains__("pay"):
        
        paymentId = payment
        amount = int(product.order_total)
        refund_amount = int(amount*100)
        
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        
        client.payment.refund(paymentId,{
            "amount": refund_amount,
            "speed": "optimum",
        })
        product = OrderProduct.objects.get(pk=pk)
        product.status = 'Cancelled'
        product.order_total = 0
        product.save()
    
        item = Product.objects.get(pk=product.product.id)
        item.stock += product.quantity
        item.save()

    else:
        product = OrderProduct.objects.get(pk=pk)
        product.status = 'Cancelled'
        product.order_total = 0
        product.save()
    
        item = Product.objects.get(pk=product.product.id)
        item.stock += product.quantity
        item.save()

    
    mail_subject = 'Order Cancellation'
    message = render_to_string('orders/order_cancelled_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    return redirect('my_orders')
    

# User Dashboard - Edit Profile
@login_required(login_url='signin')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your profile has been updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }
    return render(request,'accounts/edit_profile.html',context)


# User Dashboard - Change Password
@login_required(login_url='signin')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request,"Please enter correct current password")
                return redirect('change_password')
        else:
            messages.error(request,"Passwords does not match")
            return redirect('change_password')

    return render(request,'accounts/change_password.html')


#Wishlist - add to wishlist
login_required(login_url='signin')
def add_to_wishlist(request,id):
    product = get_object_or_404(Product,id=id)
    if product.user_wishlist.filter(id=request.user.id).exists():
        messages.error(request,"Product already in wishlist")
    else:
        product.user_wishlist.add(request.user)
        messages.success(request,"Successfully added to wishlist")
    return redirect('wishlist')


#Wishlist - delete from wishlist
def delete_wishlist(request,id):
    product = get_object_or_404(Product,id=id)
    product.user_wishlist.remove(request.user)
    messages.success(request,"Removed from wishlist")
    return redirect('wishlist')


#Wishlist
def wishlist(request):
    products = Product.objects.filter(user_wishlist=request.user)
    context = {
        'products': products
    }
    return render(request,'accounts/wishlist.html',context)


# Address Management
@login_required(login_url="userlogin")
def add_address(request):
    form = AddressForm()
    addresses = Address.objects.filter(user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.success(request, "New Address added successfully")
            return redirect("add_address")

    context = {"form": form, "addresses": addresses}
    return render(request, "accounts/add_address.html", context)


@login_required
def edit_address(request, pk):
    address = Address.objects.get(pk=pk)
    form = AddressForm(instance=address)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)

        if form.is_valid():
            form.save()
            messages.success(request, "Your address has been updated")
            return redirect("add_address")

    context = {"form": form}
    return render(request, "accounts/edit_address.html", context)


@login_required
def delete_address(request, pk):
    dlt = Address.objects.filter(id=pk)
    print(dlt)
    dlt.delete()
    messages.success(request, "Your Address has been deleted")
    return redirect("add_address")


@login_required
def set_default_address(request, pk):
    Address.objects.filter(user=request.user, default=True).update(
        default=False
    )
    address = Address.objects.get(pk=pk)
    address.default = True
    address.save()
    messages.success(request, "Default address changed")
    return redirect("add_address")
