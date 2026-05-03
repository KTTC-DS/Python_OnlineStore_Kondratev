from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from users.models import Product


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Форма для регистрации нового пользователя с дополнительным полем email."""

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
    """Форма для добавления товара в корзину с выбором продукта и количества."""

    product = forms.ModelChoiceField(queryset=Product.objects.all())
    quantity = forms.IntegerField(min_value=1, max_value=99, initial=1)


class OrderForm(forms.Form):
    """Форма оформления заказа: имя, адрес и email покупателя."""

    name = forms.CharField(max_length=200, label='Имя')
    address = forms.CharField(widget=forms.Textarea, label='Адрес')
    email = forms.EmailField(label='Email')
