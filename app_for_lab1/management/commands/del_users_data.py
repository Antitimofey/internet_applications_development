# yourapp/management/commands/load_initial_data.py
from django.core.management.base import BaseCommand
from django.db.models import Model
from app_for_lab1.models import Dataset, AIModel, DatasetInAIModel

USER_TABLE_CLASSES: list[Model] = [Dataset, AIModel, DatasetInAIModel]

class Command(BaseCommand):
    help = 'delete all users data from tabels in `model.py`'

    def handle(self, *args, **options):

        for user_table_class in USER_TABLE_CLASSES:
            count, _ = user_table_class.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'🗑️  Удалено {count} записей из {user_table_class._meta.label}')
            )