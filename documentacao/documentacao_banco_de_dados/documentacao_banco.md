# SJ System — Diagrama do Banco de Dados
## (MongoDB)

![Diagrama do banco](imagens_banco/diagrama_banco.png)

 # Banco de Dados — MongoDB (sj_reports)

 ## O MongoDB e um banco NoSQL orientado a documentos. Nao ha tabelas - existem collections de documentos JSON. O banco roda localmente e e acessado apenas pelo Django (nunca pelo front-end diretamente)

 ![banco_detalhe](imagens_banco/banco_detalhe.png)


## Por que MongoDB e nao SQL?
 ### Os itens de uma venda sao naturalmente um array dentro do documento da venda (embedded documents). Isso evita JOINs e permite buscar uma venda completa em uma unica query.

 ![Detalhes de array](imagens_banco/detalhes_array.png)

 ## Collections

 ### Clientes

 ![Collection_cliente](imagens_banco/collection_clientes.png)

 

 ### Produtos

 ![Produtos](imagens_banco/collection_produtos.png)





 ### Vendas


![vendas](imagens_banco/collection_vendas.png)

## Indices do MongoDB

![Indices](imagens_banco/Indices.png)





