from django import forms
from .models import EwasteRequest
from django.core.validators import RegexValidator

class VerifyForm(forms.Form):
    house_no = forms.CharField(
        validators=[RegexValidator(r'^\d+$', 'Only numbers allowed')]
    )

    pincode = forms.CharField(
        validators=[RegexValidator(r'^\d{6}$', 'Enter valid 6 digit pincode')]
    )

    mobile = forms.CharField(
        validators=[RegexValidator(r'^\d{10}$', 'Enter valid 10 digit mobile number')]
    )

class EwasteRequestForm(forms.ModelForm):

    class Meta:
        model = EwasteRequest
        fields = [
            'item_name',
            'quantity',
            'condition',
            'device_details',
        ]
