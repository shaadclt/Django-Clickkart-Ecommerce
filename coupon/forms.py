from django import forms
from .models import Coupon


class DateInput(forms.DateInput):
    input_type = "date"


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            "coupon_name",
            "code",
            "coupon_limit",
            "discount",
            "valid_from",
            "valid_to",
        ]
        widgets = {
            "valid_from": DateInput(),
            "valid_to": DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

