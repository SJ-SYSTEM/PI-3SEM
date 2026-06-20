const API      = "http://144.22.150.83:8000/api/relatorios";
const LABEL_PAG = { dinheiro:"Dinheiro", pix:"PIX", cartao_debito:"Debito", cartao_credito:"Credito", convenio:"Convenio" };
const COR_PAG   = { dinheiro:"#c40000",  pix:"#198754", cartao_debito:"#0d6efd", cartao_credito:"#c07800", convenio:"#5b3da8" };
let chartsInstancias = {};
let ordemAtual = { campo: "id", asc: false };
let VENDAS_LOCAL = [];

document.addEventListener("DOMContentLoaded", async () => {
    const hoje = new Date();
    const ini  = new Date(hoje.getFullYear(), hoje.getMonth(), 1).toISOString().slice(0, 10);
    const fim  = hoje.toISOString().slice(0, 10);
    document.getElementById("f-de").value  = ini;
    document.getElementById("f-ate").value = fim;
    await carregarTudo();
});

function params() {
    const de     = document.getElementById("f-de").value;
    const ate    = document.getElementById("f-ate").value;
    const status = document.getElementById("f-status").value;
    const busca  = document.getElementById("f-busca").value.trim();
    const p = new URLSearchParams();
    if (de)     p.set("de",     de);
    if (ate)    p.set("ate",    ate);
    if (status) p.set("status", status);
    if (busca)  p.set("produto",busca);
    return p.toString();
}

async function carregarTudo() {
    const q = params();
    try {
        const [kpis, fatDia, bi, vendas, prodVend] = await Promise.all([
            fetch(`${API}/kpis/?${q}`).then(r => r.json()),
            fetch(`${API}/faturamento-por-dia/?${q}`).then(r => r.json()),
            fetch(`${API}/bi/?meses=6`).then(r => r.json()),
            fetch(`http://144.22.150.83:8000/api/vendas/`).then(r => r.json()),
            fetch(`${API}/produtos-mais-vendidos/?${q}&limite=8`).then(r => r.json()),
        ]);
        renderKpis(kpis);
        renderGraficoFat(fatDia);
        renderGraficoMensal(bi.mensal);
        renderGraficoQtdMes(fatDia);
        renderGraficoTicket(bi.mensal);
        renderGraficoHora(bi.por_hora);
        renderGraficoCategoria(bi.por_categoria);
        renderGraficoProdutos(prodVend);
        renderTopProdutos(prodVend);

        VENDAS_LOCAL = vendas.data || [];
        renderTabela(filtrarLocal(VENDAS_LOCAL));
        renderGraficoDonut(VENDAS_LOCAL);
        renderGraficosPeriodo(fatDia, VENDAS_LOCAL);
        renderGraficosPeriodo(fatDia, VENDAS_LOCAL);
    } catch(e) {
        console.error('ERRO carregarTudo:', e);
        alert('Erro: ' + e.message);
    }
}

async function aplicarFiltros() { await carregarTudo(); }

function limparFiltros() {
    const hoje = new Date();
    document.getElementById("f-de").value     = new Date(hoje.getFullYear(), hoje.getMonth(), 1).toISOString().slice(0,10);
    document.getElementById("f-ate").value    = hoje.toISOString().slice(0,10);
    document.getElementById("f-status").value = "";
    document.getElementById("f-pag").value    = "";
    document.getElementById("f-busca").value  = "";
    carregarTudo();
}

function filtrarLocal(lista) {
    const status = document.getElementById("f-status").value;
    const pag    = document.getElementById("f-pag").value;
    const busca  = document.getElementById("f-busca").value.trim().toLowerCase();
    const de     = document.getElementById("f-de").value;
    const ate    = document.getElementById("f-ate").value;
    return lista.filter(v => {
        if (status && v.status !== status) return false;
        if (pag    && v.forma_pagamento !== pag) return false;
        if (de     && v.criado.slice(0,10) < de)  return false;
        if (ate    && v.criado.slice(0,10) > ate)  return false;
        if (busca) {
            const itensNome = (v.itens||[]).map(i=>i.nome_produto||'').join(' ').toLowerCase();
            if (!v.cliente_nome.toLowerCase().includes(busca) && !itensNome.includes(busca)) return false;
        }
        return true;
    });
}

