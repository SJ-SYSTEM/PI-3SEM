const API = "http://144.22.150.83:8000/api";

let itens = [];

document.addEventListener('DOMContentLoaded', () => {
    carregarMetricas();

    const campoBusca = document.getElementById('busca-produto');
    let timeoutBusca;
    campoBusca.addEventListener('input', () => {
        clearTimeout(timeoutBusca);
        const v = campoBusca.value.trim();
        if (!v) { esconderResultados(); return; }
        timeoutBusca = setTimeout(buscarProduto, 350);
    });
    campoBusca.addEventListener('keypress', e => {
        if (e.key === 'Enter') buscarProduto();
    });

    document.getElementById('desconto').addEventListener('input', atualizarTotal);

    // Busca de cliente
    let timeoutCliente;
    const campoCliente = document.getElementById('cliente-nome');
    campoCliente.addEventListener('input', () => {
        clearTimeout(timeoutCliente);
        const v = campoCliente.value.trim();
        if (!v) { document.getElementById('resultados-cliente').style.display = 'none'; return; }
        timeoutCliente = setTimeout(() => buscarCliente(v), 350);
    });
    document.addEventListener('click', e => {
        if (!e.target.closest('#resultados-cliente') && e.target !== campoCliente) {
            document.getElementById('resultados-cliente').style.display = 'none';
        }
    });
});

async function carregarMetricas() {
    try {
        const hoje = new Date().toISOString().slice(0, 10);
        const [kpis, critico] = await Promise.all([
            fetch(`${API}/relatorios/kpis/?de=${hoje}&ate=${hoje}&status=concluida`).then(r => r.json()),
            fetch(`${API}/relatorios/estoque-critico/`).then(r => r.json()),
        ]);
        document.getElementById('metric-vendas-hoje').textContent    = 'R$ ' + fmt(kpis.faturamento);
        document.getElementById('metric-transacoes').textContent     = kpis.total_vendas;
        document.getElementById('metric-ticket').textContent         = 'R$ ' + fmt(kpis.ticket_medio);
        document.getElementById('metric-critico').textContent        = critico.total ?? 0;
    } catch (e) { console.error(e); }
}

async function buscarProduto() {
    const termo = document.getElementById('busca-produto').value.trim();
    if (!termo) return;

    try {
        const res  = await fetch(`${API}/produtos/?status=ativo&busca=${encodeURIComponent(termo)}`);
        const json = await res.json();
        const lista = json.data || [];

        if (lista.length === 0) {
            mostrarResultados([]);
            return;
        }
        mostrarResultados(lista);
    } catch (e) {
        alert('Erro ao buscar produto. Verifique a API.');
        console.error(e);
    }
}

function mostrarResultados(lista) {
    const el = document.getElementById('resultados-busca');
    if (lista.length === 0) {
        el.innerHTML = '<div style="padding:12px 16px;font-size:13px;color:#888;">Nenhum produto encontrado.</div>';
        el.style.display = 'block';
        return;
    }
    el.innerHTML = lista.map(p => {
        const critico = p.estoque <= p.estoque_minimo;
        const semEstoque = p.estoque <= 0;
        return `
        <div style="padding:10px 14px;border-bottom:0.5px solid #f0f0f0;opacity:${semEstoque ? '0.5' : '1'};">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;">
                <div style="flex:1;min-width:0;">
                    <div style="font-size:13px;font-weight:600;color:#111;">${p.nome}</div>
                    <div style="font-size:11px;color:#888;margin-top:2px;">
                        #${p.sku || ''} &nbsp;|&nbsp; ${p.categoria || ''} &nbsp;|&nbsp; ${p.fabricante || ''}
                    </div>
                    <div style="font-size:11px;color:${semEstoque ? '#c40000' : critico ? '#f0a500' : '#198754'};font-weight:600;margin-top:2px;">
                        ${semEstoque ? 'Sem estoque' : 'Estoque: ' + p.estoque + ' ' + p.unidade + (critico ? ' (critico)' : '')}
                    </div>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <div style="font-size:14px;font-weight:700;color:#c40000;margin-bottom:4px;">R$ ${fmt(p.preco_venda)}</div>
                    <button
                        onclick="selecionarProduto('${p.id}')"
                        ${semEstoque ? 'disabled' : ''}
                        style="font-size:11px;font-weight:600;padding:4px 12px;border-radius:6px;border:none;background:${semEstoque ? '#eee' : '#c40000'};color:${semEstoque ? '#aaa' : '#fff'};cursor:${semEstoque ? 'not-allowed' : 'pointer'};">
                        + Adicionar
                    </button>
                </div>
            </div>
        </div>`;
    }).join('');
    el.style.display = 'block';
}

