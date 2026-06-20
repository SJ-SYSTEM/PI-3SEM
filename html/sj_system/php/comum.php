<?php
function sidebar($paginaAtiva = '') {
    $paginas = [
        'dashboard' => ['href' => 'dashboard.php', 'icon' => '🏠', 'label' => 'PDV'],
        'produtos'  => ['href' => 'produtos.php',  'icon' => '💊', 'label' => 'Produtos'],
        'clientes'  => ['href' => 'clientes.php',  'icon' => '👥', 'label' => 'Clientes'],
        'vendas'    => ['href' => 'vendas.php',    'icon' => '🛒', 'label' => 'Vendas'],
    ];

    // Detecta página ativa automaticamente se não for passada
    if (!$paginaAtiva) {
        $script = basename($_SERVER['PHP_SELF'], '.php');
        $paginaAtiva = $script;
    }

    $usuario = $_SESSION['user'] ?? 'Usuário';
    $inicial = strtoupper(substr($usuario, 0, 1));

    $html = '
    <div class="sidebar">
        <!-- Header -->
        <div class="sidebar-header">
            <div class="logo-circle">+</div>
            <div>
                <h4>SJ System</h4>
                <small>Farmácia de Bairro</small>
            </div>
        </div>

        <!-- Menu -->
        <div class="sidebar-menu">
            <div class="sidebar-section">Menu</div>';

    foreach ($paginas as $key => $pagina) {
        $active = ($paginaAtiva === $key || strpos($_SERVER['PHP_SELF'], $key) !== false)
            ? 'active' : '';
        $html .= "
            <a href='{$pagina['href']}' class='{$active}'>
                <span class='icon'>{$pagina['icon']}</span>
                {$pagina['label']}
            </a>";
    }

    $html .= "
        </div>

        <!-- Footer -->
        <div class='sidebar-footer'>
            <div style='padding: 8px 12px; margin-bottom: 8px; font-size:13px; color:#888;'>
                <div style='display:flex; align-items:center; gap:10px;'>
                    <div style='width:32px; height:32px; background:var(--color5); border-radius:50%;
                                display:flex; align-items:center; justify-content:center;
                                color:white; font-weight:bold;'>{$inicial}</div>
                    <div>
                        <div style='font-weight:bold; color:#333;'>{$usuario}</div>
                        <div style='font-size:11px;'>Operador</div>
                    </div>
                </div>
            </div>
            <a href='/php/POST_logoff.php'>
                <span class='icon'>🚪</span> Sair
            </a>
        </div>
    </div>";

    return $html;
}

function topbar($titulo = 'Dashboard') {
    $usuario = $_SESSION['user'] ?? 'Usuário';
    $inicial = strtoupper(substr($usuario, 0, 1));
    $data    = date('d/m/Y');

    return "
    <div class='topbar'>
        <div class='topbar-title'>{$titulo}</div>
        <div class='topbar-user'>
            <span style='color:#888; font-size:13px;'>{$data}</span>
            <div class='avatar'>{$inicial}</div>
            <span>{$usuario}</span>
        </div>
    </div>";
}
?>
