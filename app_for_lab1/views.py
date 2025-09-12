from django.shortcuts import render
from datetime import date
from .data import CARDS_DATA

def hello(request):
    return render(request, 'index.html', {'current_date': date.today()})


card_data = {
    'label': 'dsdsds',
    'benchmark_performance': 20,
    'dataset_size': 50,
}

def render_card(request, card_number: int):
    return render(request, 'card_index.html', {'card_data': CARDS_DATA[card_number]})


def render_cards_list(request):
    # Получаем параметр поиска из GET запроса
    search_query = request.GET.get('search', '').strip()
    
    # Фильтруем карточки по названию
    if search_query:
        # Ищем карточки, где название содержит поисковый запрос (регистронезависимо)
        filtered_data = [card_data for card_data in CARDS_DATA if search_query in card_data['label']]

        return render(request, 'cards_list_index.html', {'products': filtered_data})
    else:
        # Если поисковый запрос пустой, показываем все карточки
        return render(request, 'cards_list_index.html', {'products': CARDS_DATA})


def render_basket(request):
    active_goods = [1, 3, 5]
    filtered_data = [card_data for i, card_data in enumerate(CARDS_DATA) if i in active_goods]
    

    return render(request, 'basket.html', {'products': filtered_data, 'basket_len':len(active_goods)})
