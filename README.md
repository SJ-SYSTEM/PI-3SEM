# SJ Farma System — Sistema de Gestão para Farmácia
#### Logo

<img width="250px" alt="FarmaciaLogo" src="https://github.com/user-attachments/assets/b4190b0e-c0ac-4e14-b6df-596dec06a6d2" />


<br>

## Descrição do Projeto

O **SJ Farma System** é um projeto desenvolvido para atender às necessidades de uma farmácia de pequeno porte. A proposta é reformular um sistema antigo feito em PHP, modernizando sua estrutura e adicionando novas funcionalidades voltadas para gestão, controle e organização das rotinas da farmácia.

O sistema antigo já possuía módulos como **estoque, vendas, clientes, notas fiscais e PDV**. Na nova versão, o **PDV será mantido em PHP**, enquanto os demais módulos serão migrados para um novo sistema desenvolvido em **Django**. A comunicação entre o PDV e o sistema novo será feita por meio de uma **API REST**, permitindo que os dados sejam integrados de forma mais organizada.

O banco de dados utilizado no projeto será o **MongoDB**, conforme exigência acadêmica, permitindo uma modelagem orientada a documentos e adequada às necessidades do sistema.

---

## Objetivo do Sistema

O objetivo principal do projeto é criar uma solução personalizada para uma farmácia de bairro, oferecendo uma ferramenta simples, eficiente e confiável para auxiliar nas atividades diárias.

A proposta busca:

* Organizar o controle de estoque;
* Facilitar o gerenciamento de clientes;
* Integrar o PDV antigo com o novo sistema;
* Melhorar a gestão de vendas;
* Permitir o controle de receitas médicas;
* Utilizar notas fiscais para auxiliar na atualização do estoque;
* Melhorar a interface visual do sistema;
* Aplicar testes durante o desenvolvimento.

---

## Escopo do Projeto

O sistema será dividido entre duas partes principais:

### Sistema antigo em PHP

O módulo de **PDV** será mantido em PHP, pois já faz parte do sistema existente e continuará sendo utilizado para registrar as vendas.

### Novo sistema em Django

Os demais módulos serão desenvolvidos ou migrados para Django, com uma interface reestilizada e uma estrutura mais organizada. Esse novo sistema será responsável por gerenciar clientes, medicamentos, estoque, receitas, notas fiscais, relatórios e integração com o PDV.

---

## Funcionalidades

As principais funcionalidades previstas são:

* Autenticação de usuários;
* Cadastro de clientes;
* Cadastro de medicamentos;
* Controle de estoque;
* Registro e consulta de vendas;
* Integração com o PDV em PHP;
* Cadastro e digitalização de notas fiscais;
* Atualização do estoque a partir dos dados da nota fiscal;
* Cadastro de receitas médicas;
* Validação de receitas;
* Relatórios simples;
* Gerenciamento de usuários;
* Reestilização das telas;
* Testes funcionais e de integração.

---

## Notas Fiscais

A funcionalidade de notas fiscais terá como objetivo **cadastrar ou digitalizar notas fiscais recebidas**, permitindo que as informações sejam utilizadas para alimentar o estoque do sistema.

Este projeto **não tem como foco a emissão de notas fiscais**, mas sim o uso das informações das notas para automatizar ou facilitar o controle de entrada de produtos.

---

## Tecnologias Utilizadas

* **PHP** — manutenção do PDV existente;
* **Django** — desenvolvimento do novo sistema;
* **Django REST Framework** — criação da API de integração;
* **MongoDB** — banco de dados orientado a documentos;
* **HTML e CSS** — estrutura e reestilização das telas;
* **JavaScript** — apoio nas interações da interface;
* **GitHub Projects** — organização de backlog, tarefas e sprints.

---

## Documentação e Planejamento

Durante o desenvolvimento do projeto, foram produzidos documentos e artefatos para apoiar a organização do sistema, incluindo:

* Diagrama de caso de uso;
* Diagrama de contexto;
* Backlog inicial;
* Canvas de requisitos funcionais e não funcionais;
* Metas de usabilidade;
* Requisitos de acessibilidade;
* Mapa do site;
* Fluxos críticos;
* Wireframes low-fi;
* Style guide com paleta de cores, tipografia, componentes e padrões de tela;
* Modelagem do banco de dados em MongoDB.

---

## Público-alvo

O sistema é voltado para atendentes e farmacêuticos de uma farmácia de pequeno porte. Por isso, a interface deve ser simples, clara e objetiva, facilitando o uso durante o expediente e reduzindo erros em tarefas como venda, cadastro, controle de estoque e validação de receitas.

---

## Considerações Finais

O **SJ Farma System** busca modernizar a rotina de uma farmácia de bairro, mantendo parte do sistema legado em PHP e integrando-o com uma nova aplicação em Django. A proposta é oferecer uma solução prática, de baixo custo e adequada à realidade do estabelecimento, melhorando a gestão operacional e a qualidade do atendimento.
