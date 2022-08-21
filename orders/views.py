from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
import datetime
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from store.models import Product
from django.contrib import messages
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


# Authorize razorpay client with API keys
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def place_order(request,total =0,quantity=0):
    current_user = request.user

    #if cart count is less than or equal to 0, then redirect back to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    GST = 0
    amount_pay = 0
    discount = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    GST = (12 * total)/100
    grand_total = total + GST
    if "discount_price" in request.session:
        grand_total = request.session["discount_price"]
    if "amount_pay" in request.session:
        amount_pay = request.session["amount_pay"]

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all the billing information inside order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.GST = GST
            data.save()

            # Generate Order Number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d')
            

            payment_type  = request.POST["payment"]
            currency = 'INR'
            amount = grand_total * 100
            request.session["razorpay_amount"] = amount
            razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            razorpay_order = razorpay_client.order.create(
                dict(amount=amount, currency=currency, payment_capture="0")
            )

            if payment_type == "Razorpay":
                order_number = razorpay_order['id']
                data.order_number = razorpay_order['id']
                data.save()
            else:
                order_number = current_date + str(data.id)
                data.order_number = order_number
                request.session['order_number'] = order_number
                data.save()
            
            # Order id of newly created order
            razorpay_order_id  = razorpay_order['id']
            callback_url = 'paymenthandler/'

            payment_type = request.POST['payment']
            order = Order.objects.get(
                user=current_user, is_ordered = False, order_number = order_number
            )

            context = {
                'order': order,
                'cart_items' : cart_items,
                'total' : total,
                'GST' : GST,
                'grand_total' : grand_total,
                'razorpay_order_id' : razorpay_order_id,
                'razorpay_merchant_key': settings.RAZOR_KEY_ID,
                'razorpay_amount': amount,
                'callback_url': callback_url,
                'payment_type' : payment_type,
                'discount':discount,
                'amount_pay':amount_pay,
            }
            return render(request,'orders/payments.html', context)
    else:
        return redirect('checkout')



@csrf_exempt
def paymenthandler(request, total=0, quantity=0):
    # Only accept POST request
    if request.method == 'POST':
        try:
            # get the required parameters from post request
            payment_id = request.POST.get("razorpay_payment_id","")
            razorpay_order_id = request.POST.get("razorpay_order_id","")
            signature = request.POST.get("razorpay_signature","")
            
            params_dict = {
                "razorpay_order_id" : razorpay_order_id,
                "razorpay_payment_id" : payment_id,
                "razorpay_signature" : signature
            }
            
            # Verify the payment signature
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                amount = request.session['razorpay_amount']
                try:
                    # Capture the payment
                    razorpay_client.payment.capture(payment_id, amount)

                    # Render Success Page on successfull capture of payment

                    order = Order.objects.get(user=request.user, is_ordered=False, order_number=razorpay_order_id)

                    # Save payment information
                    payment = Payment(
                        user = request.user,
                        payment_id = payment_id,
                        payment_method = 'RazorPay',
                        amount_paid = order.order_total,
                        status = 'Completed',
                    )
                    payment.save()

                    order.payment = payment
                    order.is_ordered = True
                    order.save()


                    # Move the cart item to order product table
                    cart_items = CartItem.objects.filter(user=request.user)

                    for item in cart_items:
                        orderproduct = OrderProduct()
                        orderproduct.order_id = order.id
                        orderproduct.payment = payment
                        orderproduct.user_id = request.user.id
                        orderproduct.product_id = item.product_id
                        orderproduct.quantity = item.quantity
                        orderproduct.product_price = item.product.price
                        orderproduct.order_total = order.order_total
                        orderproduct.ordered = True
                        orderproduct.save()
                        
                        # cart_item = CartItem.objects.get(id=item.id)
                        # product_variation = cart_item.variations.all()
                        # orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                        # orderproduct.variations.set(product_variation)
                        # orderproduct.save()

                        # Reduce the quantity of sold products
                        product = Product.objects.get(id = item.product_id)
                        product.stock -= item.quantity
                        product.save()

                    # Clear the Cart
                    CartItem.objects.filter(user=request.user).delete()
                    
                   # Send order recieved email to customer
                    mail_subject = 'Thank you for your order!'
                    message = render_to_string('orders/order_recieved_email.html', {
                        'user': request.user,
                        'order': order,
                    })
                    to_email = request.user.email
                    send_email = EmailMessage(mail_subject, message, to=[to_email])
                    send_email.send()

                    # Send Transaction Successfull
                    param = (
                        "order_number="+ order.order_number +"&payment_id=" + payment.payment_id
                    )

                    # Capture the payment
                    redirect_url = reverse("order_complete")
                    return redirect(f"{redirect_url}?{param}")
                    # Render success page on successfull capture of payment
                
                except Exception as e:
                    # If there is an error while capturing payment
                    messages.error(request,"Payment Failed")
                    return redirect("place_order")

            else:
                messages.error(request,"Payment Failed")
                return redirect("place_order")
                
                # if signature verification fails

        except:
            messages.error(request,"Payment Failed")
            return redirect("place_order")
            
            # If required parameters in not found in POST data

    else:
        return redirect("place_order")
        # if request is not POST


def cod(request):
    current_user = request.user
    # generate order number
    order_number = request.session["order_number"]
    # move cart items to order product table
    cart_items = CartItem.objects.filter(user=current_user)
    order = Order.objects.get(
        user=current_user, is_ordered=False, order_number=order_number
    )

    # save payment informations
    payment = Payment(
        user=current_user,
        payment_id=order_number,
        payment_method="Cash On Delivery",
        amount_paid=order.order_total,
        status="Completed",
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.order_total = order.order_total       
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        # cart_item = CartItem.objects.get(id=item.id)
        # product_variation = cart_item.variations.all()
        # orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        # orderproduct.variations.set(product_variation)
        # orderproduct.save()

        # Reduce the quantity of sold products
        product = Product.objects.get(id=item.product_id)
        product.stock = product.stock - item.quantity
        product.save()

            # clear the cart
        CartItem.objects.filter(user=request.user).delete()

    # send transaction successfull
    param = (
        "order_number="
        + order.order_number
        + "&payment_id="
        + payment.payment_id
    )
    # Capture the payemt
    if "order_number" in request.session:
        del request.session["order_number"]

    redirect_url = reverse("order_complete")
    return redirect(f"{redirect_url}?{param}")


def order_complete(request):
    order_number = request.GET.get("order_number")
    transID = request.GET.get("payment_id")

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            "order": order,
            "ordered_products" : ordered_products,
            'order_number' : order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal' : subtotal,
        }
        return render(request,"orders/order_complete.html", context)

    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')






    