let CACHE_PRODUTOS = {};
async function selecionarProduto(id) {
    try {
        if (!CACHE_PRODUTOS[id]) {
            const res = await fetch(`${API}/produtos/${id}/`);
            CACHE_PRODUTOS[id] = await res.json();
        }
        adicionarItem(CACHE_PRODUTOS[id]);
        document.getElementById('busca-produto').value = '';
        esconderResultados();
    } catch (e) { console.error(e); }
}

function esconderResultados() {
    document.getElementById('resultados-busca').style.display = 'none';
}

function adicionarItem(produto) {
    const existente = itens.find(i => i.id === produto.id);
    if (existente) {
        if (existente.quantidade >= produto.estoque) {
            alert(`Estoque insuficiente. Disponivel: ${produto.estoque} ${produto.unidade}`);
            return;
        }
        existente.quantidade++;
    } else {
        if (produto.estoque <= 0) {
            alert('Produto sem estoque disponivel.');
            return;
        }
        itens.push({
            id:          produto.id,
            nome:        produto.nome,
            sku:         produto.sku,
            preco_venda: produto.preco_venda,
            preco_custo: produto.preco_custo,
            unidade:     produto.unidade,
            estoque:     produto.estoque,
            quantidade:  1,
        });
    }
    renderItens();
}

function alterarQtd(index, delta) {
    const item = itens[index];
    const nova = item.quantidade + delta;
    if (nova <= 0) { itens.splice(index, 1); }
    else if (nova > item.estoque) { alert(`Estoque maximo: ${item.estoque} ${item.unidade}`); return; }
    else { item.quantidade = nova; }
    renderItens();
}

function removerItem(index) {
    itens.splice(index, 1);
    renderItens();
}

function renderItens() {
    const lista = document.getElementById('lista-itens');
    if (itens.length === 0) {
        lista.innerHTML = '<p class="text-muted text-center py-3">Nenhum item adicionado ainda.</p>';
        atualizarTotal();
        return;
    }

    lista.innerHTML = itens.map((item, i) => `
        <div class="produto" style="flex-wrap:wrap;">
            <div style="flex:1;min-width:0;">
                <span class="nome">${item.nome}</span>
                <small class="text-muted ms-1">#${item.sku || ''}</small>
                <div style="font-size:12px;color:#888;margin-top:2px;">
                    R$ ${fmt(item.preco_venda)} / ${item.unidade} &nbsp;|&nbsp; estoque: ${item.estoque}
                </div>
            </div>
            <div class="d-flex align-items-center gap-2 mt-1">
                <button class="btn btn-sm btn-outline-secondary" onclick="alterarQtd(${i}, -1)">−</button>
                <span style="min-width:24px;text-align:center;font-weight:600;">${item.quantidade}</span>
                <button class="btn btn-sm btn-outline-secondary" onclick="alterarQtd(${i}, 1)">+</button>
                <span class="fw-bold ms-2" style="color:#c40000;min-width:80px;text-align:right;">
                    R$ ${fmt(item.preco_venda * item.quantidade)}
                </span>
                <button class="btn btn-sm" style="color:#c40000;" onclick="removerItem(${i})">✕</button>
            </div>
        </div>`).join('');

    atualizarTotal();
}

