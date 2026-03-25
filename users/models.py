from django.db import models
from django.contrib.auth.models import AbstractUser, User


# Create your models here.

class User(AbstractUser):
    pass


# Категория товара
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


# Товар
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey('Category', on_delete=models.PROTECT)

    def __str__(self):
        return self.name


# Клиент
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True, unique=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def total(self):
        return sum(item.product.price * item.quantity for item in self.items.all())


# Корзина
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

# Заказ
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"


# Состав заказа
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # цена на момент заказа

    def __str__(self):
        return f"{self.product.name} x{self.quantity} (order #{self.order.id})"


#  Остаток по товару
class StockBalance(models.Model):
    product = models.OneToOneField('Product', on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Остаток на складе")

    def __str__(self):
        return f"{self.product.name} — {self.quantity} шт."

    class Meta:
        verbose_name = "Остаток товара"
        verbose_name_plural = "Остатки товаров"