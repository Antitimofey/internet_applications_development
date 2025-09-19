# yourapp/management/commands/load_initial_data.py
from typing import Any
from django.core.management.base import BaseCommand
from django.db.models import Model
from django.contrib.auth import get_user_model
from app_for_lab1.models import Dataset, AIModel, DatasetInAIModel
from app_for_lab1.data import CARDS_DATA, USERS, AIMODELS_DATA


class Command(BaseCommand):
    help = 'Load initial data into YourModel'

    def handle(self, *args, **options):

        self.load_dataset_data(CARDS_DATA)
        self.load_aimodel_data(AIMODELS_DATA)

        self.load_users_data(users_data=USERS)




    def load_dataset_data(self, data: list[dict[str, str]]):
        n = 0
        for idx, obj in enumerate(data):
            obj.update({'id': idx})
            if not Dataset.objects.filter(id=idx).exists(): Dataset.objects.create(**obj); n += 1

        self.stdout.write(
            self.style.SUCCESS(f'Добавлено {n} новых записей в {Dataset._meta.label}')
        )


    def load_aimodel_data(self, data: list[dict[str, str]]):
        User = get_user_model()
        n = 0
        for idx, obj in enumerate(data):
            dtc = {
                'id': idx,
                'status': obj['status'],
                'client': User.objects.get(username=obj['client']),
                'manager': User.objects.get(username=obj['manager']),
            }
            if not AIModel.objects.filter(id=idx).exists(): AIModel.objects.create(**dtc); n += 1

        self.stdout.write(
            self.style.SUCCESS(f'Добавлено {n} новых записей в {AIModel._meta.label}')
        )


    def load_users_data(self, users_data: list[dict[str, str]]):
        User = get_user_model()
        n = 0
        for obj in users_data:
            if not User.objects.filter(username=obj['username']).exists(): User.objects.create_user(**obj); n += 1

        self.stdout.write(
            self.style.SUCCESS(f'Добавлено {n} новых записей в {User._meta.label}')
        )
