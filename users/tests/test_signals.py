from django.test import TestCase
from django.contrib.auth import get_user_model

from users.models import Customer

User = get_user_model()


class SignalTests(TestCase):
    def test_customer_created_after_user_creation(self):
        """При создании нового пользователя автоматически создаётся Customer"""
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='pass123'
        )
        # Проверяем, что Customer существует и связан с этим пользователем
        self.assertTrue(Customer.objects.filter(user=user).exists())
        customer = Customer.objects.get(user=user)
        # Проверяем пустые значения по умолчанию
        self.assertEqual(customer.last_name, '')
        self.assertEqual(customer.first_name, '')
        self.assertEqual(customer.middle_name, '')
        self.assertEqual(customer.address, '')
        self.assertEqual(customer.phone, '')

    def test_customer_not_created_twice(self):
        """Повторное сохранение пользователя не создаёт дубликат Customer"""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='pass'
        )
        # Должен быть один Customer
        self.assertEqual(Customer.objects.filter(user=user).count(), 1)
        # Сохраняем пользователя ещё раз
        user.save()
        self.assertEqual(Customer.objects.filter(user=user).count(), 1)

    def test_customer_saved_signal(self):
        """Сигнал save_customer не вызывает ошибок"""
        user = User.objects.create_user(
            'signaluser',
            'signal@example.com',
            'pass'
        )
        customer = Customer.objects.get(user=user)
        # Изменяем поля
        customer.last_name = 'Петров'
        customer.save()
        # Обновляем ссылку из пользователя
        user.refresh_from_db()
        self.assertEqual(user.customer.last_name, 'Петров')
