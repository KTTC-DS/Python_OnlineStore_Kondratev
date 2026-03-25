from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Экспортирует остатки товаров (StockBalance) в файл stock_data.json"

    def handle(self, *args, **options):
        try:
            # Открываем файл для записи
            with open('stock_data.json', 'w', encoding='utf-8') as f:
                # Выполняем dumpdata для модели StockBalance
                call_command(
                    'dumpdata',
                    'users.StockBalance',           # приложение.модель
                    format='json',
                    indent=2,
                    stdout=f                        # записываем в файл
                )
            self.stdout.write(
                self.style.SUCCESS('✅ Остатки успешно экспортированы в stock_data.json')
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'❌ Ошибка при экспорте данных: {e}')
            )