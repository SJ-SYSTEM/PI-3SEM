
<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
?>



<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Login - Sistema de Farmáa</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Seu CSS -->
    <link rel="stylesheet" href="css/style.css">
</head>
<body>

<div class="login-bg">

    <div class="shape-top"></div>
    <div class="shape-bottom"></div>

    <div class="login-card">

        <div class="logo-area">
            <div class="logo-circle">+</div>

            <h2>Bem-vindo</h2>

            <p class="text-muted">
                Acesse sua conta para continuar
            </p>
        </div>
	
<?php
$erro = '';

if (isset($_GET['erro'])) {
    $erro = "Usuario ou Senha invalidos";
}
?>

        <!-- ERRO -->
        <?php if ($erro): ?>
            <div class="alert alert-danger text-center">
                <?= $erro ?>
            </div>
        <?php endif; ?>

        <!-- FORM -->
        <form method="POST" action="php/POST_login.php">

            <div class="mb-3">
                <label class="form-label">
                    Email
                </label>

                <input
                    type="text"
                    name="email"
                    class="form-control"
                    placeholder="Digite seu usuario"
                    required
                >
            </div>

            <div class="mb-3">
                <label class="form-label">
                    Senha
                </label>

                <input
                    type="password"
                    name="senha"
                    class="form-control"
                    placeholder="Digite sua senha"
                    required
                >
            </div>

            <div class="d-flex justify-content-between align-items-center mb-4">

                <div class="form-check">
                    <input class="form-check-input" type="checkbox" name="lembrar">
                    <label class="form-check-label">
                        Lembrar-me
                    </label>
                </div>

                <a href="#" class="link-red">
                    Esqueceu a senha?
                </a>

            </div>

            <button type="submit" class="btn btn-login w-100">
                Entrar
            </button>
            


        </form>


<a href="cadastro.php" class="btn btn-cadastro w-100 mt-3">
    Criar Conta
</a>

</div>
    </div>

    <div class="footer-text">
        2026 Sistema de Farmacia
    </div>

</div>

</body>
</html>
