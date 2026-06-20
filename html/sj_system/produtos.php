<?php
require_once("php/auth.php");
require_once("php/comum.php");
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Produtos - SJ System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="css/dashboard.css">
</head>
<body>

<?php echo sidebar('produtos'); ?>
<?php echo topbar('Produtos'); ?>

<div class="main">

    <!-- Métricas rápidas -->
    <div class="row mb-3">
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-total">—</div>
                <div class="label">Total de produtos</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-ativos">—</div>
                <div class="label">Produtos ativos</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-criticos">—</div>
                <div class="label">Estoque crítico</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-inativos">—</div>
                <div class="label">Produtos inativos</div>
            </div>
        </div>
    </div>

    <div class="row">

        <!-- ESQUERDA: Lista de produtos -->
        <div class="col-md-8">

            <div class="card-box">
                <h5>Produtos cadastrados</h5>
                <div class="input-group mb-0">
                    <input
                        type="text"
                        id="busca-produto"
                        class="form-control"
                        placeholder="Buscar por nome, código ou categoria..."
                    >
                    <button class="btn btn-acao" onclick="buscarProduto()">
                        Buscar
                    </button>
                    <button class="btn btn-acao ms-1" onclick="renderProdutos(produtos)">
                        Todos
                    </button>
                </div>
            </div>

            <div class="card-box">
                <h5>Estoque critico</h5>
                <div id="lista-criticos-prod">
                    <p class="text-muted text-center py-3">Carregando...</p>
                </div>
            </div>

            <div class="card-box">
                <div id="lista-produtos" style="max-height:600px; overflow-y:auto;">
                    <p class="text-muted text-center py-3">Nenhum produto cadastrado ainda.</p>
                </div>
            </div>

        </div>

        <!-- DIREITA: Formulário de cadastro -->
        <div class="col-md-4">
            <div class="card-box">
                <h5 id="form-titulo">Novo produto</h5>

                <div class="mb-3">
                    <label class="form-label fw-bold">Nome <span class="text-danger">*</span></label>
                    <input type="text" id="campo-nome" class="form-control" placeholder="Nome do produto">
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Código / SKU</label>
                    <input type="text" id="campo-codigo" class="form-control" placeholder="Ex: PROD-001">
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Categoria</label>
                    <select class="form-select" id="campo-categoria">
                        <option value="medicamento">Medicamento</option>
                        <option value="perfumaria">Perfumaria</option>
                        <option value="higiene">Higiene</option>
                        <option value="alimento">Alimento</option>
                        <option value="outro">Outro</option>
                    </select>
                </div>

                <div class="row mb-3">
                    <div class="col">
                        <label class="form-label fw-bold">Preço de custo <span class="text-danger">*</span></label>
                        <div class="input-group">
                            <span class="input-group-text">R$</span>
                            <input type="text" id="campo-preco-custo" class="form-control" placeholder="0,00" inputmode="decimal">
                        </div>
                    </div>
                    <div class="col">
                        <label class="form-label fw-bold">Preço de venda <span class="text-danger">*</span></label>
                        <div class="input-group">
                            <span class="input-group-text">R$</span>
                            <input type="text" id="campo-preco-venda" class="form-control" placeholder="0,00" inputmode="decimal">
                        </div>
                    </div>
                </div>

                <div class="row mb-3">
                    <div class="col">
                        <label class="form-label fw-bold">Quantidade</label>
                        <input type="number" id="campo-estoque" class="form-control" placeholder="0" min="0" step="1" value="0">
                    </div>
                    <div class="col">
                        <label class="form-label fw-bold">Estoque crítico</label>
                        <input type="number" id="campo-estoque-min" class="form-control" placeholder="0" min="0" step="1" value="0">
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Unidade</label>
                    <select class="form-select" id="campo-unidade">
                        <optgroup label="── Farmacêutico ──">
                            <option value="cx">Caixa (cx)</option>
                            <option value="cart">Cartela (cart)</option>
                            <option value="fr">Frasco (fr)</option>
                            <option value="amp">Ampola (amp)</option>
                            <option value="bisn">Bisnaga (bisn)</option>
                        </optgroup>
                        <optgroup label="── Geral ──">
                            <option value="un">Unidade (un)</option>
                        </optgroup>
                    </select>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Fabricante / Laboratório</label>
                    <input type="text" id="campo-fabricante" class="form-control" placeholder="Ex: EMS, Medley, Eurofarma...">
                </div>

                <div class="row mb-3">
                    <div class="col">
                        <label class="form-label fw-bold">Lote</label>
                        <input type="text" id="campo-lote" class="form-control" placeholder="Ex: L2024001">
                    </div>
                    <div class="col">
                        <label class="form-label fw-bold">Validade</label>
                        <input type="date" id="campo-validade" class="form-control">
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Status</label>
                    <select class="form-select" id="campo-status">
                        <option value="ativo">✅ Ativo</option>
                        <option value="inativo">🚫 Inativo</option>
                    </select>
                </div>
                </div>

                <button class="btn-finalizar" onclick="salvarProduto()">
                    💾 Salvar produto
                </button>

                <button
                    class="btn w-100 mt-2"
                    style="border:2px solid #c40000; color:#c40000; border-radius:10px;"
                    onclick="limparFormulario()"
                >
                    🗑 Limpar
                </button>
            </div>
        </div>

    </div>
</div>

<!-- ───── Modal de Edição Rápida (Estoque / Preço) ───── -->
<div class="modal fade" id="modalEditar" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered modal-md">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">✏️ Editar produto</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p class="fw-bold mb-3" id="modal-produto-nome" style="font-size:1.05rem;"></p>

                <div class="mb-3">
                    <label class="form-label fw-bold">📦 Quantidade em estoque</label>
                    <input type="number" id="modal-estoque" class="form-control form-control-lg" min="0" step="1">
                    <small class="text-muted">Estoque mínimo: <span id="modal-estoque-min-label"></span></small>
                </div>

                <hr>

                <div class="row">
                    <div class="col">
                        <label class="form-label fw-bold">💲 Preço de custo</label>
                        <div class="input-group">
                            <span class="input-group-text">R$</span>
                            <input type="number" id="modal-preco-custo" class="form-control" min="0" step="0.01">
                        </div>
                    </div>
                    <div class="col">
                        <label class="form-label fw-bold">💰 Preço de venda</label>
                        <div class="input-group">
                            <span class="input-group-text">R$</span>
                            <input type="number" id="modal-preco-venda" class="form-control" min="0" step="0.01">
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-success" onclick="salvarEdicaoModal()">💾 Salvar alterações</button>
            </div>
        </div>
    </div>
</div>

<!-- Modal de confirmação de exclusão -->
<div class="modal fade" id="modalExcluir" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Confirmar exclusão</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                Deseja realmente excluir o produto <strong id="modal-nome-produto"></strong>?
                <br><small class="text-muted">Esta ação não poderá ser desfeita.</small>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-danger" onclick="confirmarExclusao()">Excluir</button>
            </div>
        </div>
    </div>
</div>


<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="js/produtos.js?v=13"></script>
</body>
</html>
