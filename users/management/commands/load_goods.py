from django.core.management.base import BaseCommand
from django.core.management import call_command
import traceback


class Command(BaseCommand):
    help = "Загружает данные остатков товаров из data.json"

    def handle(self, *args, **options):
        try:
            # Выполняем стандартную команду loaddata
            call_command('loaddata', 'data.json')
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Успешно загружены остатки товаров из data.json')
            )
        except Exception as e:
            # Показываем полную ошибку и трейсбек
            self.stderr.write(self.style.ERROR(
                f'❌ Ошибка при загрузке данных: {e}')
            )
            self.stderr.write(self.style.ERROR('Полный traceback:'))
            self.stderr.write(self.style.ERROR(traceback.format_exc()))
