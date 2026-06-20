from django.urls import path
from . import views

urlpatterns = [
    path('produtos/metricas/',                 views.ProdutoMetricas.as_view(),          name='produto-metricas'),
    path('produtos/',                          views.ProdutoListCreate.as_view(),        name='produto-list'),
    path('produtos/<str:id>/',                 views.ProdutoDetail.as_view(),            name='produto-detail'),
    path('clientes/',                          views.ClienteListCreate.as_view(),        name='cliente-list'),
    path('clientes/<str:id>/',                 views.ClienteDetail.as_view(),            name='cliente-detail'),
    path('vendas/',                            views.VendaListCreate.as_view(),          name='venda-list'),
    path('vendas/<str:id>/',                   views.VendaDetail.as_view(),              name='venda-detail'),
    path('relatorios/diarios/',                views.RelatorioDiarioList.as_view(),      name='relatorio-diario'),
    path('relatorios/estoque-critico/',        views.EstoqueCritico.as_view(),           name='estoque-critico'),
    path('relatorios/ticket-medio/',           views.TicketMedio.as_view(),              name='ticket-medio'),
    path('relatorios/kpis/',                   views.KpisView.as_view(),                 name='kpis'),
    path('relatorios/faturamento-por-dia/',    views.FaturamentoPorDiaView.as_view(),    name='fat-dia'),
    path('relatorios/mensal/',                 views.ComparativoMensalView.as_view(),    name='mensal'),
    path('relatorios/produtos-mais-vendidos/', views.ProdutosMaisVendidosView.as_view(), name='prod-vendidos'),
    path('relatorios/lista-produtos/',         views.ListaProdutosView.as_view(),        name='lista-produtos'),
    path('relatorios/bi-estoque/',          views.BiEstoqueView.as_view(),             name='bi-estoque'),
    path('relatorios/bi/',                 views.BiVendasView.as_view(),              name='bi-vendas'),
    path('relatorios/lista-status/',           views.ListaStatusView.as_view(),          name='lista-status'),
]
