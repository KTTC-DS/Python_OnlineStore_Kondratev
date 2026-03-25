from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from users.models import Product, Cart

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Обязательное поле.")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CartForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    quantity = forms.IntegerField(min_value=1, max_value=99, initial=1)


class OrderForm(forms.Form):
    name = forms.CharField(max_length=200, label='Имя')
    address = forms.CharField(widget=forms.Textarea, label='Адрес')
    email = forms.EmailField(label='Email')
    cart = forms.ModelChoiceField(queryset=Cart.objects.all())