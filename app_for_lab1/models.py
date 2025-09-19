from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Dataset(models.Model):
    label = models.CharField(max_length=255)
    benchmark_performance = models.IntegerField()
    dataset_size = models.IntegerField()
    is_active = models.BooleanField(default=True)
    img = models.URLField(null=True)

    def __str__(self):
        return self.label


class AIModel(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT"
        DELETED = "DELETED"
        FORMED = "FORMED"
        COMPLETED = "COMPLETED"
        REJECTED = "REJECTED"
    
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    creation_datatime = models.DateTimeField(auto_now_add=True)
    formation_datetime = models.DateTimeField(blank=True, null=True)
    complition_datetime = models.DateTimeField(blank=True, null=True)
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_aimodels')
    manager = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='managed_aimodels', blank=True, null=True)

    def __str__(self):
        return f'AIModel № {self.id}'
    

class DatasetInAIModel(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.DO_NOTHING, related_name='binded_datasets', blank=False, null=False)
    aimodel = models.ForeignKey(AIModel, on_delete=models.DO_NOTHING, related_name='binded_aimodels', blank=False, null=False)
    quantity = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.dataset_id}-{self.aimodel_id}"

    class Meta:
        unique_together = ('dataset', 'aimodel'),