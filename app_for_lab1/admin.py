from django.contrib import admin
from .models import Dataset, AIModel, DatasetInAIModel

# Register your models here.

admin.site.register(Dataset)
admin.site.register(AIModel)
admin.site.register(DatasetInAIModel)
