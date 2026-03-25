from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Экспортирует остатки товаров в файл data.json"

    def handle(self, *args, **options):
        try:
            with open('data.json', 'w', encoding='utf-8') as f:
                call_command(
                    'dumpdata',
                    'users.StockBalance',
                    format='json',
                    indent=2,
                    stdout=f
                )
            self.stdout.write(
                self.style.SUCCESS('✅ Остатки успешно экспортированы в data.json')
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'❌ Ошибка экспорта: {e}')
            )