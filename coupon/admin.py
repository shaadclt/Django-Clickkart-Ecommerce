from django.contrib import admin
from .models import Coupon, ReviewCoupon


class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "valid_from",'coupon_limit' ,"valid_to", "discount", "active"]
    list_filter = ["active", "valid_from", "valid_to"]
    search_fields = ["code"]


admin.site.register(Coupon,CouponAdmin)
admin.site.register(ReviewCoupon)
