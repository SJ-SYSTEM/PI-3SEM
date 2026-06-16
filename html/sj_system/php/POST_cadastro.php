<?php
require 'db.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $nome     = $_POST['nome'] ?? '';
    $usuario  = $_POST['usuario'] ?? '';
    $email    = $_POST['email'] ?? '';
    $senha    = $_POST['senha'] ?? '';

    $hash = password_hash($senha, PASSWORD_DEFAULT);

    $stmt = $conn->prepare("INSERT INTO usuario (nome, usuario, email, senha) VALUES (?, ?, ?, ?)");
    $stmt->bind_param("ssss", $nome, $usuario, $email, $hash);
	
if ($stmt->execute()) {
    header("Location: ../login.php?status=sucesso");
    exit;
} else {
    header("Location: ../cadastro.php?status=erro");
    exit;
}
}

?>
