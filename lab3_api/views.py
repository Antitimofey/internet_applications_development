from datetime import datetime, timezone
import uuid

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from lab3_api.serializer import *
from app_for_lab1.models import Dataset, AIModel, DatasetInAIModel
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from utils.minio_client import get_minio_client, ensure_bucket_exists
from django.http import HttpResponse

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model, authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializer import UserRegistrationSerializer, UserProfileSerializer, UserLoginSerializer
from .permissions import IsAdmin, IsManager

import redis
# Connect to our Redis instance
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator


def method_redis_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            # Получаем куку
            ssid = self.request.COOKIES.get("session_id")
            if not ssid:
                return Response({'error': 'No session'}, status=401)
            
            # Проверяем сессию в Redis
            user_email = session_storage.get(ssid).decode('utf-8')
            if not user_email:
                return Response({'error': 'Invalid session'}, status=401)
            print(user_email)
            
            # Получаем пользователя
            User = get_user_model()
            try:
                user = User.objects.get(email=user_email)
                print('is he staff:', user.is_staff)
                self.request.user = user
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=401)
            
            # Проверяем permissions стандартным способом
            self.permission_classes = classes
            self.check_permissions(self.request)
            
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

class DatasetList(APIView):
    model_class = Dataset
    serializer_class = DatasetSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        datasets = Dataset.objects.filter(is_active=True)
        # Получаем параметр поиска из GET запроса
        search_query = request.GET.get('search-model', '').strip()
        filtered_data = Dataset.objects.filter(is_active=True, label__icontains=search_query) if search_query else Dataset.objects.filter(is_active=True)
        serializer = self.serializer_class(filtered_data, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(request_body=DatasetSerializer)
    @method_redis_permission_classes((IsManager,))
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class DatasetDetail(APIView):
    model_class = Dataset
    serializer_class = DatasetSerializer
    authentication_classes = []
    permission_classes = []


    # @swagger_auto_schema(query_serializer=DatasetSerializer)
    def get(self, request, pk, format=None):
        dataset = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(dataset)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=DatasetSerializer)
    @method_redis_permission_classes((IsManager,))
    def put(self, request, pk, format=None):
        dataset = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(dataset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        dataset = get_object_or_404(self.model_class, pk=pk)
        dataset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


############################# Image Loader ##############################################

class ImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, dataset_id: int):
        serializer = ImageUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            custom_filename = serializer.validated_data.get('filename')
            
            try:
                # Генерируем уникальное имя файла
                if custom_filename:
                    filename = custom_filename
                else:
                    file_ext = os.path.splitext(image_file.name)[1]
                    filename = f"{uuid.uuid4()}{file_ext}"
                
                # Создаем путь для хранения
                today = datetime.now().strftime("%Y/%m/%d")
                object_name = f"images/{today}/{filename}"
                
                # Убеждаемся, что бакет существует
                ensure_bucket_exists(settings.MINIO_BUCKET_NAME)
                
                # Загружаем в MinIO
                minio_client = get_minio_client()
                
                minio_client.put_object(
                    bucket_name=settings.MINIO_BUCKET_NAME,
                    object_name=object_name,
                    data=image_file,
                    length=image_file.size,
                    content_type=image_file.content_type
                )
                
                # Формируем URL для доступа к файлу
                if settings.MINIO_PUBLIC_URL:
                    file_url = f"{settings.MINIO_PUBLIC_URL}/{settings.MINIO_BUCKET_NAME}/{object_name}"
                else:
                    file_url = minio_client.presigned_get_object(
                        settings.MINIO_BUCKET_NAME,
                        object_name
                    )
                
                # Загружаем изображение в датасет
                dataset = Dataset.objects.get(pk=dataset_id)
                dataset.img = file_url
                dataset.save()

                
                return Response({
                    'message': 'Image uploaded successfully',
                    'filename': filename,
                    'object_name': object_name,
                    'url': file_url,
                    'size': image_file.size
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Failed to upload image: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



################# Добавление датасета в DatasetInAIModel #############################
class add_to_draft_aimodel(APIView):
    authentication_classes = []
    permission_classes = []
    
    @swagger_auto_schema(request_body=DatasetSerializer)
    @method_redis_permission_classes((IsAuthenticated,))
    def post(self, request, dataset_id, format=None):
        """Добавление датасета в заявку-черновик"""
        
        try:
            aimodel = AIModel.objects.get(client=request.user.id, status=AIModel.Status.DRAFT)
        except AIModel.DoesNotExist:
                AIModel.objects.create(**{'client': request.user, 'status':'DRAFT'})
                aimodel = AIModel.objects.get(client=request.user, status='DRAFT')

        dct = {
            'dataset': Dataset.objects.get(id=dataset_id),
            'aimodel': aimodel,
        }
        if not DatasetInAIModel.objects.filter(dataset=dct['dataset'], aimodel=dct['aimodel']).exists():
            DatasetInAIModel.objects.create(**dct)
            message = 'Dataset added to draft AIModel'
            http_status = status.HTTP_201_CREATED
        else:
            message = 'Dataset already in AIModel'
            http_status = status.HTTP_200_OK
        
        return Response({
            'message': message,
            'aimodel_id': aimodel.id,
        }, status=http_status)



# AIModel Views
class AIModelBasketIcon(APIView):
    authentication_classes = []
    permission_classes = []

    @method_redis_permission_classes((IsAuthenticated,))
    def get(self, request, format=None):
        """GET иконки корзины (без входных параметров, ид заявки вычисляется).
        Возвращается id заявки-черновика этого пользователя и количество услуг в этой заявке"""
        user = request.user
        
        try:
            draft_aimodel = AIModel.objects.get(
                client=user,
                status=AIModel.Status.DRAFT
            )
            datasets_count = draft_aimodel.binded_aimodels.count()
            return Response({
                'aimodel_id': draft_aimodel.id,
                'datasets_count': datasets_count
            })
        except AIModel.DoesNotExist:
            return Response({
                'aimodel_id': None,
                'datasets_count': 0
            })


class AIModelList(APIView):
    authentication_classes = []
    permission_classes = []

    @method_redis_permission_classes((IsAuthenticated,))
    def get(self, request, format=None):
        """GET список (кроме удаленных и черновика, поля модератора и создателя через логины)
        с фильтрацией по диапазону даты формирования и статусу"""
        # Исключаем удаленные и черновики
        aimodels = AIModel.objects.exclude(
            status__in=[AIModel.Status.DELETED, AIModel.Status.DRAFT]
        )

        # СОЗДАТЕЛЬ и не админ или менеждер - видит только свои заявки
        if not (request.user.is_staff or request.user.is_superuser):
            aimodels = aimodels.filter(client=request.user)
        
        # Фильтрация по статусу
        status_filter = request.query_params.get('status', None)
        if status_filter:
            aimodels = aimodels.filter(status=status_filter)
        
        # Фильтрация по диапазону даты формирования
        formation_date_from = request.query_params.get('formation_date_from', None)
        formation_date_to = request.query_params.get('formation_date_to', None)
        
        if formation_date_from:
            try:
                formation_date_from = datetime.strptime(formation_date_from, '%Y-%m-%d').date()
                aimodels = aimodels.filter(formation_datetime__date__gte=formation_date_from)
            except ValueError:
                pass
        
        if formation_date_to:
            try:
                formation_date_to = datetime.strptime(formation_date_to, '%Y-%m-%d').date()
                aimodels = aimodels.filter(formation_datetime__date__lte=formation_date_to)
            except ValueError:
                pass
        
        serializer = AIModelSerializer(aimodels, many=True)
        return Response(serializer.data)


class AIModelDetail(APIView):
    def get(self, request, pk, format=None):
        """GET одна запись (поля заявки + ее услуги).
        При получении заявки возвращется список ее услуг с картинками"""
        aimodel = get_object_or_404(AIModel, pk=pk)
        if aimodel.status == AIModel.Status.DELETED:
            return Response({'error': 'AIModel not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AIModelDetailSerializer(aimodel)
        return Response(serializer.data)


class AIModelUpdate(APIView):
    authentication_classes = []
    permission_classes = []

    @method_redis_permission_classes((IsAuthenticated,))
    def put(self, request, format=None):
        """PUT изменения полей заявки по теме"""
        user = request.user
        aimodel = get_object_or_404(AIModel, client=user, status=AIModel.Status.DRAFT)
        
        if aimodel.status != AIModel.Status.DRAFT:
            return Response({'error': 'Can only update DRAFT aimodels'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Разрешаем изменение только определенных полей
        allowed_fields = ['batch_size', 'epochs']
        data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = AIModelSerializer(aimodel, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AIModelForm(APIView):
    authentication_classes = []
    permission_classes = []

    @method_redis_permission_classes((IsAuthenticated,))
    def put(self, request, format=None):
        """PUT сформировать создателем (дата формирования). Происходит проверка на обязательные поля"""
        user = request.user
        aimodel = get_object_or_404(AIModel, client=user, status=AIModel.Status.DRAFT)
        
        if aimodel.status != AIModel.Status.DRAFT:
            return Response({'error': 'Can only form DRAFT aimodels'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверка обязательных полей
        if not (aimodel.batch_size and aimodel.epochs):
            return Response({'error': 'batch_size and epochs is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if aimodel.binded_aimodels.count() == 0:
            return Response({'error': 'At least one dataset is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Смена статуса на FORMED
        aimodel.status = AIModel.Status.FORMED
        aimodel.formation_datetime = datetime.now()
        aimodel.save()
        
        serializer = AIModelSerializer(aimodel)
        return Response(serializer.data)



class AIModelCompleteReject(APIView):
    authentication_classes = []
    permission_classes = []

    @method_redis_permission_classes((IsManager,))
    def put(self, request, pk, format=None):
        """PUT завершить/отклонить модератором. При завершить/отклонении заявки проставляется модератор и дата завершения.
        Одно из доп. полей заявки или м-м рассчитывается (реализовать формулу представленную в лаб-2) при завершении заявки
        (вычисление стоимости заказа, даты доставки в течении месяца, вычисления в м-м)."""
        user = request.user
        aimodel = get_object_or_404(AIModel, id=pk)
        
        if aimodel.status != AIModel.Status.FORMED:
            return Response({'error': 'Can only complete/reject FORMED aimodels'}, status=status.HTTP_400_BAD_REQUEST)
        
        action = request.data.get('action')
        if action not in ['complete', 'reject']:
            return Response({'error': 'Action must be "complete" or "reject"'}, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'complete':
            aimodel.status = AIModel.Status.COMPLETED
            # Вычисление дополнительных полей
            for dataset_item in aimodel.binded_aimodels.all():
                # Расчет времени обучения на основе формулы
                dataset_item.fitting_time = (dataset_item.dataset.dataset_size * aimodel.epochs) / (dataset_item.gpus_cnt * 1000)
                dataset_item.save()
        else:
            aimodel.status = AIModel.Status.REJECTED
        
        aimodel.manager = user
        aimodel.complition_datetime = datetime.now()
        aimodel.save()
        
        if action == 'complete':
            # Возвращаем расчетные данные
            response_data = AIModelDetailSerializer(aimodel).data
            return Response(response_data)
        
        serializer = AIModelSerializer(aimodel)
        return Response(serializer.data)




class AIModelDelete(APIView):
    def delete(self, request, pk, format=None):
        """DELETE удаление (дата формирования)"""
        aimodel = get_object_or_404(AIModel, id=pk)
        
        if aimodel.status not in [AIModel.Status.DRAFT, AIModel.Status.FORMED]:
            return Response({'error': 'Can only delete DRAFT or FORMED aimodels'}, status=status.HTTP_400_BAD_REQUEST)
        
        aimodel.status = AIModel.Status.DELETED
        aimodel.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)




################################# DatasetInAIModel Views #################################################

class DatasetInAIModelAPI(APIView):
    authentication_classes = []
    permission_classes = []

    @method_redis_permission_classes((IsAuthenticated,))
    def delete(self, request, dataset_id:int, format=None):
        """DELETE удаление из заявки (без PK м-м)"""
        user = request.user
        aimodel = get_object_or_404(AIModel, client=user, status=AIModel.Status.DRAFT)
        dataset_in_aimodel = get_object_or_404(DatasetInAIModel, dataset_id=dataset_id, aimodel_id=aimodel.id)
        
        dataset_in_aimodel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @method_redis_permission_classes((IsAuthenticated,))
    def put(self, request, dataset_id:int, format=None):
        """PUT изменение количества/порядка/значения в м-м (без PK м-м)"""
        user = request.user
        aimodel = get_object_or_404(AIModel, client=user, status=AIModel.Status.DRAFT)
        dataset_in_aimodel = get_object_or_404(DatasetInAIModel, dataset_id=dataset_id, aimodel_id=aimodel.id)
        
        serializer = DatasetInAIModelSerializer(dataset_in_aimodel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




#################################### User Views ##########################################################

User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request, format=None):
        # ИСПОЛЬЗУЕМ request.data (JSON ТЕЛО)
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            random_key = uuid.uuid4()
            session_storage.set(str(random_key), user.email)

            response = Response({"status": "ok"})
            response.set_cookie("session_id", str(random_key))
            return response
        else:
            return Response({"status": "error", "error": "login failed"}, status=401)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        logout(request)
        return Response({'message': 'Logout successful'})



##################################### Athtorization #############################


class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

