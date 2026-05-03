from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.db import IntegrityError

from users.models import (
    Category, Product, StockBalance, Cart, CartItem, Order, OrderItem
)

User = get_user_model()


class ModelTestCase(TestCase):
    """
    Набор тестов для проверки моделей интернет-магазина.

    Проверяет создание и корректную работу моделей:
    User, Category, Product, StockBalance, Customer, Cart, CartItem, Order, OrderItem.
    """

    def setUp(self):
        """
        Создаёт тестовые данные, используемые в каждом тесте:
        - пользователя (автоматически создаётся Customer по сигналу)
        - категорию, товар, остаток на складе, корзину.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = self.user.customer
        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(
            name='Тестовый товар',
            description='Описание',
            price=Decimal('99.99'),
            category=self.category
        )
        self.stock = StockBalance.objects.create(
            product=self.product,
            quantity=10
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_user_creation(self):
        """Проверяет создание пользователя, проверку пароля и строковое представление."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(str(self.user), 'testuser')

    def test_category_creation(self):
        """Проверяет создание категории, строковое представление и мета-информацию."""
        self.assertEqual(self.category.name, 'Тестовая категория')
        self.assertEqual(str(self.category), 'Тестовая категория')
        self.assertEqual(self.category._meta.verbose_name, 'Категория')
        self.assertEqual(self.category._meta.verbose_name_plural, 'Категории')

    def test_product_creation(self):
        """Проверяет создание товара, его поля и строковое представление."""
        self.assertEqual(self.product.name, 'Тестовый товар')
        self.assertEqual(self.product.description, 'Описание')
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(str(self.product), 'Тестовый товар')
        self.assertEqual(self.product._meta.verbose_name, 'Товар')
        self.assertEqual(self.product._meta.verbose_name_plural, 'Товары')

    def test_stock_balance_creation(self):
        """
        Проверяет создание остатка товара, уникальность связи OneToOne
        и невозможность создать два остатка для одного товара.
        """
        self.assertEqual(self.stock.product, self.product)
        self.assertEqual(self.stock.quantity, 10)
        self.assertEqual(str(self.stock), f'{self.product.name} — 10 шт.')
        self.assertEqual(self.stock._meta.verbose_name, 'Остаток товара')
        self.assertEqual(self.stock._meta.verbose_name_plural, 'Остатки товаров')
        with self.assertRaises(Exception):
            StockBalance.objects.create(product=self.product, quantity=20)

    def test_customer_creation(self):
        """
        Проверяет автоматическое создание Customer при регистрации пользователя,
        значения полей по умолчанию и строковое представление.
        """
        self.assertEqual(self.customer.user, self.user)
        self.assertEqual(self.customer.last_name, '')
        self.assertEqual(self.customer.first_name, '')
        self.assertEqual(self.customer.middle_name, '')
        self.assertEqual(self.customer.address, '')
        self.assertEqual(self.customer.phone, '')
        self.assertEqual(str(self.customer), self.user.username)
        self.assertEqual(self.customer._meta.verbose_name, 'Клиент')
        self.assertEqual(self.customer._meta.verbose_name_plural, 'Клиенты')

    def test_cart_creation(self):
        """
        Проверяет создание корзины, связь с пользователем,
        строковое представление и метод total() для пустой корзины.
        """
        self.assertEqual(self.cart.user, self.user)
        self.assertIsNotNone(self.cart.created_at)
        self.assertEqual(str(self.cart), f'Корзина {self.user.username}')
        self.assertEqual(self.cart._meta.verbose_name, 'Корзина')
        self.assertEqual(self.cart._meta.verbose_name_plural, 'Корзины')
        self.assertEqual(self.cart.total(), Decimal('0.00'))

    def test_cart_item_creation(self):
        """
        Проверяет добавление товара в корзину, уникальность пары (cart, product),
        обновление количества и строковое представление элемента корзины.
        """
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 3)
        expected_str = (f'{self.product.name} '
                        f'x3 (в корзине {self.user.username})')
        self.assertEqual(str(cart_item), expected_str)
        self.assertEqual(cart_item._meta.verbose_name, 'Элемент корзины')
        self.assertEqual(cart_item._meta.verbose_name_plural,
                         'Элементы корзины')

        self.assertEqual(self.cart.total(), Decimal('99.99') * 3)

        with self.assertRaises(IntegrityError):
            CartItem.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=1
            )

    def test_cart_total_method(self):
        """
        Проверяет правильность расчёта общей суммы корзины при наличии
        нескольких различных товаров с разным количеством.
        """
        product2 = Product.objects.create(
            name='Второй товар',
            description='Описание',
            price=Decimal('50.00'),
            category=self.category
        )
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        CartItem.objects.create(cart=self.cart, product=product2, quantity=1)
        total = self.cart.total()
        expected = Decimal('99.99') * 2 + Decimal('50.00')
        self.assertEqual(total, expected)

    def test_order_creation(self):
        """
        Проверяет создание заказа, корректность статусов (русские имена),
        строковое представление заказа и мета-информацию.
        """
        order = Order.objects.create(
            customer=self.customer,
            status='new',
            total_amount=Decimal('199.98')
        )
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, 'new')
        self.assertEqual(order.total_amount, Decimal('199.98'))
        self.assertEqual(str(order), f'Заказ №{order.id}')
        self.assertEqual(order._meta.verbose_name, 'Заказ')
        self.assertEqual(order._meta.verbose_name_plural, 'Заказы')
        self.assertEqual(dict(Order.STATUS_CHOICES)['new'], 'Новый')
        self.assertEqual(dict(Order.STATUS_CHOICES)['paid'], 'Оплачен')
        self.assertEqual(dict(Order.STATUS_CHOICES)['shipped'], 'Отправлен')
        self.assertEqual(dict(Order.STATUS_CHOICES)['delivered'], 'Доставлен')
        self.assertEqual(dict(Order.STATUS_CHOICES)['cancelled'], 'Отменён')

    def test_order_item_creation(self):
        """
        Проверяет создание позиции заказа, связь с заказом и товаром,
        сохранение цены на момент заказа и строковое представление.
        """
        order = Order.objects.create(
            customer=self.customer,
            status='new',
            total_amount=Decimal('99.99')
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price_at_time=Decimal('99.99')
        )
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.price_at_time, Decimal('99.99'))
        expected_str = f'{self.product.name} x1 (заказ #{order.id})'
        self.assertEqual(str(order_item), expected_str)
        self.assertEqual(order_item._meta.verbose_name, 'Элемент заказа')
        self.assertEqual(order_item._meta.verbose_name_plural, 'Элементы заказов')

    def test_order_creation_from_cart(self):
        """
        Сквозной тест: создание заказа из корзины.
        Проверяет, что все позиции корзины переносятся в заказ,
        а корзина после этого очищается.
        """
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        total = self.cart.total()
        order = Order.objects.create(
            customer=self.customer,
            total_amount=total,
            status='new'
        )
        for item in self.cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_time=item.product.price
            )
        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price_at_time, self.product.price)
        self.cart.items.all().delete()
        self.assertEqual(self.cart.items.count(), 0)