"""
URL configuration for lab1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from app_for_lab1 import views
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', views.hello),

    path('observe_dataset/<int:card_number>/', views.render_card, name='model-desc'),
    path('observe_dataset/<int:card_number>/<int:user_id>/', views.render_card, name='model-desc-idx'),
    path('dataset_market/', views.render_cards_list, name='ai-market'),
    path('dataset_market/<int:user_id>/', views.render_cards_list, name='ai-market-idx'),
    path('calculate_time/', views.render_basket, name='time-calc'),
    path('calculate_time/<int:user_id>/', views.render_basket, name='time-calc-idx'),

    path('add-to-aimodel/<int:dataset_id>/<int:user_id>/', views.add_to_aimodel, name='add-to-aimodel'),

]