from django import forms
from users.models import Product, Cart


class CartForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    quantity = forms.IntegerField(min_value=1, max_value=99, initial=1)


class OrderForm(forms.Form):
    name = forms.CharField(max_length=200, label='Имя')
    address = forms.CharField(widget=forms.Textarea, label='Адрес')
    email = forms.EmailField(label='Email')
    cart = forms.ModelChoiceField(queryset=Cart.objects.all())