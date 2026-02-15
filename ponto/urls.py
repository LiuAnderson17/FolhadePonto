from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bater-ponto/', views.bater_ponto, name='bater_ponto'),
    path('relatorio/', views.relatorio, name='relatorio'),
]