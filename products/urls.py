from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('<int:pk>/', views.car_detail_view, name='detail'),
    path('<int:pk>/order/', views.create_order_view, name='create_order'),
]
