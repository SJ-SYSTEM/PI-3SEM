const API_CLI = "http://144.22.150.83:8000/api";

let clienteParaExcluir = null;
let idEditando = null;
let CLIENTES = [];
let modalExcluir;

document.addEventListener('DOMContentLoaded', () => {
    modalExcluir = new bootstrap.Modal(document.getElementById('modalExcluir'));

    document.getElementById('busca-cliente').addEventListener('keypress', e => {
        if (e.key === 'Enter') buscarCliente();
    });

    aplicarMascaras();
    carregarClientes();
});

function aplicarMascaras() {
    document.getElementById('campo-documento').addEventListener('input', function () {
        let v = this.value.replace(/\D/g, '');
        if (v.length <= 11) {
            v = v.replace(/(\d{3})(\d)/, '$1.$2')
                 .replace(/(\d{3})(\d)/, '$1.$2')
                 .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        } else {
            v = v.replace(/^(\d{2})(\d)/, '$1.$2')
                 .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
                 .replace(/\.(\d{3})(\d)/, '.$1/$2')
                 .replace(/(\d{4})(\d)/, '$1-$2');
        }
        this.value = v;
    });

    document.getElementById('campo-telefone').addEventListener('input', function () {
        let v = this.value.replace(/\D/g, '');
        if (v.length <= 10) {
            v = v.replace(/(\d{2})(\d)/, '($1) $2').replace(/(\d{4})(\d)/, '$1-$2');
        } else {
            v = v.replace(/(\d{2})(\d)/, '($1) $2').replace(/(\d{5})(\d)/, '$1-$2');
        }
        this.value = v;
    });
}

async function carregarClientes(status = '') {
    try {
        const url = `${API_CLI}/clientes/`;
        const res  = await fetch(url);
        const json = await res.json();
        CLIENTES = json.data || [];
        renderClientes(CLIENTES);
        atualizarMetricas(CLIENTES);
    } catch (e) {
        document.getElementById('lista-clientes').innerHTML =
            '<p class="text-danger text-center py-3">Erro ao carregar clientes. Verifique a API.</p>';
        console.error(e);
    }
}

function filtrarClientes() {
    const termo = document.getElementById('busca-cliente').value.trim().toLowerCase();
    const status = document.getElementById('filtro-status-cliente').value;
    if (!termo && !status) { renderClientes(CLIENTES); return; }
    const filtrados = CLIENTES.filter(c => {
        if (status && c.status !== status) return false;
        return true;
    }).filter(c =>
        c.nome.toLowerCase().includes(termo) ||
        (c.cpf      || '').toLowerCase().includes(termo) ||
        (c.telefone || '').toLowerCase().includes(termo) ||
        (c.email    || '').toLowerCase().includes(termo)
    );
    renderClientes(filtrados);
}

function limparFiltroClientes() {
    document.getElementById('busca-cliente').value = '';
    document.getElementById('filtro-status-cliente').value = '';
    renderClientes(CLIENTES);
}

function renderClientes(lista) {
    const el = document.getElementById('lista-clientes');

    if (!lista || lista.length === 0) {
        el.innerHTML = '<p class="text-muted text-center py-3">Nenhum cliente encontrado.</p>';
        return;
    }

    el.innerHTML = lista.map(c => `
        <div class="produto" style="flex-wrap:wrap; gap:6px;">
            <div style="flex:1; min-width:0;">
                <span class="nome">${c.nome}</span>
                <br>
                <small class="text-muted">
                    ${c.cpf      ? '📄 ' + c.cpf      + ' &nbsp;' : ''}
                    ${c.telefone ? '📞 ' + c.telefone  + ' &nbsp;' : ''}
                    ${c.email    ? '✉️ '  + c.email                : ''}
                    ${c.endereco ? '<br>📍 ' + c.endereco          : ''}
                </small>
            </div>
            <div class="d-flex align-items-center gap-2">
                <span class="badge ${c.status === 'ativo' ? 'bg-success' : 'bg-secondary'}">
                    ${c.status === 'ativo' ? 'Ativo' : 'Inativo'}
                </span>
                <button class="btn btn-sm btn-outline-secondary" onclick="editarCliente('${c.id}')" title="Editar">✏️</button>
                <button class="btn btn-sm" style="color:#c40000;" onclick="pedirExclusao('${c.id}', '${escapeHtml(c.nome)}')" title="Excluir">✕</button>
            </div>
        </div>
    `).join('');
}

