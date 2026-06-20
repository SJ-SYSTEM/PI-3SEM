import json
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, Client
import mongoengine


TEST_DB = 'sj_reports_test'


def connect_test_db():
    mongoengine.disconnect()
    mongoengine.connect(db=TEST_DB, host='127.0.0.1', port=27017)


def disconnect_test_db():
    mongoengine.disconnect()
    from pymongo import MongoClient
    MongoClient('127.0.0.1', 27017).drop_database(TEST_DB)


# ══════════════════════════════════════
#  TESTES DE MODELS
# ══════════════════════════════════════

class TestClienteModel(TestCase):

    def setUp(self):
        connect_test_db()
        from reports.models import Cliente
        self.Cliente = Cliente
        self.Cliente.drop_collection()

    def tearDown(self):
        disconnect_test_db()

    def test_criar_cliente_valido(self):
        c = self.Cliente(nome='Ana Silva', cpf='123.456.789-00', status='ativo')
        c.save()
        self.assertEqual(self.Cliente.objects.count(), 1)
        self.assertEqual(self.Cliente.objects.first().nome, 'Ana Silva')

    def test_nome_obrigatorio(self):
        from mongoengine.errors import ValidationError
        c = self.Cliente(cpf='000.000.000-00')
        with self.assertRaises(ValidationError):
            c.save()

    def test_cpf_unico(self):
        from mongoengine.errors import NotUniqueError
        self.Cliente(nome='Cliente 1', cpf='111.111.111-11').save()
        with self.assertRaises(NotUniqueError):
            self.Cliente(nome='Cliente 2', cpf='111.111.111-11').save()

    def test_status_default_ativo(self):
        c = self.Cliente(nome='Teste')
        c.save()
        self.assertEqual(c.status, 'ativo')

    def test_status_invalido(self):
        from mongoengine.errors import ValidationError
        c = self.Cliente(nome='Teste', status='bloqueado')
        with self.assertRaises(ValidationError):
            c.validate()

    def test_timestamps_preenchidos(self):
        c = self.Cliente(nome='Teste').save()
        self.assertIsNotNone(c.criado)
        self.assertIsNotNone(c.atualizado)


class TestProdutoModel(TestCase):

    def setUp(self):
        connect_test_db()
        from reports.models import Produto
        self.Produto = Produto
        self.Produto.drop_collection()

    def tearDown(self):
        disconnect_test_db()

    def test_criar_produto_valido(self):
        p = self.Produto(
            sku='SKU001', nome='Dipirona 500mg',
            preco_custo=8.5, preco_venda=16.9,
            estoque=100, categoria='medicamento'
        )
        p.save()
        self.assertEqual(self.Produto.objects.count(), 1)

    def test_nome_obrigatorio(self):
        from mongoengine.errors import ValidationError
        p = self.Produto(sku='SKU999')
        with self.assertRaises(ValidationError):
            p.save()

    def test_sku_unico(self):
        from mongoengine.errors import NotUniqueError
        self.Produto(nome='Produto A', sku='SKU001').save()
        with self.assertRaises(NotUniqueError):
            self.Produto(nome='Produto B', sku='SKU001').save()

    def test_categoria_invalida(self):
        from mongoengine.errors import ValidationError
        p = self.Produto(nome='Teste', categoria='invalida')
        with self.assertRaises(ValidationError):
            p.validate()

    def test_categoria_default_medicamento(self):
        p = self.Produto(nome='Teste')
        self.assertEqual(p.categoria, 'medicamento')

    def test_status_default_ativo(self):
        p = self.Produto(nome='Teste')
        self.assertEqual(p.status, 'ativo')

    def test_estoque_default_zero(self):
        p = self.Produto(nome='Teste')
        self.assertEqual(p.estoque, 0)

    def test_estoque_critico(self):
        p = self.Produto(nome='Teste', estoque=3, estoque_minimo=10)
        self.assertTrue(p.estoque <= p.estoque_minimo)

    def test_calculo_margem(self):
        p = self.Produto(nome='Teste', preco_custo=10.0, preco_venda=20.0)
        margem = ((p.preco_venda - p.preco_custo) / p.preco_custo) * 100
        self.assertAlmostEqual(margem, 100.0)