function renderKpis(k) {
    const margem = k.faturamento > 0 ? ((k.lucro / k.faturamento)*100).toFixed(1) : 0;
    document.getElementById("kpis-row").innerHTML = `
        <div class="col-6 col-md-2 mb-2"><div class="card-kpi"><div class="kpi-val">R$ ${fmt(k.faturamento)}</div><div class="kpi-lab">Faturamento</div></div></div>
        <div class="col-6 col-md-2 mb-2"><div class="card-kpi"><div class="kpi-val" style="color:#198754;">R$ ${fmt(k.lucro)}</div><div class="kpi-lab">Lucro <small style="color:#198754;">${margem}% margem</small></div></div></div>
        <div class="col-6 col-md-2 mb-2"><div class="card-kpi"><div class="kpi-val">R$ ${fmt(k.ticket_medio)}</div><div class="kpi-lab">Ticket medio</div></div></div>
        <div class="col-6 col-md-2 mb-2"><div class="card-kpi"><div class="kpi-val">${k.total_vendas}</div><div class="kpi-lab">Vendas concluidas</div></div></div>
        <div class="col-6 col-md-2 mb-2"><div class="card-kpi"><div class="kpi-val" style="color:#c40000;">${k.cancelamentos}</div><div class="kpi-lab">Cancelamentos</div></div></div>
        <div class="col-6 col-md-2 mb-2"><div class="card-kpi"><div class="kpi-val" style="color:#c07800;">${k.pendentes}</div><div class="kpi-lab">Pendentes</div></div></div>
    `;
}

function criarOuAtualizar(id, tipo, data, options={}) {
    if (chartsInstancias[id]) chartsInstancias[id].destroy();
    const ctx = document.getElementById(id);
    if (!ctx) return;
    chartsInstancias[id] = new Chart(ctx, { type: tipo, data, options: { responsive:true, plugins:{legend:{display:false}}, ...options }});
}

function renderGraficoDonut(vendas) {
    const contagem = {};
    (vendas || []).filter(v => v.status === 'concluida').forEach(v => {
        const p = LABEL_PAG[v.forma_pagamento] || v.forma_pagamento;
        contagem[p] = (contagem[p] || 0) + 1;
    });
    const labels = Object.keys(contagem);
    const data   = Object.values(contagem);
    const cores  = labels.map(l => {
        const k = Object.keys(LABEL_PAG).find(k => LABEL_PAG[k] === l);
        return COR_PAG[k] || '#888';
    });
    criarOuAtualizar('chart-donut', 'doughnut', {
        labels,
        datasets: [{ data, backgroundColor: cores, borderWidth: 2 }]
    }, {
        cutout: '60%',
        plugins: { legend: { display: true, position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } }
    });
}


function renderGraficosPeriodo(fatDia, vendas) {
    const de  = document.getElementById("f-de").value;
    const ate = document.getElementById("f-ate").value;

    // Filtra por periodo
    const dadosFiltrados = fatDia.filter(d => {
        if (de  && d.data < de)  return false;
        if (ate && d.data > ate) return false;
        return true;
    });

    // Grafico 1: Vendas realizadas (faturamento por dia)
    criarOuAtualizar('chart-vendas-periodo', 'line', {
        labels: dadosFiltrados.map(d => d.data.slice(5)),
        datasets: [{
            label: 'Faturamento',
            data: dadosFiltrados.map(d => d.faturamento),
            borderColor: '#c40000',
            backgroundColor: 'rgba(196,0,0,.08)',
            fill: true, tension: .4, pointRadius: 2
        }, {
            label: 'Lucro',
            data: dadosFiltrados.map(d => d.lucro),
            borderColor: '#198754',
            backgroundColor: 'rgba(25,135,84,.05)',
            fill: true, tension: .4, pointRadius: 2, borderDash: [5,3]
        }]
    }, {
        plugins: { legend: { display: true, position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } }
    });

    // Grafico 2: Saida de estoque por dia (soma das quantidades vendidas)
    const saidaPorDia = {};
    vendas.filter(v => {
        if (v.status !== 'concluida') return false;
        const d = v.criado.slice(0,10);
        if (de  && d < de)  return false;
        if (ate && d > ate) return false;
        return true;
    }).forEach(v => {
        const dia = v.criado.slice(0,10).slice(5);
        const qtd = (v.itens || []).reduce((s, i) => s + i.quantidade, 0);
        saidaPorDia[dia] = (saidaPorDia[dia] || 0) + qtd;
    });

    const diasOrdenados = Object.keys(saidaPorDia).sort();
    criarOuAtualizar('chart-estoque-periodo', 'bar', {
        labels: diasOrdenados,
        datasets: [{
            label: 'Unidades saidas',
            data: diasOrdenados.map(d => saidaPorDia[d]),
            backgroundColor: 'rgba(196,0,0,.7)',
            borderRadius: 3
        }]
    }, {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
    });
}


