
function aplicarMascaraMoeda(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('blur', function () {
        const v = parseFloat(this.value);
        if (!isNaN(v)) this.value = v.toFixed(2);
    });
}
const API = "http://144.22.150.83:8000/api";

let PRODUTOS = [];
let produtoParaExcluir = null;
let idEditando = null;
let modalExcluir, modalEditar;

document.addEventListener('DOMContentLoaded', () => {
    modalExcluir = new bootstrap.Modal(document.getElementById('modalExcluir'));
    modalEditar = new bootstrap.Modal(document.getElementById('modalEditar'));

    document.getElementById('busca-produto').addEventListener('keypress', e => {
        if (e.key === 'Enter') buscarProduto();
    });

    aplicarMascaraMoeda('campo-preco-custo');
    aplicarMascaraMoeda('campo-preco-venda');
    aplicarMascaraMoeda('modal-preco-custo');
    aplicarMascaraMoeda('modal-preco-venda');

    // Mascara monetaria
    ['campo-preco-custo', 'campo-preco-venda', 'modal-preco-custo', 'modal-preco-venda'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('blur', function () {
            const v = parseFloat(this.value);
            if (!isNaN(v)) this.value = v.toFixed(2);
        });
    });

    carregarProdutos();
});

async function carregarProdutos(status = 'ativo') {
    try {
        const res = await fetch(`${API}/produtos/?status=${status}`);
        const json = await res.json();
        PRODUTOS = json.data || [];
        renderProdutos(PRODUTOS);
        await carregarMetricas();
    } catch (e) {
        document.getElementById('lista-produtos').innerHTML =
            '<p class="text-danger text-center py-3">Erro ao carregar produtos. Verifique a API.</p>';
        console.error(e);
    }
}

async function carregarMetricas() {
    try {
        const res = await fetch(`${API}/produtos/metricas/`);
        const d = await res.json();
        document.getElementById('metric-total').textContent = d.total ?? '—';
        document.getElementById('metric-ativos').textContent = d.ativos ?? '—';
        document.getElementById('metric-criticos').textContent = d.criticos ?? '—';
        document.getElementById('metric-inativos').textContent = d.inativos ?? '—';
    } catch (e) { console.error(e); }
}

async function buscarProduto() {
    const termo = document.getElementById('busca-produto').value.trim();
    if (!termo) { renderProdutos(PRODUTOS); return; }

    try {
        const res = await fetch(`${API}/produtos/?busca=${encodeURIComponent(termo)}`);
        const json = await res.json();
        renderProdutos(json.data || []);
    } catch (e) {
        const filtrados = PRODUTOS.filter(p =>
            p.nome.toLowerCase().includes(termo.toLowerCase()) ||
            (p.sku || '').toLowerCase().includes(termo.toLowerCase()) ||
            (p.categoria || '').toLowerCase().includes(termo.toLowerCase())
        );
        renderProdutos(filtrados);
    }
}

