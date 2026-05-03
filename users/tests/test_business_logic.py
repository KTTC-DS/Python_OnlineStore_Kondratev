from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from users.models import Category, Product, Cart, CartItem
from users.views import create_order_from_cart


User = get_user_model()


class BusinessLogicTestCase(TestCase):
    """Unit-тесты для изолированной бизнес-логики."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='123'
        )
        self.customer = self.user.customer
        self.category = Category.objects.create(name='Тестовая')
        self.product = Product.objects.create(
            name='Тестовый товар',
            description='Описание',
            price=Decimal('100.00'),
            category=self.category
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )

    def test_create_order_from_cart(self):
        """Проверяет, что из корзины создаётся правильный заказ и корзина очищается."""   # noqa
        order = create_order_from_cart(self.cart, self.customer)

        # Проверяем созданный заказ
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.total_amount, Decimal('300.00'))
        self.assertEqual(order.status, 'new')
        self.assertEqual(order.items.count(), 1)

        # Проверяем элемент заказа
        order_item = order.items.first()
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 3)
        self.assertEqual(order_item.price_at_time, Decimal('100.00'))

        # Корзина должна быть пуста
        self.assertEqual(self.cart.items.count(), 0)