function renderGraficosPeriodo(fatDia, vendas) {
    const de  = document.getElementById("f-de").value;
    const ate = document.getElementById("f-ate").value;

    // Filtra por periodo
    const dadosFiltrados = fatDia.filter(d => {
        if (de  && d.data < de)  return false;
        if (ate && d.data > ate) return false;
        return true;
    });

    // Grafico 1: Vendas realizadas (faturamento por dia)
    criarOuAtualizar('chart-vendas-periodo', 'line', {
        labels: dadosFiltrados.map(d => d.data.slice(5)),
        datasets: [{
            label: 'Faturamento',
            data: dadosFiltrados.map(d => d.faturamento),
            borderColor: '#c40000',
            backgroundColor: 'rgba(196,0,0,.08)',
            fill: true, tension: .4, pointRadius: 2
        }, {
            label: 'Lucro',
            data: dadosFiltrados.map(d => d.lucro),
            borderColor: '#198754',
            backgroundColor: 'rgba(25,135,84,.05)',
            fill: true, tension: .4, pointRadius: 2, borderDash: [5,3]
        }]
    }, {
        plugins: { legend: { display: true, position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } }
    });

    // Grafico 2: Saida de estoque por dia (soma das quantidades vendidas)
    const saidaPorDia = {};
    vendas.filter(v => {
        if (v.status !== 'concluida') return false;
        const d = v.criado.slice(0,10);
        if (de  && d < de)  return false;
        if (ate && d > ate) return false;
        return true;
    }).forEach(v => {
        const dia = v.criado.slice(0,10).slice(5);
        const qtd = (v.itens || []).reduce((s, i) => s + i.quantidade, 0);
        saidaPorDia[dia] = (saidaPorDia[dia] || 0) + qtd;
    });

    const diasOrdenados = Object.keys(saidaPorDia).sort();
    criarOuAtualizar('chart-estoque-periodo', 'bar', {
        labels: diasOrdenados,
        datasets: [{
            label: 'Unidades saidas',
            data: diasOrdenados.map(d => saidaPorDia[d]),
            backgroundColor: 'rgba(196,0,0,.7)',
            borderRadius: 3
        }]
    }, {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
    });
}


function renderTopProdutos(dados) {
    if (!dados || dados.length === 0) return;
    criarOuAtualizar('chart-top-produtos', 'bar', {
        labels: dados.map(d => d.nome.length > 25 ? d.nome.slice(0,23)+'...' : d.nome),
        datasets: [{
            label: 'Unidades vendidas',
            data: dados.map(d => d.qtd),
            backgroundColor: dados.map((_,i) => i === 0 ? '#c40000' : 'rgba(196,0,0,.6)'),
            borderRadius: 4,
        }]
    }, {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } }
    });
}

function renderGraficoFat(dados) {
    const labels = dados.map(d => d.data.slice(5));
    criarOuAtualizar('chart-fat', 'line', {
        labels,
        datasets: [
            { label:'Faturamento', data: dados.map(d=>d.faturamento), borderColor:'#c40000', backgroundColor:'rgba(196,0,0,.08)', fill:true, tension:.4, pointRadius:2 },
            { label:'Lucro',       data: dados.map(d=>d.lucro),       borderColor:'#198754', backgroundColor:'rgba(25,135,84,.05)', fill:true, tension:.4, pointRadius:2, borderDash:[5,3] },
        ]
    }, { plugins:{ legend:{ display:true, position:'top', labels:{ boxWidth:12, font:{size:11} } } } });
}

