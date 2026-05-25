from django.urls import path
from . import views

urlpatterns = [
    # O caminho vazio '' significa que esta será a página inicial do app
    path('', views.index, name='index'),
]