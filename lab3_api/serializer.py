from app_for_lab1.models import Dataset, AIModel, DatasetInAIModel
from rest_framework import serializers

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'label', 'benchmark_performance']