from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Order, OrderItem
from online_store.forms import CartForm, OrderForm

# Create your views here.


def product_list(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'product_list.html', context)


def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    context = {'product': product}
    return render(request, 'product_detail.html', context)


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']

            # Получаем или создаём корзину пользователя
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Добавляем товар в корзину (увеличиваем количество, если уже есть)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return redirect('cart_detail')  # перенаправление на страницу корзины
    else:
        form = CartForm()
    return render(request, 'add_to_cart.html', {'form': form})


@login_required
def cart_detail(request):
    try:
        cart = request.user.cart
        items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        items = []
    return render(request, 'cart_detail.html', {'cart': cart, 'items': items})


@login_required
def checkout(request):
    try:
        cart = request.user.cart
        items = cart.items.all()
    except Cart.DoesNotExist:
        return redirect('product_list')  # если корзины нет, идём на главную

    if not items:
        return redirect('cart_detail')   # если корзина пуста, возвращаемся

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаём заказ
            order = Order.objects.create(
                customer=request.user.customer,  # предполагаем, что у пользователя есть профиль Customer
                status='new',
                total_amount=cart.total()
            )
            # Переносим товары из корзины в заказ
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_time=item.product.price
                )
            # Очищаем корзину
            cart.items.all().delete()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = OrderForm()

    return render(request, 'checkout.html', {'form': form, 'cart': cart, 'items': items})


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    return render(request, 'order_confirmation.html', {'order': order})