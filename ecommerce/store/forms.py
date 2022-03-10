from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter username'})
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Confirm password'})


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter your name'})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter email address'})
        self.fields['address'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter address'})
        self.fields['contact'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter contact no.'})

class CheckoutForm(forms.Form):
    street_address = forms.CharField()
    appartment_address = forms.CharField(required=False)
    country = forms.CharField()
    contact = forms.RegexField(regex=r'^[0-9]{5,10}$')

    def __init__(self, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)
        # self.fields['country'].disabled = True
        self.fields['country'].initial = 'Nepal'
        self.fields['street_address'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter your address'})
        self.fields['appartment_address'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter your secondary address'})
        self.fields['country'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter your country name'})
        self.fields['contact'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter your phone no.'})
