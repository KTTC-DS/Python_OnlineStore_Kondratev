from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


# Категория товара
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


# Товар
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey('Category', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


# Клиент
class Customer(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='customer'
                                )
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        # Если указаны имя/фамилия – показываем их, иначе только username
        full_name = f"{self.last_name} {self.first_name}".strip()
        if full_name:
            return f"{self.user.username} ({full_name})"
        return self.user.username


# Корзина
class Cart(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='cart'
                                )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        # Возвращаем имя пользователя или, если его нет, "Корзина #id"
        if self.user and self.user.username:
            return f"Корзина {self.user.username}"
        return f"Корзина №{self.id}"

    def total(self):
        """Возвращает общую сумму всех товаров в корзине"""
        return sum(
            item.product.price * item.quantity for item in self.items.all()
        )


# Элемент корзины
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,
                             on_delete=models.CASCADE,
                             related_name='items'
                             )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'

    def __str__(self):
        # Отображаем название товара и количество
        return (f"{self.product.name} x{self.quantity} "
                f"(в корзине {self.cart.user.username})"
                )


# Заказ
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    customer = models.ForeignKey(Customer,
                                 on_delete=models.PROTECT,
                                 related_name='orders'
                                 )

    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default='new'
                              )

    total_amount = models.DecimalField(max_digits=10,
                                       decimal_places=2
                                       )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ №{self.id}"


# Состав заказа
class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='items'
                              )

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    # цена на момент заказа
    price_at_time = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказов'

    def __str__(self):
        return (f"{self.product.name} "
                f"x{self.quantity} "
                f"(заказ #{self.order.id})"
                )


# Остаток по товару
class StockBalance(models.Model):
    product = models.OneToOneField('Product',
                                   on_delete=models.CASCADE,
                                   verbose_name="Товар"
                                   )

    quantity = models.PositiveIntegerField(default=0,
                                           verbose_name="Остаток на складе"
                                           )

    class Meta:
        verbose_name = 'Остаток товара'
        verbose_name_plural = 'Остатки товаров'

    def __str__(self):
        return f"{self.product.name} — {self.quantity} шт."


@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    """Создаёт объект Customer при создании нового пользователя."""
    if created:
        Customer.objects.create(user=instance,
                                last_name='',
                                first_name=''
                                )


@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    """Сохраняет Customer при сохранении пользователя."""
    instance.customer.save()
