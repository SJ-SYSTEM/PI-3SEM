from django.urls import path
from . import views

urlpatterns = [
    path('produtos/metricas/', views.ProdutoMetricas.as_view(), name='produto-metricas'),
    path('produtos/', views.ProdutoListCreate.as_view(), name='produto-list'),
    path('produtos/<str:id>/', views.ProdutoDetail.as_view(), name='produto-detail'),

    path('relatorios/bi-estoque/', views.BiEstoqueView.as_view(), name='bi-estoque'),
]