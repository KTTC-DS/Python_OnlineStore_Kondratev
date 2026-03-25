# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, StockBalance, Customer, CartItem, Order, OrderItem


# --- Пользователь (User) ---
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Отображение списка пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ()}),
    )


# --- Категория ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# --- Товар ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'display_image')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    readonly_fields = ('display_image',)

    def display_image(self, obj):
        if obj.image:
            return f"<img src='{obj.image.url}' width='50' height='50' style='object-fit: cover; border-radius: 4px;' />"
        return "Нет изображения"
    display_image.short_description = "Изображение"
    display_image.allow_tags = True  # Для Django < 4.2; в 4.2+ не нужно


# --- Остатки товаров ---
@admin.register(StockBalance)
class StockBalanceAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')
    list_editable = ('quantity',)  # Можно редактировать прямо в списке
    search_fields = ('product__name',)
    ordering = ('product__name',)


# --- Клиент ---
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'user', 'phone')
    search_fields = ('last_name', 'first_name', 'user__username', 'phone')
    list_filter = ('user__is_active',)


# --- Элемент корзины ---
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('product__name',)


# --- Заказ ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'status', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__user__username', 'customer__last_name')
    readonly_fields = ('order_date', 'total_amount')
    ordering = ('-order_date',)


# --- Элемент заказа ---
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_time')
    search_fields = ('product__name', 'order__id')
    readonly_fields = ('price_at_time',)