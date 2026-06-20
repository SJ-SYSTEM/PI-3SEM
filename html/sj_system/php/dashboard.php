<?php
require_once("php/auth.php");
require_once("php/comum.php");
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>PDV - SJ System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="css/dashboard.css">
</head>
<body>

<?php echo sidebar('dashboard'); ?>
<?php echo topbar('PDV — Ponto de Venda'); ?>

<div class="main">

    <!-- Métricas rápidas -->
    <div class="row mb-3">
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-vendas-hoje">R$ 0,00</div>
                <div class="label">Vendas hoje</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-transacoes">0</div>
                <div class="label">Transacoes hoje</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-ticket">R$ 0,00</div>
                <div class="label">Ticket medio</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-critico">0</div>
                <div class="label">Estoque critico</div>
            </div>
        </div>
    </div>

    <div class="row">
        <!-- ESQUERDA: Busca e itens -->
        <div class="col-md-8">

            <div class="card-box">
                <h5>Adicionar produto</h5>
                <div class="busca-wrap" style="position:relative;">
                <div>
                    <input
                        type="text"
                        id="busca-produto"
                        class="form-control"
                        placeholder="Digite o nome ou SKU do produto..."
                        autocomplete="off"
                    >

                </div>
                <div id="resultados-busca" style="display:none;position:absolute;z-index:999;background:#fff;border:0.5px solid #ddd;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.1);width:100%;max-height:280px;overflow-y:auto;top:100%;left:0;"></div>
                </div>
            </div>

            <div class="card-box">
                <h5>Itens da venda</h5>
                <div id="lista-itens">
                    <p class="text-muted text-center py-3">
                        Nenhum item adicionado ainda.
                    </p>
                </div>
            </div>

        </div>

        <!-- DIREITA: Resumo -->
        <div class="col-md-4">
            <div class="card-box">
                <h5>Resumo da venda</h5>

                <div class="d-flex justify-content-between mb-2">
                    <span>Subtotal:</span>
                    <span id="subtotal">R$ 0,00</span>
                </div>

                <div class="d-flex justify-content-between mb-2">
                    <span>Desconto:</span>
                    <input
                        type="number"
                        id="desconto"
                        class="form-control form-control-sm w-50 text-end"
                        value="0"
                        min="0"
                        step="0.01"
                    >
                </div>

                <hr>

                <div class="d-flex justify-content-between mb-3">
                    <span class="fw-bold">Total:</span>
                    <span class="total" id="total">R$ 0,00</span>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Forma de pagamento</label>
                    <select class="form-select" id="forma-pagamento">
                        <option value="dinheiro">💵 Dinheiro</option>
                        <option value="pix">📱 PIX</option>
                        <option value="cartao_debito">💳 Cartão Débito</option>
                        <option value="cartao_credito">💳 Cartão Crédito</option>
                    </select>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Cliente (opcional)</label>
                    <div style="position:relative;">
                        <input
                            type="text"
                            id="cliente-nome"
                            class="form-control"
                            placeholder="Buscar cliente..."
                            autocomplete="off"
                        >
                        <div id="resultados-cliente" style="display:none;position:absolute;z-index:9999;background:#fff;border:0.5px solid #ddd;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.1);width:100%;max-height:200px;overflow-y:auto;top:100%;left:0;"></div>
                    </div>
                    <input type="hidden" id="cliente-id">
                </div>

                <button class="btn-finalizar" onclick="finalizarVenda()">
                    ✅ Finalizar venda
                </button>

                <button
                    class="btn w-100 mt-2"
                    style="border:2px solid #c40000; color:#c40000; border-radius:10px;"
                    onclick="limparVenda()"
                >
                    🗑 Limpar
                </button>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="js/dashboard.js?v=5"></script>
</body>
</html>
