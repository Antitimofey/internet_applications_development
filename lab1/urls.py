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
from django.urls import include, path

from lab3_api import views as api_views
from rest_framework import routers, permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view


router = routers.DefaultRouter()

router.register(r'user', api_views.UserViewSet, basename='user')

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

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
    path('del-aimodel/<int:user_id>/', views.del_aimodel, name='del-aimodel'),


    #==================== REST API ==============================
    path('', include(router.urls)),
    # Dataset URLs
    path(r'api/datasets/', api_views.DatasetList.as_view(), name='dataset-list'),
    path(r'api/datasets/<int:pk>/', api_views.DatasetDetail.as_view(), name='dataset-detail'),
    path(r'api/datasets/load-img/<int:dataset_id>/', api_views.ImageUploadView.as_view(), name='dataset-img-loader'),

    # DatasetInAIModel URLs
    path(r'api/add-to-draft-aimodel/<int:dataset_id>/', api_views.add_to_draft_aimodel.as_view(), name='add-to-draft-aimodel'),
    path(r'api/dataset-in-aimodel/<int:dataset_id>/', api_views.DatasetInAIModelAPI.as_view(), name='dataset-in-aimodel'),

    # AIModel URLs
    path(r'api/aimodel/basket-icon/', api_views.AIModelBasketIcon.as_view(), name='aimodel-basket-icon'),
    path(r'api/aimodels/', api_views.AIModelList.as_view(), name='aimodel-list'),
    path(r'api/aimodels/<int:pk>/', api_views.AIModelDetail.as_view(), name='aimodel-detail'),
    path(r'api/aimodel/update/', api_views.AIModelUpdate.as_view(), name='aimodel-update'),
    path(r'api/aimodel/form/', api_views.AIModelForm.as_view(), name='aimodel-form'),
    path(r'api/aimodel/complete-reject/<int:pk>/', api_views.AIModelCompleteReject.as_view(), name='aimodel-complete-reject'),
    path(r'api/aimodel/delete/<int:pk>/', api_views.AIModelDelete.as_view(), name='aimodel-delete'),

    # User URLs
    # path(r'api/auth/register/', api_views.RegisterView.as_view(), name='user-register'),
    # path(r'api/auth/profile/', api_views.UserProfileView.as_view(), name='user-profile'),
    path(r'api/auth/login/', api_views.LoginView.as_view(), name='user-login'),
    path(r'api/auth/logout/', api_views.LogoutView.as_view(), name='user-logout'),
    
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    ########################### Swagger ##########################
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),


    # path('login/',  api_views.login_view, name='login'),
    # path('logout/', api_views.logout_view, name='logout'),

]