function renderGraficoMensal(dados) {
    criarOuAtualizar('chart-men', 'bar', {
        labels: dados.map(d => d.mes),
        datasets: [
            { label:'Faturamento', data: dados.map(d=>d.faturamento), backgroundColor:'rgba(196,0,0,.7)', borderRadius:4 },
            { label:'Lucro',       data: dados.map(d=>d.lucro),       backgroundColor:'rgba(25,135,84,.7)', borderRadius:4 },
        ]
    }, { plugins:{ legend:{ display:true, position:'top', labels:{ boxWidth:12, font:{size:11} } } } });
}

function renderGraficoQtdMes(dados) {
    criarOuAtualizar('chart-qtd-mes', 'bar', {
        labels: dados.map(d => d.mes),
        datasets: [
            { label:'Vendas concluidas', data: dados.map(d=>d.quantidade),    backgroundColor:'rgba(196,0,0,.7)', borderRadius:4 },
            { label:'Cancelamentos',     data: dados.map(d=>d.cancelamentos),  backgroundColor:'rgba(200,120,0,.6)', borderRadius:4 },
        ]
    }, {
        plugins:{ legend:{ display:true, position:'top', labels:{ boxWidth:12, font:{size:11} } } },
        scales:{ y:{ beginAtZero:true, ticks:{ stepSize:1 } } }
    });
}

function renderGraficoTicket(dados) {
    criarOuAtualizar('chart-ticket', 'line', {
        labels: dados.map(d => d.mes),
        datasets: [{
            label:'Ticket medio', data: dados.map(d=>d.ticket),
            borderColor:'#5b3da8', backgroundColor:'rgba(91,61,168,.08)',
            fill:true, tension:.4, pointRadius:4, pointBackgroundColor:'#5b3da8'
        }]
    }, { plugins:{ legend:{ display:false } }, scales:{ y:{ beginAtZero:false } } });
}

function renderGraficoHora(dados) {
    const horas = Array.from({length:24}, (_,i) => i);
    const qtd   = horas.map(h => { const d = dados.find(x=>x.hora===h); return d ? d.quantidade : 0; });
    criarOuAtualizar('chart-hora', 'bar', {
        labels: horas.map(h => h + 'h'),
        datasets: [{ label:'Vendas', data: qtd, backgroundColor: qtd.map(v => v === Math.max(...qtd) ? '#c40000' : 'rgba(196,0,0,.35)'), borderRadius:3 }]
    }, { plugins:{ legend:{ display:false } }, scales:{ y:{ beginAtZero:true, ticks:{ stepSize:1 } } } });
}

function renderGraficoCategoria(dados) {
    const cores = ['#c40000','#198754','#0d6efd','#c07800','#5b3da8','#0dcaf0'];
    criarOuAtualizar('chart-categoria', 'doughnut', {
        labels: dados.map(d => d.categoria),
        datasets: [{ data: dados.map(d=>d.total), backgroundColor: cores.slice(0, dados.length), borderWidth:2 }]
    }, { plugins:{ legend:{ display:true, position:'right', labels:{ boxWidth:12, font:{size:11} } } }, cutout:'60%' });
}

function renderGraficoProdutos(dados) {
    criarOuAtualizar('chart-prod', 'bar', {
        labels: dados.map(d => d.nome.length > 20 ? d.nome.slice(0,18)+'…' : d.nome),
        datasets: [{ label:'Qtd', data: dados.map(d=>d.qtd), backgroundColor:'rgba(196,0,0,.7)', borderRadius:4 }]
    }, { indexAxis:'y', plugins:{ legend:{ display:false } }, scales:{ x:{ beginAtZero:true } } });
}

