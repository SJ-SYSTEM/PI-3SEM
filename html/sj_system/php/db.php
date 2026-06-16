<?php

$conn = new mysqli("127.0.0.1", 'root', 'kz14wdsy', 'sj_system');

if ($conn->connect_error) {
    die("Erro banco: " . $conn->connect_error);
}
?>