class TestVendaModel(TestCase):

    def setUp(self):
        connect_test_db()
        from reports.models import Venda, ItemVenda
        self.Venda = Venda
        self.ItemVenda = ItemVenda
        self.Venda.drop_collection()

    def tearDown(self):
        disconnect_test_db()

    def test_criar_venda_valida(self):
        item = self.ItemVenda(
            produto_id='abc123',
            nome_produto='Dipirona',
            quantidade=2,
            preco_unit=16.9,
            preco_custo=8.5,
            subtotal=33.8
        )
        v = self.Venda(
            cliente_nome='Joao Silva',
            itens=[item],
            subtotal=33.8,
            total=33.8,
            forma_pagamento='pix',
            status='concluida'
        )
        v.save()
        self.assertEqual(self.Venda.objects.count(), 1)

    def test_total_obrigatorio(self):
        from mongoengine.errors import ValidationError
        v = self.Venda(cliente_nome='Teste')
        with self.assertRaises(ValidationError):
            v.save()

    def test_forma_pagamento_invalida(self):
        from mongoengine.errors import ValidationError
        v = self.Venda(total=10.0, forma_pagamento='cheque')
        with self.assertRaises(ValidationError):
            v.validate()

    def test_status_invalido(self):
        from mongoengine.errors import ValidationError
        v = self.Venda(total=10.0, status='devolvida')
        with self.assertRaises(ValidationError):
            v.validate()

    def test_status_default_concluida(self):
        v = self.Venda(total=10.0)
        self.assertEqual(v.status, 'concluida')

    def test_itens_embedded(self):
        item = self.ItemVenda(
            produto_id='x1', nome_produto='Teste',
            quantidade=1, preco_unit=10.0, subtotal=10.0
        )
        v = self.Venda(total=10.0, itens=[item]).save()
        salvo = self.Venda.objects.first()
        self.assertEqual(len(salvo.itens), 1)
        self.assertEqual(salvo.itens[0].nome_produto, 'Teste')

    def test_desconto_aplicado(self):
        subtotal = 100.0
        desconto = 10.0
        total    = subtotal - desconto
        v = self.Venda(subtotal=subtotal, desconto=desconto, total=total).save()
        self.assertEqual(self.Venda.objects.first().total, 90.0)


# ══════════════════════════════════════
#  TESTES DE API — CLIENTES
# ══════════════════════════════════════

