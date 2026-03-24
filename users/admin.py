from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, Category, Product, Stock, Customer, CartItem, Order, OrderItem


# Register your models here.


admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Customer)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)