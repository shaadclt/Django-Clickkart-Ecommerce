import datetime
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from store.models import Product, Variation
from django.contrib.auth import authenticate, login
from store.forms import ProductForm, VariationForm, ProductGalleryForm
from .forms import EditProduct, EditVariation, EditCategory, EditCoupon
from category.forms import CategoryForm 
from datetime import date
from coupon.forms import CouponForm
from coupon.models import Coupon
from accounts.models import Account
from category.models import Category
from django.http import JsonResponse, HttpResponse
from orders.models import Order, OrderProduct, STATUS1, Payment
from django.db.models import Sum
import csv
from django.template.loader import render_to_string
from django.utils import timezone
import tempfile
from weasyprint import HTML
# import xlwt



@csrf_exempt
def adminlogin(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(email=email, password=password, is_admin=True)

        try:
            if user.is_superadmin:
                if user is not None:
                    request.session["key"] = "value"
                    login(request,user)
                    messages.success(request, "Admin Online")
                    return redirect("dashboard")
                else:
                    messages.error(request, "You are not an Admin")
                    return redirect("adminlogin")
        except Exception as e:
            messages.error(request,"You are not an Admin")
        else:
            messages.error(request, "You are not an admin")
            return redirect("adminlogin")
    
    return render(request, "adminapp/adminlogin.html")


# Admin - Change Password
@login_required(login_url='adminlogin')
@user_passes_test(lambda user: user.is_superadmin)
def admin_change_password(request):
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
                return redirect('admin_change_password')
            else:
                messages.error(request,"Please enter correct current password")
                return redirect('admin_change_password')
        else:
            messages.error(request,"Passwords does not match")
            return redirect('admin_change_password')

    return render(request,'adminapp/admin_change_password.html')



@login_required(login_url='adminlogin')
@user_passes_test(lambda user: user.is_superadmin)
def signout(request):
    if request.session.has_key("key"):
        del request.session["key"]
        request.session.modified = True
    return redirect("adminlogin")


# Admin Dashboard
@login_required(login_url='adminlogin')
@user_passes_test(lambda user: user.is_superadmin)
def dashboard(request):
    products = Product.objects.all()
    total_revenue = OrderProduct.objects.aggregate(Sum("order_total"))
    total_orders = OrderProduct.objects.filter(ordered=True).count()
    total_products = Product.objects.filter(is_available=True).count()

    if request.session.has_key("key"):

        # Sales/orders
        current_year = timezone.now().year
        status2 = ["New","Placed","Shipped","Accepted","Delivered"]
        order_detail = OrderProduct.objects.filter(created_at__lt=datetime.date(current_year, 12, 31),ordered=True)
        # Using '__' we can access foreign key objects
        
       
        monthly_order_count = []
        month = timezone.now().month
       
        for i in range(1, month + 1):
            monthly_order = order_detail.filter(created_at__month=i).count() - order_detail.filter(created_at__month=i,status="Cancelled").count()
            monthly_order_count.append(monthly_order)

        # Status
        new_count = OrderProduct.objects.filter(status="New").count()
        placed_count = OrderProduct.objects.filter(status="Placed").count()
        shipped_count = OrderProduct.objects.filter(status="Shipped").count()
        accepted_count = OrderProduct.objects.filter(status="Accepted").count()
        delivered_count = OrderProduct.objects.filter(status="Delivered").count()
        cancelled_count = OrderProduct.objects.filter(status="Cancelled").count()

        # most moving product
        most_moving_product_count = []
        most_moving_product = []
        for i in products:
            most_moving_product.append(i)
            most_moving_product_count.append(
                OrderProduct.objects.filter(product=i, status="New").count())

        context = {
            "order_detail": order_detail,
            "monthly_order_count": monthly_order_count,
            "status_counter": [
                new_count,
                placed_count,
                shipped_count,
                accepted_count,
                delivered_count,
                cancelled_count,
            ],
            "most_moving_product_count": most_moving_product_count,
            "most_moving_product": most_moving_product,
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_products": total_products,
        }
        return render(request, "adminapp/dashboard.html", context)
    else:
        return redirect("adminlogin")


# Display all Products
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def productlist(request):
    if request.session.has_key("key"):
        datas = Product.objects.all()
        return render(request,"adminapp/productlist.html",{"datas": datas})
    else:
        return redirect("dashboard")


# Add Products
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def addproduct(request):
    form = ProductForm()

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("productlists")

    context = {"form": form}
    return render(request, "adminapp/productadd.html", context)

#Add Product Gallery
@login_required(login_url='adminlogin')
@user_passes_test(lambda user: user.is_superadmin)
def addproductgallery(request):
    form = ProductGalleryForm()

    if request.method == "POST":
        form = ProductGalleryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("productlists")

    context = {"form": form}
    return render(request, "adminapp/addproductgallery.html", context)


# Edit Products
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def editProduct(request, product_id):
    edtproduct = Product.objects.get(pk=product_id)
    form = EditProduct(instance=edtproduct)
    if request.method == "POST":
        form = EditProduct(request.POST, request.FILES, instance=edtproduct)
        if form.is_valid():
            try:
                form.save()

            except:
                context = {"form": form}
                return render(request, "adminapp/editproduct.html", context)
            return redirect("productlists")

    context = {"form": form}
    return render(request, "adminapp/editproduct.html", context)


# Delete Products
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def deleteproduct(request, product_id):
    dlt = Product.objects.get(pk=product_id)
    dlt.delete()
    messages.success(request,"Product Has been deleted")
    return redirect("productlists")


# Display all Variations
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def variationlist(request):
    variations = Variation.objects.all()
    for v in variations:
        print(v.product)

    context = {
        "variations": variations,
    }
    return render(request, "adminapp/variationlist.html", context)


# Add Variation
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def addvariation(request):
    form = VariationForm()
    if request.method == "POST":
        form = VariationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("variationlist")

    context = {"form": form}
    return render(request, "adminapp/addvariation.html", context)


# Edit Variation
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def editvariation(request, variation_id):
    edtvarient = Variation.objects.get(pk=variation_id)
    form = EditVariation(instance=edtvarient)
    if request.method == "POST":
        form = EditVariation(request.POST, instance=edtvarient)
        if form.is_valid():
            try:
                form.save()

            except:
                context = {"form": form}
                return render(request, "adminapp/editvariation.html", context)
            return redirect("variationlist")

    context = {"form": form}
    return render(request, "adminapp/editvariation.html", context)


# Delete Variation
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def deletevariation(request, variation_id):
    dlt = Variation.objects.get(pk=variation_id)
    dlt.delete()
    messages.success(request, "Variation has been deleted")
    return redirect("variationlist")


# Display All Categories
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def categorylist(request):
    categories = Category.objects.all()
    return render(
        request, "adminapp/categorylist.html", {"categories": categories}
    )


# Add Category
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def addcategory(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("categorylist")

    context = {"form": form}
    return render(request, "adminapp/addcategory.html", context)


# Edit Category
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def editcategory(request, category_id):
    category = Category.objects.get(pk=category_id)
    form = EditCategory(instance=category)
    if request.method == "POST":
        form = EditCategory(request.POST, request.FILES, instance=category)
        if form.is_valid():
            try:
                form.save()

            except:
                context = {"form": form}
                return render(request, "adminapp/editcategory.html", context)
            return redirect("categorylists")

    context = {"form": form}
    return render(request, "adminapp/editcategory.html", context)


# Delete Category
@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def deletecategory(request, category_id):
    category = Category.objects.get(pk=category_id)
    category.delete()
    messages.success(request, "Category has been deleted")
    return redirect("categorylist")



@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def activeorders(request):
    exclude_list = ["Delivered", "Cancelled"]
    active_orders = OrderProduct.objects.all().exclude(status__in=exclude_list)[::-1]  # for reversing the order.
    status = STATUS1
    
    context = {
        "active_orders": active_orders,
        "status": status,
    }
    return render(request, "adminapp/activeorders.html", context)


@login_required(login_url='adminlogin')
@user_passes_test(lambda user: user.is_superadmin)
def admin_order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)  # with the '__' we can access foreign key objects
    order = Order.objects.get(order_number=order_id)
    subtotal = 0

    for i in order_detail:
        subtotal = subtotal + i.product_price * i.quantity

    context = {
        "order_detail": order_detail,
        "order": order,
        "subtotal": subtotal,
    }

    return render(request, "adminapp/admin_order_detail.html", context)


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def order_history(request):
    exclude_list = [
        "New",
        "Accepted",
        "Placed",
        "Shipped",
    ]
    active_orders = OrderProduct.objects.all().exclude(
        status__in=exclude_list
    )[::-1]
    status = STATUS1
    context = {
        "active_orders": active_orders,
        "status": status,
    }
    return render(request, "adminapp/order_history.html", context)


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def order_status_change(request):
    id = request.POST["id"]
    status = request.POST["status"]
    order_product = OrderProduct.objects.get(id=id)
    order_product.status = status
    order_product.save()
    return JsonResponse({"success": True})



@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def activeusers(request):
    users = Account.objects.order_by("id").filter(is_admin=False).all()
    return render(request, "adminapp/activeusers.html", {"users": users})


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def blockuser(request, user_id):
    if request.user.is_authenticated:
        user = Account.objects.get(pk=user_id)
        user.is_active = False
        user.save()
        return redirect("activeusers")

@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def unblockuser(request, user_id):
    if request.user.is_authenticated:
        user = Account.objects.get(pk=user_id)
        user.is_active = True
        user.save()
        return redirect("activeusers")


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def deleteuser(request, user_id):
    if request.user.is_authenticated:
        dlt = Account.objects.get(pk=user_id)
        dlt.delete()
        return redirect("activeusers")


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def couponlist(request):
    today = date.today()
    coupon_form = CouponForm()
    coupons = Coupon.objects.all().order_by("-id")

    for coupon in coupons:
        if coupon.valid_from <= today and coupon.valid_to >= today:
            Coupon.objects.filter(id=coupon.id).update(active=True)
        else:
            Coupon.objects.filter(id=coupon.id).update(active=False)

    context = {
        "coupon_form": coupon_form,
        "coupons": coupons,
    }
    return render(request, "adminapp/couponlist.html", context)


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def add_coupon(request):
    form = CouponForm()
    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("couponlist")
    context = {"form": form}
    return render(request, "adminapp/add_coupon.html", context)



@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def editcoupon(request, coupon_id):
    edtcoupon = Coupon.objects.get(pk=coupon_id)
    form = EditCoupon(instance=edtcoupon)
    if request.method == "POST":
        form = EditCoupon(request.POST, instance=edtcoupon)
        if form.is_valid():
            try:
                form.save()

            except:
                context = {"form": form}
                return render(request, "admin/editcoupon.html", context)
            return redirect("coupon_lists")

    context = {"form": form}
    return render(request, "adminapp/editcoupon.html", context)


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def deletecoupon(request, coupon_id):
    coupon = Coupon.objects.get(pk=coupon_id)
    coupon.delete()
    messages.success(request, "Coupon has been deleted")
    return redirect("couponlist")


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def product_report(request):
    products = Product.objects.all()
    orders = OrderProduct.objects.filter(ordered=True).order_by("-created_at")

    if request.GET.get("from"):
        date_from = datetime.datetime.strptime(
            request.GET.get("from"), "%Y-%m-%d"
        )
        date_to = datetime.datetime.strptime(
            request.GET.get("to"), "%Y-%m-%d"
        )
        date_to += datetime.timedelta(days=1)
        orders = OrderProduct.objects.filter(
            created_at__range=[date_from, date_to]
        )

    if request.GET.get("from"):
        date_from = datetime.datetime.strptime(
            request.GET.get("from"), "%Y-%m-%d"
        )
        date_to = datetime.datetime.strptime(
            request.GET.get("to"), "%Y-%m-%d"
        )
        date_to += datetime.timedelta(days=1)
        products = Product.objects.filter(
            created_date__range=[date_from, date_to]
        )

    context = {
        "products": products,
        "orders": orders,
    }
    return render(request, "adminapp/product_report.html", context)



@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def sales_report(request):
    products = Product.objects.all()
    orders = OrderProduct.objects.filter(ordered=True).order_by("-created_at") and OrderProduct.objects.exclude(status="Cancelled").order_by("-created_at")

    if request.GET.get("from"):
        date_from = datetime.datetime.strptime(
            request.GET.get("from"), "%Y-%m-%d"
        )
        date_to = datetime.datetime.strptime(
            request.GET.get("to"), "%Y-%m-%d"
        )
        date_to += datetime.timedelta(days=1)
        orders = OrderProduct.objects.filter(
            created_at__range=[date_from, date_to]
        )

    if request.GET.get("from"):
        date_from = datetime.datetime.strptime(
            request.GET.get("from"), "%Y-%m-%d"
        )
        date_to = datetime.datetime.strptime(
            request.GET.get("to"), "%Y-%m-%d"
        )
        date_to += datetime.timedelta(days=1)
        products = Product.objects.filter(
            created_date__range=[date_from, date_to]
        )

    context = {
        "products": products,
        "orders": orders,
    }
    return render(request, "adminapp/sales_report.html", context)


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def product_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = "attachement; filename=Product_Report.csv"

    writer = csv.writer(response)
    writer.writerow(
        [
            "Product Name",
            "Brand Name",
            "Category Name",
            "Rating",
            "Price",
            "Stock",
        ]
    )

    products = Product.objects.all().order_by("id")

    for product in products:
        writer.writerow(
            [
                product.product_name,
                product.category,
                product.averageReview(),
                product.price,
                product.stock,
            ]
        )

    return response


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def product_export_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; attachement; filename=Product_Report.pdf"

    response["Content-Transfer-Encoding"] = "binary"

    products = Product.objects.all().order_by("id")

    html_string = render_to_string(
        "adminapp/product_pdf_output.html", {"products": products, "total": 0}
    )

    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output.seek(0)
        # output = open(output.name, "rb")
        response.write(output.read())

    return response


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def sales_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=orders.csv"

    writer = csv.writer(response)
    orders = OrderProduct.objects.filter(ordered=True).order_by("-created_at")

    writer.writerow(
        [
            "Order Number",
            "Customer",
            "Product",
            "Amount",
            "Payment",
            "Qty",
            "Status",
            "Date",
        ]
    )

    for order in orders:
        writer.writerow(
            [
                order.order.order_number,
                order.user.full_name(),
                order.product,
                order.product_price,
                order.payment.payment_method,
                order.quantity,
                order.status,
                order.updated_at,
            ]
        )
    return response


@login_required(login_url="adminlogin")
@user_passes_test(lambda user: user.is_superadmin)
def sales_export_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = "inline; attachement; filename=sales_report.pdf"

    response["Content-Transfer-Encoding"] = "binary"

    orders = OrderProduct.objects.filter(ordered=True).order_by("-created_at")

    html_string = render_to_string(
        "adminapp/sales_pdf_output.html", {"orders": orders, "total": 0}
    )

    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, "rb")
        response.write(output.read())

    return response
