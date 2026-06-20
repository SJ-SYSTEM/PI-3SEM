from mongoengine import Document, fields
from datetime import datetime


class Produto(Document):
    sku = fields.StringField(unique=True, max_length=50)
    nome = fields.StringField(required=True, max_length=255)
    descricao = fields.StringField()
    fabricante = fields.StringField(max_length=255)
    preco_custo = fields.FloatField(default=0.0)
    preco_venda = fields.FloatField(default=0.0)
    estoque = fields.IntField(default=0)
    estoque_minimo = fields.IntField(default=5)
    unidade = fields.StringField(default='un', max_length=20)
    validade = fields.DateTimeField()
    lote = fields.StringField(max_length=50)

    categoria = fields.StringField(
        default='medicamento',
        choices=['medicamento', 'perfumaria', 'higiene', 'alimento', 'outro']
    )

    status = fields.StringField(
        default='ativo',
        choices=['ativo', 'inativo']
    )

    criado = fields.DateTimeField(default=datetime.now)
    atualizado = fields.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'produtos',
        'ordering': ['nome']
    }

    def __str__(self):
        return self.nome