class TestApiClientes(SimpleTestCase):

    def setUp(self):
        connect_test_db()
        from reports.models import Cliente
        self.Cliente = Cliente
        self.Cliente.drop_collection()
        self.client = Client()

    def tearDown(self):
        disconnect_test_db()

    def test_listar_clientes_vazio(self):
        r = self.client.get('/api/clientes/')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertEqual(data['total'], 0)
        self.assertEqual(data['data'], [])

    def test_criar_cliente(self):
        payload = {'nome': 'Maria Oliveira', 'cpf': '111.222.333-44', 'status': 'ativo'}
        r = self.client.post('/api/clientes/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.Cliente.objects.count(), 1)

    def test_criar_cliente_sem_nome(self):
        payload = {'cpf': '000.000.000-00'}
        r = self.client.post('/api/clientes/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_criar_cliente_cpf_duplicado(self):
        self.Cliente(nome='Cliente 1', cpf='111.111.111-11').save()
        payload = {'nome': 'Cliente 2', 'cpf': '111.111.111-11'}
        r = self.client.post('/api/clientes/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_listar_clientes_filtro_status(self):
        self.Cliente(nome='Ativo', cpf='111.111.111-11', status='ativo').save()
        self.Cliente(nome='Inativo', cpf='222.222.222-22', status='inativo').save()
        r = self.client.get('/api/clientes/?status=ativo')
        data = json.loads(r.content)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['data'][0]['nome'], 'Ativo')

    def test_buscar_cliente_por_id(self):
        c = self.Cliente(nome='Pedro Costa').save()
        r = self.client.get(f'/api/clientes/{c.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.content)['nome'], 'Pedro Costa')

    def test_buscar_cliente_inexistente(self):
        r = self.client.get('/api/clientes/000000000000000000000000/')
        self.assertEqual(r.status_code, 404)

    def test_atualizar_cliente(self):
        c = self.Cliente(nome='Original').save()
        payload = {'nome': 'Atualizado', 'status': 'inativo'}
        r = self.client.put(f'/api/clientes/{c.id}/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.Cliente.objects.get(id=c.id).nome, 'Atualizado')

    def test_deletar_cliente(self):
        c = self.Cliente(nome='Para Deletar').save()
        r = self.client.delete(f'/api/clientes/{c.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.Cliente.objects.count(), 0)


# ══════════════════════════════════════
#  TESTES DE API — PRODUTOS
# ══════════════════════════════════════

class TestApiProdutos(SimpleTestCase):

    def setUp(self):
        connect_test_db()
        from reports.models import Produto
        self.Produto = Produto
        self.Produto.drop_collection()
        self.client = Client()

    def tearDown(self):
        disconnect_test_db()

    def test_listar_produtos_vazio(self):
        r = self.client.get('/api/produtos/')
        self.assertEqual(r.status_code, 200)

    def test_criar_produto(self):
        payload = {
            'sku': 'SKU001', 'nome': 'Dipirona 500mg',
            'preco_custo': 8.5, 'preco_venda': 16.9,
            'estoque': 100, 'categoria': 'medicamento', 'status': 'ativo'
        }
        r = self.client.post('/api/produtos/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.Produto.objects.count(), 1)

    def test_criar_produto_sem_nome(self):
        payload = {'sku': 'SKU999', 'preco_venda': 10.0}
        r = self.client.post('/api/produtos/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_criar_produto_sku_duplicado(self):
        self.Produto(nome='Produto A', sku='SKU001').save()
        payload = {'nome': 'Produto B', 'sku': 'SKU001'}
        r = self.client.post('/api/produtos/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 400)
        data = json.loads(r.content)
        self.assertIn('SKU001', data['erro'])

    def test_metricas_produtos(self):
        self.Produto(nome='Ativo 1', sku='SKU001', status='ativo', estoque=10, estoque_minimo=5).save()
        self.Produto(nome='Ativo 2', sku='SKU002', status='ativo', estoque=2, estoque_minimo=5).save()
        self.Produto(nome='Inativo', sku='SKU003', status='inativo', estoque=0, estoque_minimo=5).save()
        r = self.client.get('/api/produtos/metricas/')
        data = json.loads(r.content)
        self.assertEqual(data['total'], 3)
        self.assertEqual(data['ativos'], 2)
        self.assertEqual(data['inativos'], 1)
        self.assertEqual(data['criticos'], 1)

    def test_atualizar_produto(self):
        p = self.Produto(nome='Original', sku='SKU001', preco_venda=10.0).save()
        payload = {'preco_venda': 20.0, 'estoque': 50}
        r = self.client.put(f'/api/produtos/{p.id}/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        atualizado = self.Produto.objects.get(id=p.id)
        self.assertEqual(atualizado.preco_venda, 20.0)
        self.assertEqual(atualizado.estoque, 50)

    def test_deletar_produto(self):
        p = self.Produto(nome='Para Deletar', sku='SKU001').save()
        r = self.client.delete(f'/api/produtos/{p.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.Produto.objects.count(), 0)


# ══════════════════════════════════════
#  TESTES DE API — VENDAS
# ══════════════════════════════════════

class TestApiVendas(SimpleTestCase):

    def setUp(self):
        connect_test_db()
        from reports.models import Venda, Produto, Cliente
        self.Venda   = Venda
        self.Produto = Produto
        self.Cliente = Cliente
        self.Venda.drop_collection()
        self.Produto.drop_collection()
        self.Cliente.drop_collection()
        self.client = Client()
        self.produto = self.Produto(
            nome='Dipirona 500mg', sku='SKU001',
            preco_custo=8.5, preco_venda=16.9,
            estoque=50, unidade='cx'
        ).save()

    def tearDown(self):
        disconnect_test_db()

    def _payload_venda(self, qtd=2, status='concluida'):
        return {
            'cliente_nome': 'Consumidor Final',
            'subtotal': self.produto.preco_venda * qtd,
            'desconto': 0,
            'total':    self.produto.preco_venda * qtd,
            'forma_pagamento': 'pix',
            'status': status,
            'itens': [{
                'produto_id':   str(self.produto.id),
                'nome_produto': self.produto.nome,
                'quantidade':   qtd,
                'preco_unit':   self.produto.preco_venda,
                'preco_custo':  self.produto.preco_custo,
                'subtotal':     self.produto.preco_venda * qtd,
                'unidade':      self.produto.unidade,
            }]
        }

    def test_criar_venda(self):
        r = self.client.post('/api/vendas/', json.dumps(self._payload_venda()), content_type='application/json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.Venda.objects.count(), 1)

    def test_venda_decrementa_estoque(self):
        estoque_antes = self.produto.estoque
        self.client.post('/api/vendas/', json.dumps(self._payload_venda(qtd=3)), content_type='application/json')
        self.produto.reload()
        self.assertEqual(self.produto.estoque, estoque_antes - 3)

    def test_venda_sem_itens(self):
        payload = {'cliente_nome': 'Teste', 'total': 0, 'itens': []}
        r = self.client.post('/api/vendas/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_venda_estoque_insuficiente(self):
        payload = self._payload_venda(qtd=999)
        r = self.client.post('/api/vendas/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 400)
        data = json.loads(r.content)
        self.assertIn('Estoque insuficiente', data['erro'])

    def test_venda_cancelada_nao_decrementa_estoque(self):
        estoque_antes = self.produto.estoque
        self.client.post('/api/vendas/', json.dumps(self._payload_venda(status='cancelada')), content_type='application/json')
        self.produto.reload()
        self.assertEqual(self.produto.estoque, estoque_antes)

    def test_listar_vendas(self):
        self.client.post('/api/vendas/', json.dumps(self._payload_venda()), content_type='application/json')
        self.client.post('/api/vendas/', json.dumps(self._payload_venda()), content_type='application/json')
        r = self.client.get('/api/vendas/')
        data = json.loads(r.content)
        self.assertEqual(data['total'], 2)

    def test_buscar_venda_por_id(self):
        r = self.client.post('/api/vendas/', json.dumps(self._payload_venda()), content_type='application/json')
        venda_id = json.loads(r.content)['id']
        r2 = self.client.get(f'/api/vendas/{venda_id}/')
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(json.loads(r2.content)['cliente_nome'], 'Consumidor Final')

    def test_desconto_aplicado_na_venda(self):
        payload = self._payload_venda(qtd=1)
        payload['desconto'] = 5.0
        payload['total']    = payload['subtotal'] - 5.0
        r = self.client.post('/api/vendas/', json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 201)
        venda = self.Venda.objects.first()
        self.assertEqual(venda.desconto, 5.0)
        self.assertEqual(venda.total, payload['subtotal'] - 5.0)
