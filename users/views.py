from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Order, OrderItem
from online_store.forms import CartForm, OrderForm, CustomUserCreationForm


# ---------------------- Вспомогательные бизнес-функции ----------------------

def create_order_from_cart(cart, customer):
    """Создаёт заказ из корзины и очищает её"""
    order = Order.objects.create(
        customer=customer,
        status='new',
        total_amount=cart.total()
    )
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_time=item.product.price
        )
    cart.items.all().delete()
    return order


# ------------------------- Представления (views) -------------------------

def product_list(request):
    """Отображает список всех товаров."""
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'product_list.html', context)


def product_detail(request, pk):
    """Отображает детальную страницу товара."""
    product = Product.objects.get(pk=pk)
    context = {'product': product}
    return render(request, 'product_detail.html', context)


@login_required
def add_to_cart(request):
    """Добавляет товар в корзину текущего пользователя."""
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            return redirect('cart_detail')
    else:
        form = CartForm()
    return render(request, 'add_to_cart.html', {'form': form})


@login_required
def cart_detail(request):
    """Показывает содержимое корзины пользователя."""
    try:
        cart = request.user.cart
        items = cart.items.all()
        total = cart.total()
    except Cart.DoesNotExist:
        items = []
        total = 0
    return render(request,
                  'cart_detail.html',
                  {'items': items, 'total': total}
                  )


@login_required
def cart_update_item(request, item_id):
    """Изменяет количество товара в корзине."""
    cart_item = get_object_or_404(CartItem,
                                  id=item_id,
                                  cart__user=request.user
                                  )
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart_detail')


@login_required
def cart_remove_item(request, item_id):
    """Удаляет один товар из корзины."""
    cart_item = get_object_or_404(CartItem,
                                  id=item_id,
                                  cart__user=request.user
                                  )
    cart_item.delete()
    return redirect('cart_detail')


@login_required
def cart_clear(request):
    """Полная очистка корзины пользователя."""
    CartItem.objects.filter(cart__user=request.user).delete()
    return redirect('cart_detail')


@login_required
def checkout(request):
    """Оформление заказа и создание заказа из корзины."""
    try:
        cart = request.user.cart
        items = cart.items.all()
        total = cart.total()
    except Cart.DoesNotExist:
        return redirect('product_list')
    if not items:
        return redirect('cart_detail')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = create_order_from_cart(cart, request.user.customer)
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = OrderForm()
    return render(request,
                  'checkout.html',
                  {'form': form, 'items': items, 'total': total}
                  )


@login_required
def order_confirmation(request, order_id):
    """Страница подтверждения заказа."""
    order = get_object_or_404(Order,
                              id=order_id,
                              customer=request.user.customer
                              )
    return render(request, 'order_confirmation.html', {'order': order})


def register(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def home_view(request):
    """Главная страница."""
    return render(request, 'home.html')


def logout_view(request):
    """Выход пользователя."""
    logout(request)
    return render(request, 'registration/logout.html')


@login_required
def order_history(request):
    """История заказов пользователя."""
    orders = (Order.objects.filter(customer=request.user.customer)
              .prefetch_related('items__product')
              .order_by('-order_date')
              )
    return render(request, 'order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Детали конкретного заказа."""
    order = get_object_or_404(Order,
                              id=order_id,
                              customer=request.user.customer
                              )
    items = order.items.all()
    return render(request, 'order_detail.html',
                  {'order': order, 'items': items}
                  )
