from django.urls import path
from . import views

urlpatterns = [
    path('place_order/',views.place_order,name='place_order'),
    path('order_complete/',views.order_complete, name='order_complete'),
    path('place_order/paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path("cod/", views.cod, name="cod"),
]
