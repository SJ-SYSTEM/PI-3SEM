from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

# ── Clientes ────────────────────────────
class Cliente(Document):
    nome        = fields.StringField(required=True, max_length=255)
    cpf         = fields.StringField(max_length=14, unique=True)
    telefone    = fields.StringField(max_length=20)
    email       = fields.EmailField()
    endereco    = fields.StringField(max_length=500)
    status      = fields.StringField(default='ativo', choices=['ativo', 'inativo'])
    criado      = fields.DateTimeField(default=datetime.now)
    atualizado  = fields.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'clientes',
        'ordering': ['nome']
    }

    def __str__(self):
        return self.nome


# ── Produtos ────────────────────────────
class Produto(Document):
    nome           = fields.StringField(required=True, max_length=255)
    descricao      = fields.StringField()
    preco_custo    = fields.FloatField(default=0.0)
    preco_venda    = fields.FloatField(default=0.0)
    estoque        = fields.IntField(default=0)
    estoque_minimo = fields.IntField(default=5)
    unidade        = fields.StringField(default='un', max_length=20)
    validade       = fields.DateTimeField()
    lote           = fields.StringField(max_length=50)
    categoria      = fields.StringField(
        default='medicamento',
        choices=['medicamento', 'perfumaria', 'higiene', 'alimento', 'outro']
    )
    status         = fields.StringField(default='ativo', choices=['ativo', 'inativo'])
    criado         = fields.DateTimeField(default=datetime.now)
    atualizado     = fields.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'produtos',
        'ordering': ['nome']
    }

    def __str__(self):
        return self.nome


# ── Itens da Venda ──────────────────────
class ItemVenda(EmbeddedDocument):
    produto_id   = fields.StringField(required=True)
    nome_produto = fields.StringField(required=True)
    quantidade   = fields.IntField(required=True, default=1)
    preco_unit   = fields.FloatField(required=True)
    subtotal     = fields.FloatField(required=True)


# ── Vendas ──────────────────────────────
class Venda(Document):
    cliente_id      = fields.StringField()
    cliente_nome    = fields.StringField()
    itens           = fields.EmbeddedDocumentListField(ItemVenda)
    total           = fields.FloatField(required=True)
    desconto        = fields.FloatField(default=0.0)
    forma_pagamento = fields.StringField(
        default='dinheiro',
        choices=['dinheiro', 'cartao_credito', 'cartao_debito', 'pix']
    )
    status          = fields.StringField(
        default='concluida',
        choices=['concluida', 'cancelada', 'pendente']
    )
    criado          = fields.DateTimeField(default=datetime.now)
    atualizado      = fields.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'vendas',
        'ordering': ['-criado']
    }


# ── Relatórios Diários ──────────────────
class RelatorioDiario(Document):
    data                 = fields.DateTimeField(required=True)
    total_vendas         = fields.FloatField(default=0.0)
    qtd_vendas           = fields.IntField(default=0)
    ticket_medio         = fields.FloatField(default=0.0)
    produto_mais_vendido = fields.StringField()
    criado               = fields.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'relatorios_diarios',
        'ordering': ['-data']
    }