function atualizarMetricas(lista) {
    const agora    = new Date();
    const mes      = agora.getMonth();
    const ano      = agora.getFullYear();
    const ativos   = lista.filter(c => c.status === 'ativo').length;
    const inativos = lista.filter(c => c.status === 'inativo').length;
    const novos    = lista.filter(c => {
        if (!c.criado) return false;
        const d = new Date(c.criado);
        return d.getMonth() === mes && d.getFullYear() === ano;
    }).length;

    document.getElementById('metric-total').textContent    = lista.length;
    document.getElementById('metric-ativos').textContent   = ativos;
    document.getElementById('metric-inativos').textContent = inativos;
    document.getElementById('metric-novos').textContent    = novos;
}

async function salvarCliente() {
    const nome = document.getElementById('campo-nome').value.trim();
    if (!nome) { alert('O nome do cliente é obrigatório.'); return; }

    const payload = {
        nome,
        cpf:      document.getElementById('campo-documento').value.trim(),
        telefone: document.getElementById('campo-telefone').value.trim(),
        email:    document.getElementById('campo-email').value.trim(),
        endereco: document.getElementById('campo-endereco').value.trim(),
        status:   document.getElementById('campo-status').value,
    };

    const url    = idEditando ? `${API_CLI}/clientes/${idEditando}/` : `${API_CLI}/clientes/`;
    const method = idEditando ? 'PUT' : 'POST';

    try {
        const res  = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload),
        });
        const json = await res.json();
        if (!res.ok) { alert('Erro: ' + (json.erro || 'Falha ao salvar.')); return; }
        alert(idEditando ? 'Cliente atualizado com sucesso!' : 'Cliente cadastrado com sucesso!');
        limparFormulario();
        carregarClientes();
    } catch (e) {
        alert('Erro de conexão com a API.');
        console.error(e);
    }
}

async function editarCliente(id) {
    try {
        const res = await fetch(`${API_CLI}/clientes/${id}/`);
        const c   = await res.json();
        idEditando = id;
        document.getElementById('modal-cliente-id').value = c.id       || '';
        document.getElementById('modal-nome').value       = c.nome     || '';
        document.getElementById('modal-cpf').value        = c.cpf      || '';
        document.getElementById('modal-telefone').value   = c.telefone || '';
        document.getElementById('modal-email').value      = c.email    || '';
        document.getElementById('modal-endereco').value   = c.endereco || '';
        document.getElementById('modal-status').value     = c.status   || 'ativo';
        new bootstrap.Modal(document.getElementById('modalEditar')).show();
    } catch (e) {
        alert('Erro ao carregar dados do cliente.');
        console.error(e);
    }
}

async function salvarEdicaoCliente() {
    const nome = document.getElementById('modal-nome').value.trim();
    if (!nome) { alert('O nome e obrigatorio.'); return; }

    const payload = {
        nome,
        cpf:      document.getElementById('modal-cpf').value.trim(),
        telefone: document.getElementById('modal-telefone').value.trim(),
        email:    document.getElementById('modal-email').value.trim(),
        endereco: document.getElementById('modal-endereco').value.trim(),
        status:   document.getElementById('modal-status').value,
    };

    try {
        const res  = await fetch(`${API_CLI}/clientes/${idEditando}/`, {
            method:  'PUT',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload),
        });
        const json = await res.json();
        if (!res.ok) { alert('Erro: ' + (json.erro || 'Falha ao atualizar.')); return; }
        bootstrap.Modal.getInstance(document.getElementById('modalEditar')).hide();
        idEditando = null;
        carregarClientes();
    } catch (e) {
        alert('Erro de conexao com a API.');
        console.error(e);
    }
}

function pedirExclusao(id, nome) {
    clienteParaExcluir = id;
    document.getElementById('modal-nome-cliente').textContent = nome;
    modalExcluir.show();
}

async function confirmarExclusao() {
    try {
        const res = await fetch(`${API_CLI}/clientes/${clienteParaExcluir}/`, { method: 'DELETE' });
        if (!res.ok) { alert('Erro ao excluir cliente.'); return; }
        clienteParaExcluir = null;
        modalExcluir.hide();
        carregarClientes();
    } catch (e) {
        alert('Erro de conexão com a API.');
        console.error(e);
    }
}

function limparFormulario() {
    idEditando = null;
    document.getElementById('cliente-id').value        = '';
    document.getElementById('campo-nome').value        = '';
    document.getElementById('campo-documento').value   = '';
    document.getElementById('campo-telefone').value    = '';
    document.getElementById('campo-email').value       = '';
    document.getElementById('campo-endereco').value    = '';
    document.getElementById('campo-status').value      = 'ativo';
    document.getElementById('form-titulo').textContent = 'Novo cliente';
}

function escapeHtml(str) {
    return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