function atualizarTotal() {
    const subtotal = itens.reduce((s, i) => s + i.preco_venda * i.quantidade, 0);
    const descontoPct = parseFloat(document.getElementById('desconto').value) || 0;
    const desconto = parseFloat((subtotal * descontoPct / 100).toFixed(2));
    const total    = Math.max(0, subtotal - desconto);

    document.getElementById('subtotal').textContent = 'R$ ' + fmt(subtotal);
    document.getElementById('total').textContent    = 'R$ ' + fmt(total);
}

async function finalizarVenda() {
    if (itens.length === 0) { alert('Adicione ao menos um produto.'); return; }

    const descontoPct = parseFloat(document.getElementById('desconto').value) || 0;
    const subtotal = itens.reduce((s, i) => s + i.preco_venda * i.quantidade, 0);
    const desconto = parseFloat((subtotal * descontoPct / 100).toFixed(2));
    const total    = Math.max(0, subtotal - desconto);
    const pagamento = document.getElementById('forma-pagamento').value;
    const cliente   = document.getElementById('cliente-nome').value.trim();

    const venda = {
        cliente_nome:    cliente || 'Consumidor final',
        total:           parseFloat(total.toFixed(2)),
        subtotal:        parseFloat(subtotal.toFixed(2)),
        desconto:        parseFloat(desconto.toFixed(2)),
        forma_pagamento: pagamento,
        status:          'concluida',
        itens: itens.map(i => ({
            produto_id:   i.id,
            nome_produto: i.nome,
            quantidade:   i.quantidade,
            preco_unit:   i.preco_venda,
            preco_custo:  i.preco_custo,
            subtotal:     parseFloat((i.preco_venda * i.quantidade).toFixed(2)),
            unidade:      i.unidade,
        }))
    };

    try {
        const res  = await fetch(`${API}/vendas/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(venda),
        });
        const json = await res.json();
        if (!res.ok) { alert('Erro: ' + (json.erro || 'Falha ao finalizar.')); return; }
        alert('Venda finalizada com sucesso!');
        limparVenda();
        carregarMetricas();
    } catch (e) {
        alert('Erro de conexao com a API.');
        console.error(e);
    }
}

function limparVenda() {
    itens = [];
    document.getElementById('desconto').value     = 0;
    document.getElementById('cliente-nome').value = '';
    document.getElementById('forma-pagamento').value = 'dinheiro';
    renderItens();
}

async function buscarCliente(termo) {
    try {
        const res  = await fetch(`${API}/clientes/?status=ativo`);
        const json = await res.json();
        const lista = (json.data || []).filter(c =>
            c.nome.toLowerCase().includes(termo.toLowerCase()) ||
            (c.cpf || '').includes(termo) ||
            (c.telefone || '').includes(termo)
        );
        const el = document.getElementById('resultados-cliente');
        if (lista.length === 0) {
            el.innerHTML = '<div style="padding:10px 14px;font-size:13px;color:#888;">Nenhum cliente encontrado.</div>';
            el.style.display = 'block';
            return;
        }
        el.innerHTML = lista.slice(0, 8).map(c => `
            <div onclick="selecionarCliente('${c.id}', '${c.nome.replace(/'/g, '')}')"
                 style="padding:10px 14px;cursor:pointer;border-bottom:0.5px solid #f0f0f0;font-size:13px;"
                 onmouseover="this.style.background='#fef6f6'" onmouseout="this.style.background=''">
                <div style="font-weight:600;color:#111;">${c.nome}</div>
                <div style="font-size:11px;color:#888;">${c.cpf || ''} ${c.telefone ? '| ' + c.telefone : ''}</div>
            </div>`).join('');
        el.style.display = 'block';
    } catch (e) { console.error(e); }
}

function selecionarCliente(id, nome) {
    document.getElementById('cliente-id').value   = id;
    document.getElementById('cliente-nome').value = nome;
    document.getElementById('resultados-cliente').style.display = 'none';
}

function fmt(v) {
    return parseFloat(v || 0).toFixed(2).replace('.', ',');
}
