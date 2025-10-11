from app_for_lab1.models import Dataset, AIModel, DatasetInAIModel
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import os

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'label', 'benchmark_performance', 'dataset_size']

class DatasetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = '__all__'

class DatasetInAIModelSerializer(serializers.ModelSerializer):
    dataset_label = serializers.CharField(source='dataset.label', read_only=True)
    dataset_img = serializers.URLField(source='dataset.img', read_only=True)
    
    class Meta:
        model = DatasetInAIModel
        fields = ['dataset', 'dataset_label', 'dataset_img', 'gpus_cnt', 'fitting_time']

class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    filename = serializers.CharField(required=False, max_length=255)
    
    def validate_image(self, value):
        # Проверка размера файла (максимум 5MB)
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size too large. Max 50MB allowed.")
        
        # Проверка формата
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError("Unsupported file format.")
        
        return value


class AIModelSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.username', read_only=True)
    manager_username = serializers.CharField(source='manager.username', read_only=True, allow_null=True)
    
    class Meta:
        model = AIModel
        fields = ['id', 'status', 'creation_datatime', 'formation_datetime', 
                 'complition_datetime', 'client', 'client_username', 'manager', 
                 'manager_username', 'batch_size', 'epochs']

class AIModelDetailSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.username', read_only=True)
    manager_username = serializers.CharField(source='manager.username', read_only=True, allow_null=True)
    datasets = DatasetInAIModelSerializer(source='binded_aimodels', many=True, read_only=True)
    
    class Meta:
        model = AIModel
        fields = ['id', 'status', 'creation_datatime', 'formation_datetime', 
                 'complition_datetime', 'client', 'client_username', 'manager', 
                 'manager_username', 'batch_size', 'epochs', 'datasets']



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login')
        read_only_fields = ('id', 'username', 'date_joined', 'last_login')

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')