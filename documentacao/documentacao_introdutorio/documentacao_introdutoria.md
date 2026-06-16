## SJ System
#### Documentacao de Estrutura de Pastas, Arquivos e Banco de Dados

Este documento descreve cada pasta e arquivo do projeto SJ System, indicando sua camada (back-end, front-end ou banco de dados), sua funcao e como se relaciona com os demais componentes.

![imagem - camadas da aplicacao](imagens_intro/camadas-doc.png)

## Raizes do Servidor - /var/www/
![imagem - raiz do servidor](imagens_intro/raiz-do-servidor.png)

### Por que o venv e importante?
O servidor usa Python 3.6.8 do sistema. O venv garante que as versoes corretas das bibliotecas sejam usadas sem interferir em outros projetos. Sempre ativar antes de rodar o Django.

<hr>

### Back-end Django — /var/www/html/

API REST construida com Django 3.2. Nao serve HTML - apenas recebe requisicoes HTTP do front-end e retorna JSON. Usa MongoEngine como ODM e pymongo para as aggregation pipelines dos relatorios.

![imagem das rotas/requisicoes](imagens_intro/requisicoes.png)
