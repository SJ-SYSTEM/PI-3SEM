<?php
require_once("php/auth.php");
require_once("php/comum.php");
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Vendas - SJ System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="css/dashboard.css">
    <link rel="stylesheet" href="css/vendas.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
</head>
<body>

<?php echo sidebar('vendas'); ?>
<?php echo topbar('Vendas'); ?>

<div class="main">



    <div class="card-box no-print mb-3">
        <div class="d-flex flex-wrap gap-2 align-items-end">
            <div>
                <div class="form-label" style="font-size:12px;">De</div>
                <input type="date" id="f-de" class="form-control form-control-sm" style="width:130px;">
            </div>
            <div>
                <div class="form-label" style="font-size:12px;">Ate</div>
                <input type="date" id="f-ate" class="form-control form-control-sm" style="width:130px;">
            </div>
            <div>
                <div class="form-label" style="font-size:12px;">Status</div>
                <select id="f-status" class="form-select form-select-sm" style="width:130px;">
                    <option value="">Todos</option>
                    <option value="concluida">Concluida</option>
                    <option value="pendente">Pendente</option>
                    <option value="cancelada">Cancelada</option>
                </select>
            </div>
            <div>
                <div class="form-label" style="font-size:12px;">Pagamento</div>
                <select id="f-pag" class="form-select form-select-sm" style="width:130px;">
                    <option value="">Todos</option>
                    <option value="dinheiro">Dinheiro</option>
                    <option value="pix">PIX</option>
                    <option value="cartao_debito">Debito</option>
                    <option value="cartao_credito">Credito</option>
                </select>
            </div>
            <div>
                <div class="form-label" style="font-size:12px;">Buscar</div>
                <input type="text" id="f-busca" class="form-control form-control-sm" placeholder="Cliente, produto..." style="width:180px;">
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-acao btn-sm" onclick="aplicarFiltros()">Filtrar</button>
                <button class="btn btn-outline-secondary btn-sm" onclick="limparFiltros()">Limpar</button>
                <button class="btn btn-outline-secondary btn-sm" onclick="window.print()">🖨️</button>
            </div>
            <small class="text-muted ms-auto" id="info-periodo"></small>
        </div>
    </div>

    <!-- KPIs vendas -->
    <div class="row mb-2" id="kpis-row"></div>

    <!-- ══ SECAO: ANALISE DE VENDAS ══ -->
    <div class="bi-secao-titulo">Analise de Vendas</div>

    <div class="row">
        <div class="col-md-8">
            <div class="card-grafico">
                <h6>Faturamento x Lucro — periodo selecionado</h6>
                <canvas id="chart-fat" height="140"></canvas>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-grafico">
                <h6>Pagamento por volume</h6>
                <canvas id="chart-donut" height="200"></canvas>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-12">
            <div class="card-grafico">
                <h6>Comparativo mensal — ultimos 6 meses</h6>
                <canvas id="chart-men" height="80"></canvas>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-6">
            <div class="card-grafico">
                <h6>Ticket medio por mes</h6>
                <canvas id="chart-ticket" height="140"></canvas>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card-grafico">
                <h6>Pico de vendas por hora do dia</h6>
                <canvas id="chart-hora" height="140"></canvas>
            </div>
        </div>
    </div>






    <div class="row mb-3">
        <div class="col-md-12">
            <div class="card-grafico">
                <h6>Top 10 produtos mais vendidos no periodo</h6>
                <canvas id="chart-top-produtos" height="80"></canvas>
            </div>
        </div>
    </div>

    <!-- ══ HISTORICO DE VENDAS ══ -->
    <!-- ══ GRAFICOS DO PERIODO ══ -->
    <div class="row mb-3">
        <div class="col-md-12">
            <div class="card-grafico">
                <h6>Saida de estoque no periodo (unidades)</h6>
                <canvas id="chart-estoque-periodo" height="60"></canvas>
            </div>
        </div>
    </div>
    <div class="card-box">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="mb-0">Historico de vendas</h5>
            <small class="text-muted" id="info-registros"></small>
        </div>
        <div style="overflow-x:auto; max-height:500px; overflow-y:auto;">
            <table class="tabela-vendas">
                <thead>
                    <tr>
                        <th onclick="ordenarPor('id')" style="cursor:pointer;">N° ↕</th>
                        <th onclick="ordenarPor('data')" style="cursor:pointer;">Data ↕</th>
                        <th>Cliente</th>
                        <th>Itens</th>
                        <th onclick="ordenarPor('total')" style="cursor:pointer;">Total ↕</th>
                        <th>Pagamento</th>
                        <th>Status</th>
                        <th class="no-print">Acoes</th>
                    </tr>
                </thead>
                <tbody id="tbody-vendas">
                    <tr><td colspan="8" class="text-muted text-center py-3">Carregando...</td></tr>
                </tbody>
            </table>
        </div>
        <div class="d-flex justify-content-between align-items-center mt-3 pt-2" style="border-top:1px solid #eee;">
            <small class="text-muted" id="info-total-registros">—</small>
            <div class="fw-bold" id="total-filtrado" style="color:#c40000; font-size:1rem;"></div>
        </div>
    </div>

</div>

<!-- Modal Detalhe -->
<div class="modal fade" id="modalDetalhe" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Detalhes da venda</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="detalhe-body"></div>
            <div class="modal-footer">
                <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Fechar</button>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="js/relatorios.js?v=21"></script>
</body>
</html>
