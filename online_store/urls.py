"""
URL configuration for online_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users.views import (product_list, product_detail, cart_detail, checkout,
                         add_to_cart, order_confirmation, register, home_view,
                         logout_view, cart_remove_item, cart_clear,
                         cart_update_item, order_history, order_detail
                         )
admin_url = os.environ.get('ADMIN_URL', 'admin/')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('products/', product_list, name='product_list'),
    path('products/<int:pk>/', product_detail, name='product_detail'),
    path('cart/', cart_detail, name='cart_detail'),
    path('checkout/', checkout, name='checkout'),
    path('order/<int:order_id>/', order_confirmation, name='order_confirmation'),  # noqa: E501
    path('register/', register, name='register'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', cart_remove_item, name='cart_remove_item'),  # noqa: E501
    path('cart/clear/', cart_clear, name='cart_clear'),
    path('cart/update/<int:item_id>/', cart_update_item, name='cart_update_item'),  # noqa: E501
    path('orders/', order_history, name='order_history'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # noqa: E501
    path('logout/', logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
