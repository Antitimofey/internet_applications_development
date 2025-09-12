from django.shortcuts import render
from datetime import date
from .data import CARDS_DATA, USERS_DATA

def hello(request):
    return render(request, 'index.html', {'current_date': date.today()})


card_data = {
    'label': 'dsdsds',
    'benchmark_performance': 20,
    'dataset_size': 50,
}

def render_card(request, card_number: int, user_id: int = 0):
    return render(request, 'card_index.html', {'card_data': CARDS_DATA[card_number], 'current_user': USERS_DATA[user_id]})



def render_cards_list(request, user_id:int = 0):
    # Получаем параметр поиска из GET запроса
    search_query = request.GET.get('search', '').strip()

    # Фильтруем карточки по названию
    if search_query: filtered_data = [card_data for card_data in CARDS_DATA if search_query in card_data['label']]
    else: filtered_data = CARDS_DATA

    context = {
        'products': filtered_data,
        'users': USERS_DATA,
        'current_user': USERS_DATA[user_id],
    }
    
    return render(request, 'cards_list_index.html', context=context)



def render_basket(request, user_id:int = 0):
    active_goods = USERS_DATA[user_id]['chosen_models']
    filtered_data = [card_data for i, card_data in enumerate(CARDS_DATA) if i in active_goods]
    
    # Получим пользователя
    # current_user = request.GET.get('user_id')
    # if current_user is None: current_user = 0


    context = {
        'products': filtered_data,
        'basket_len':len(active_goods),
        'users': USERS_DATA,
        'current_user': USERS_DATA[user_id],
    }

    return render(request, 'basket.html', context=context)
