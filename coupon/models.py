from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Account


class Coupon(models.Model):
    coupon_name = models.CharField(max_length=25)
    code = models.CharField(max_length=25, unique=True)
    coupon_limit = models.IntegerField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)])
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class ReviewCoupon(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)

    def __str__(self):
        return self.coupon.coupon_name