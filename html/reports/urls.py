
from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.ProdutoListCreate.as_view(), name='produto-list'),
    path('produtos/<str:id>/', views.ProdutoDetail.as_view(), name='produto-detail'),

    path('clientes/', views.ClienteListCreate.as_view(), name='cliente-list'),
    path('clientes/<str:id>/', views.ClienteDetail.as_view(), name='cliente-detail'),

    path('vendas/', views.VendaListCreate.as_view(), name='venda-list'),
    path('vendas/<str:id>/', views.VendaDetail.as_view(), name='venda-detail'),

    path('relatorios/diarios/', views.RelatorioDiarioList.as_view(), name='relatorio-diario'),
    path('relatorios/estoque-critico/', views.EstoqueCritico.as_view(), name='estoque-critico'),
    path('relatorios/ticket-medio/', views.TicketMedio.as_view(), name='ticket-medio'),
]
