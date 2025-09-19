from django.shortcuts import render
from datetime import date
from .data import CARDS_DATA, USERS_DATA
from .models import Dataset, AIModel, DatasetInAIModel
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib import messages
from django.shortcuts import redirect

def hello(request):
    return render(request, 'index.html', {'current_date': date.today()})


# CARDS_DATA:
#     'label': 'ResNet-50 and CIFAR-10',
#     'benchmark_performance': 2850,
#     'dataset_size': 60000,
#     'img': 'http://172.18.0.5:9000/forlab1images/ResNet-50_CIFAR-10.png'


def render_card(request, card_number: int, user_id: int = 0):
    dataset = Dataset.objects.filter(id=card_number)[0]
    return render(request, 'card_index.html', {'card_data': dataset, 'current_user_id': user_id})



def render_cards_list(request, user_id:int = 0):
    # Получаем параметр поиска из GET запроса
    search_query = request.GET.get('search-model', '').strip()

    datasets = Dataset.objects.filter(is_active=True)


    filtered_data = Dataset.objects.filter(is_active=True, label__icontains=search_query) if search_query else Dataset.objects.filter(is_active=True)

    # Фильтруем карточки по названию
    # if search_query: filtered_data = [card_data for card_data in datasets if search_query in card_data['label']]
    # else: filtered_data = datasets

    context = {
        'products': filtered_data,
        'basket_len':get_basket_len(user_id),
        'users': get_user_model().objects.filter(is_superuser=False),
        'current_user_id': user_id,
    }

    return render(request, 'cards_list_index.html', context=context)



def render_basket(request, user_id:int = 0):
    query = """select m.id, d.dataset_size, benchmark_performance, img from app_for_lab1_datasetinaimodel m
        join app_for_lab1_dataset d on d.id = m.dataset_id
        where m.aimodel_id = (
        select id from app_for_lab1_aimodel
        where status like 'DRAFT' and client_id = %s
    )"""
    datasets = execute_sql_to_dicts(query, [user_id])

    for card_data in datasets:
        card_data['estimate_time'] = round(card_data['dataset_size'] / card_data['benchmark_performance'], 2)

    context = {
        'products': datasets,
        'basket_len':get_basket_len(user_id),
        'users': get_user_model().objects.filter(is_superuser=False),
        'current_user_id': user_id,
    }

    return render(request, 'basket.html', context=context)




def add_to_aimodel(request, dataset_id: int, user_id: int = 0):
    try:
        aimodel = AIModel.objects.get(client=user_id, status='DRAFT')
    except AIModel.DoesNotExist:
        User = get_user_model()
        AIModel.objects.create(**{'client': User.objects.get(id=user_id), 'status':'DRAFT'})
        aimodel = AIModel.objects.get(client=user_id, status='DRAFT')

    dct = {
        'dataset': Dataset.objects.get(id=dataset_id),
        'aimodel': aimodel,
    }
    if not DatasetInAIModel.objects.filter(dataset=dct['dataset'], aimodel=dct['aimodel']).exists():
        DatasetInAIModel.objects.create(**dct)

    messages.success(request, 'Операция выполнена успешно!')
    return redirect('ai-market-idx', user_id=user_id)






def execute_sql_to_dicts(sql, params=None):
    """
    Выполняет SQL запрос и возвращает результат как список словарей
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        
        # Получаем названия колонок
        columns = [col[0] for col in cursor.description]
        
        # Преобразуем в список словарей
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results

def get_basket_len(user_id: int):
    query = """select count(*) as basket_len from app_for_lab1_datasetinaimodel m
    where m.aimodel_id = (
        select id from app_for_lab1_aimodel
        where status like 'DRAFT' and client_id = %s
    )"""
    return execute_sql_to_dicts(query, [user_id])[0]['basket_len']
