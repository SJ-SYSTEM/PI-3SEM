<?php
require_once("php/auth.php");
require_once("php/comum.php");
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Clientes - SJ System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="css/dashboard.css">
</head>
<body>

<?php echo sidebar('clientes'); ?>
<?php echo topbar('Clientes'); ?>

<div class="main">

    <!-- Métricas rápidas -->
    <div class="row mb-3">
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-total">—</div>
                <div class="label">Total de clientes</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-ativos">—</div>
                <div class="label">Clientes ativos</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-novos">—</div>
                <div class="label">Novos este mês</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card-metrica">
                <div class="valor" id="metric-inativos">—</div>
                <div class="label">Clientes inativos</div>
            </div>
        </div>
    </div>

    <div class="row">

        <!-- ESQUERDA: Lista de clientes -->
        <div class="col-md-8">

            <div class="card-box">
                <h5>Clientes cadastrados</h5>
                <div class="d-flex gap-2 flex-wrap mb-0">
                    <input
                        type="text"
                        id="busca-cliente"
                        class="form-control"
                        placeholder="Buscar por nome, CPF/CNPJ ou telefone..."
                        style="min-width:200px;flex:1;"
                    >
                    <select id="filtro-status-cliente" class="form-select" style="width:140px;flex-shrink:0;" onchange="filtrarClientes()">
                        <option value="">Todos</option>
                        <option value="ativo">Ativos</option>
                        <option value="inativo">Inativos</option>
                    </select>
                    <button class="btn btn-acao" onclick="filtrarClientes()">Buscar</button>
                    <button class="btn btn-outline-secondary" onclick="limparFiltroClientes()">Limpar</button>
                </div>
            </div>

            <div class="card-box">
                <div id="lista-clientes" style="max-height:600px; overflow-y:auto;">
                    <p class="text-muted text-center py-3">Carregando clientes...</p>
                </div>
            </div>

        </div>

        <!-- DIREITA: Formulário -->
        <div class="col-md-4">
            <div class="card-box">
                <h5 id="form-titulo">Novo cliente</h5>

                <input type="hidden" id="cliente-id">

                <div class="mb-3">
                    <label class="form-label fw-bold">Nome <span class="text-danger">*</span></label>
                    <input
                        type="text"
                        id="campo-nome"
                        class="form-control"
                        placeholder="Nome completo ou razão social"
                    >
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">CPF / CNPJ</label>
                    <input
                        type="text"
                        id="campo-documento"
                        class="form-control"
                        placeholder="000.000.000-00"
                        maxlength="18"
                    >
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Telefone</label>
                    <input
                        type="text"
                        id="campo-telefone"
                        class="form-control"
                        placeholder="(00) 00000-0000"
                        maxlength="15"
                    >
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">E-mail</label>
                    <input
                        type="email"
                        id="campo-email"
                        class="form-control"
                        placeholder="cliente@email.com"
                    >
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Endereço</label>
                    <input
                        type="text"
                        id="campo-endereco"
                        class="form-control"
                        placeholder="Rua, número, bairro, cidade"
                    >
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">Status</label>
                    <select class="form-select" id="campo-status">
                        <option value="ativo">✅ Ativo</option>
                        <option value="inativo">🚫 Inativo</option>
                    </select>
                </div>

                <button class="btn-finalizar" onclick="salvarCliente()">
                    💾 Salvar cliente
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


<!-- Modal de Edicao de Cliente -->
<div class="modal fade" id="modalEditar" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Editar cliente</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <input type="hidden" id="modal-cliente-id">

                <div class="mb-3">
                    <label class="form-label fw-bold">Nome <span class="text-danger">*</span></label>
                    <input type="text" id="modal-nome" class="form-control" placeholder="Nome completo">
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold">CPF / CNPJ</label>
                    <input type="text" id="modal-cpf" class="form-control" placeholder="000.000.000-00" maxlength="18">
                </div>
                <div class="row mb-3">
                    <div class="col">
                        <label class="form-label fw-bold">Telefone</label>
                        <input type="text" id="modal-telefone" class="form-control" placeholder="(00) 00000-0000" maxlength="15">
                    </div>
                    <div class="col">
                        <label class="form-label fw-bold">Status</label>
                        <select class="form-select" id="modal-status">
                            <option value="ativo">Ativo</option>
                            <option value="inativo">Inativo</option>
                        </select>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold">E-mail</label>
                    <input type="email" id="modal-email" class="form-control" placeholder="cliente@email.com">
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold">Endereco</label>
                    <input type="text" id="modal-endereco" class="form-control" placeholder="Rua, numero, bairro, cidade">
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-danger" onclick="salvarEdicaoCliente()">Salvar alteracoes</button>
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
                Deseja realmente excluir o cliente <strong id="modal-nome-cliente"></strong>?
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

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="js/clientes.js"></script>
</body>
</html>