function renderProdutos(lista) {
    const el = document.getElementById('lista-produtos');

    if (!lista || lista.length === 0) {
        el.innerHTML = '<p class="text-muted text-center py-3">Nenhum produto encontrado.</p>';
        return;
    }

    el.innerHTML = lista.map(p => {
        const critico = p.estoque <= p.estoque_minimo;

        const estoqueBar = Math.min(100, p.estoque_minimo > 0
            ? Math.round((p.estoque / (p.estoque_minimo * 3)) * 100)
            : 100);
        const barColor = critico ? '#c40000' : (estoqueBar < 60 ? '#f0a500' : '#198754');

        return `
        <div class="produto" style="flex-wrap:wrap; gap:6px;">
            <div style="flex:1; min-width:0;">
                <span class="nome">${p.nome}</span>
                ${p.sku ? `<small class="text-muted ms-1">#${p.sku}</small>` : ''}
                <br>
                <small class="text-muted">
                    ${p.categoria ? '🏷️ ' + p.categoria + ' &nbsp;' : ''}
                    ${p.fabricante ? '🏭 ' + p.fabricante + ' &nbsp;' : ''}
                    <br>
                    💰 Venda: <strong>R$ ${fmtMoeda(p.preco_venda)}</strong> &nbsp;

                    ${p.lote ? ' &nbsp;🔖 Lote: ' + p.lote : ''}
                    ${p.validade ? ' &nbsp;📅 Val: ' + fmtData(p.validade) : ''}
                </small>
                <div class="mt-2" style="display:flex; align-items:center; gap:8px;">
                    <small class="${critico ? 'text-danger fw-bold' : 'text-success fw-bold'}">
                        📦 ${p.estoque} ${p.unidade || 'un'}
                    </small>
                    <div style="flex:1; background:#e9ecef; border-radius:20px; height:7px; overflow:hidden;">
                        <div style="width:${estoqueBar}%; background:${barColor}; height:100%; border-radius:20px; transition:width .4s;"></div>
                    </div>
                    <small class="text-muted" style="white-space:nowrap;">mín: ${p.estoque_minimo} ${p.unidade || 'un'}</small>
                </div>
            </div>
            <div class="d-flex align-items-center gap-2">
                <span class="badge ${p.status === 'ativo' ? 'bg-success' : 'bg-secondary'}">
                    ${p.status === 'ativo' ? 'Ativo' : 'Inativo'}
                </span>
                ${critico ? '<span class="badge bg-danger">⚠️ Crítico</span>' : ''}
                <button class="btn btn-sm btn-outline-secondary" onclick="abrirModalEditar('${p.id}')" title="Editar">✏️</button>
                <button class="btn btn-sm" style="color:#c40000;" onclick="pedirExclusao('${p.id}', '${escapeHtml(p.nome)}')" title="Excluir">✕</button>
            </div>
        </div>`;
    }).join('');
}

async function salvarProduto() {
    const nome = document.getElementById('campo-nome').value.trim();
    const sku = document.getElementById('campo-codigo').value.trim();
    const precoCusto = parseFloat(document.getElementById('campo-preco-custo').value.replace(',', '.'));
    const precoVenda = parseFloat(document.getElementById('campo-preco-venda').value.replace(',', '.'));

    if (!nome) { alert('O nome do produto é obrigatório.'); return; }
    if (!sku) { alert('O SKU é obrigatório.'); return; }
    if (isNaN(precoCusto)) { alert('Informe o preço de custo.'); return; }
    if (isNaN(precoVenda)) { alert('Informe o preço de venda.'); return; }

    const body = {
        sku,
        nome,
        fabricante: document.getElementById('campo-fabricante').value.trim(),
        categoria: document.getElementById('campo-categoria').value.trim(),
        preco_custo: precoCusto,
        preco_venda: precoVenda,
        estoque: parseInt(document.getElementById('campo-estoque').value) || 0,
        estoque_minimo: parseInt(document.getElementById('campo-estoque-min').value) || 0,
        unidade: document.getElementById('campo-unidade').value,
        lote: document.getElementById('campo-lote').value.trim(),
        validade: document.getElementById('campo-validade').value || null,
        status: document.getElementById('campo-status').value,
    };

    try {
        const res = await fetch(`${API}/produtos/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const json = await res.json();
        if (!res.ok) { alert('Erro: ' + (json.erro || 'Falha ao salvar.')); return; }
        limparFormulario();
        await carregarProdutos();
        alert('Produto cadastrado com sucesso!');
    } catch (e) {
        alert('Erro de conexão com a API.');
        console.error(e);
    }
}

function abrirModalEditar(id) {
    const p = PRODUTOS.find(x => x.id === id);
    if (!p) return;

    idEditando = id;
    document.getElementById('modal-produto-nome').textContent = p.nome;
    document.getElementById('modal-estoque').value = p.estoque;
    document.getElementById('modal-estoque-min-label').textContent = p.estoque_minimo + ' ' + (p.unidade || 'un');
    document.getElementById('modal-preco-custo').value = p.preco_custo;
    document.getElementById('modal-preco-venda').value = p.preco_venda;

    modalEditar.show();
}

async function salvarEdicaoModal() {
    const novoEstoque = parseInt(document.getElementById('modal-estoque').value);
    const novoCusto = parseFloat(document.getElementById('modal-preco-custo').value);
    const novoVenda = parseFloat(document.getElementById('modal-preco-venda').value);

    if (isNaN(novoEstoque) || novoEstoque < 0) { alert('Informe uma quantidade válida.'); return; }
    if (isNaN(novoCusto) || novoCusto < 0) { alert('Informe um preço de custo válido.'); return; }
    if (isNaN(novoVenda) || novoVenda < 0) { alert('Informe um preço de venda válido.'); return; }

    try {
        const res = await fetch(`${API}/produtos/${idEditando}/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estoque: novoEstoque, preco_custo: novoCusto, preco_venda: novoVenda }),
        });
        const json = await res.json();
        if (!res.ok) { alert('Erro: ' + (json.erro || 'Falha ao atualizar.')); return; }
        modalEditar.hide();
        await carregarProdutos();
        alert('Produto atualizado com sucesso!');
    } catch (e) {
        alert('Erro de conexão com a API.');
        console.error(e);
    }
}

function pedirExclusao(id, nome) {
    produtoParaExcluir = id;
    document.getElementById('modal-nome-produto').textContent = nome;
    modalExcluir.show();
}

async function confirmarExclusao() {
    try {
        const res = await fetch(`${API}/produtos/${produtoParaExcluir}/`, { method: 'DELETE' });
        if (!res.ok) { alert('Erro ao excluir produto.'); return; }
        produtoParaExcluir = null;
        modalExcluir.hide();
        await carregarProdutos();
    } catch (e) {
        alert('Erro de conexão com a API.');
        console.error(e);
    }
}

function limparFormulario() {
    ['campo-nome', 'campo-codigo', 'campo-categoria', 'campo-fabricante', 'campo-lote'].forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('campo-preco-custo').value = '';
    document.getElementById('campo-preco-venda').value = '';
    document.getElementById('campo-estoque').value = 0;
    document.getElementById('campo-estoque-min').value = 0;
    document.getElementById('campo-unidade').value = 'cx';
    document.getElementById('campo-validade').value = '';
    document.getElementById('campo-status').value = 'ativo';

}

function fmtMoeda(v) {
    return parseFloat(v || 0).toFixed(2).replace('.', ',');
}

function fmtData(d) {
    if (!d) return '';
    return d.slice(0, 10).split('-').reverse().join('/');
}

function escapeHtml(str) {
    return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

async function carregarEstoqueCritico() {
    try {
        const res = await fetch(`${API}/relatorios/bi-estoque/?meses=1`);
        const json = await res.json();
        const lista = json.criticos || [];
        const el = document.getElementById('lista-criticos-prod');
        if (!el) return;
        if (lista.length === 0) {
            el.innerHTML = '<p class="text-success text-center py-2">Nenhum produto em estoque critico.</p>';
            return;
        }
        el.innerHTML = '<div style="display:flex;flex-wrap:wrap;gap:10px;">' +
            lista.map(p => `
                <div style="background:#fff8f8;border:1px solid #f5c6c6;border-radius:8px;padding:10px 14px;min-width:160px;">
                    <div style="font-size:13px;font-weight:600;color:#111;">${p.nome}</div>
                    <div style="font-size:12px;color:#c40000;margin-top:4px;">Estoque: ${p.estoque} ${p.unidade}</div>
                    <div style="font-size:11px;color:#888;">Minimo: ${p.estoque_minimo} ${p.unidade}</div>
                </div>`).join('') + '</div>';
    } catch (e) { console.error(e); }
}

document.addEventListener('DOMContentLoaded', () => {
    carregarEstoqueCritico();
});