function renderTabela(lista) {
    const filtPag = document.getElementById("f-pag").value;
    const exibir  = filtPag ? lista.filter(v => v.forma_pagamento === filtPag) : lista;
    const total   = exibir.reduce((s,v)=>s+(v.status==='concluida'?v.total:0), 0);

    document.getElementById("info-registros").textContent      = exibir.length + " venda(s) no periodo";
    document.getElementById("info-total-registros").textContent = exibir.length + " registros";
    document.getElementById("total-filtrado").textContent       = exibir.length ? "Total: R$ " + fmt(total) : "";

    if (!exibir.length) {
        document.getElementById("tbody-vendas").innerHTML = '<tr><td colspan="8" class="text-muted text-center py-3">Nenhuma venda encontrada.</td></tr>';
        return;
    }

    document.getElementById("tbody-vendas").innerHTML = exibir.map(v => {
        const itensStr = (v.itens||[]).slice(0,2).map(i => `${i.nome_produto} x${i.quantidade}`).join(', ') + ((v.itens||[]).length > 2 ? '…' : '');
        const badge    = v.status === 'concluida' ? 'success' : v.status === 'cancelada' ? 'danger' : 'warning';
        const pag      = LABEL_PAG[v.forma_pagamento] || v.forma_pagamento;
        return `<tr>
            <td><span class="fw-bold text-muted">#${(v.id||"-").slice(-6)}</span></td>
            <td>${fmtData(v.criado)}</td>
            <td><strong>${v.cliente_nome||"—"}</strong><br><small class="text-muted">${itensStr}</small></td>
            <td>${(v.itens||[]).length} itens</td>
            <td class="fw-bold">R$ ${fmt(v.total)}</td>
            <td><span class="badge" style="background:${COR_PAG[v.forma_pagamento]||'#888'};font-size:11px;">${pag}</span></td>
            <td><span class="badge bg-${badge}">${v.status}</span></td>
            <td class="no-print"><button class="btn btn-sm btn-outline-secondary" onclick="verDetalhe('${v.id}')">Ver</button></td>
        </tr>`;
    }).join('');
}

function ordenarPor(campo) {
    if (ordemAtual.campo === campo) ordemAtual.asc = !ordemAtual.asc;
    else { ordemAtual.campo = campo; ordemAtual.asc = false; }
    const sorted = [...filtrarLocal(VENDAS_LOCAL)].sort((a,b) => {
        let va = campo === 'total' ? a.total : (campo === 'data' ? a.criado : a.id);
        let vb = campo === 'total' ? b.total : (campo === 'data' ? b.criado : b.id);
        return ordemAtual.asc ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1);
    });
    renderTabela(sorted);
}

async function verDetalhe(id) {
    try {
        const v = await fetch(`http://144.22.150.83:8000/api/vendas/${id}/`).then(r=>r.json());
        const itensHtml = (v.itens||[]).map(i => `
            <tr>
                <td>${i.nome_produto}</td>
                <td class="text-center">${i.quantidade}</td>
                <td class="text-end">R$ ${fmt(i.preco_unit)}</td>
                <td class="text-end fw-bold">R$ ${fmt(i.subtotal)}</td>
            </tr>`).join('');
        document.getElementById("detalhe-body").innerHTML = `
            <div class="row mb-3">
                <div class="col-6"><small class="text-muted">Cliente</small><div class="fw-bold">${v.cliente_nome||'—'}</div></div>
                <div class="col-3"><small class="text-muted">Data</small><div>${fmtData(v.criado)}</div></div>
                <div class="col-3"><small class="text-muted">Status</small><div><span class="badge bg-${v.status==='concluida'?'success':v.status==='cancelada'?'danger':'warning'}">${v.status}</span></div></div>
            </div>
            <table class="table table-sm"><thead><tr><th>Produto</th><th class="text-center">Qtd</th><th class="text-end">Preco unit</th><th class="text-end">Subtotal</th></tr></thead><tbody>${itensHtml}</tbody></table>
            <div class="d-flex justify-content-end gap-4 mt-2">
                <span>Subtotal: <strong>R$ ${fmt(v.subtotal||v.total)}</strong></span>
                <span>Desconto: <strong>R$ ${fmt(v.desconto||0)}</strong></span>
                <span style="color:#c40000;">Total: <strong>R$ ${fmt(v.total)}</strong></span>
            </div>
            <div class="mt-2 text-muted" style="font-size:12px;">Pagamento: ${LABEL_PAG[v.forma_pagamento]||v.forma_pagamento}</div>`;
        new bootstrap.Modal(document.getElementById('modalDetalhe')).show();
    } catch(e) { alert('Erro ao carregar detalhes.'); }
}


function fmt(v) { return parseFloat(v||0).toFixed(2).replace('.',','); }
function fmtData(d) {
    if (!d) return '—';
    const dt = new Date(d);
    return dt.toLocaleDateString('pt-BR') + ' ' + dt.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
}
