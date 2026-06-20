from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Produto, Cliente, Venda, ItemVenda, RelatorioDiario
from datetime import datetime, timedelta, timezone
from mongoengine.connection import get_db
import json


def documento_para_dict(doc):
    d = doc.to_mongo().to_dict()
    d['id'] = str(d.pop('_id'))
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


# ══════════════════════════════════════
#  HELPERS RELATORIOS
# ══════════════════════════════════════

def _parse_date(value, fallback):
    if not value:
        return fallback
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return fallback

def _filtro_base(request):
    hoje       = datetime.now(tz=timezone.utc)
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    de         = _parse_date(request.GET.get("de"),  inicio_mes)
    ate        = _parse_date(request.GET.get("ate"), hoje)
    ate        = ate.replace(hour=23, minute=59, second=59, microsecond=999999)

    filtro = {"criado": {"$gte": de, "$lte": ate}}

    st = request.GET.get("status")
    if st:
        filtro["status"] = st

    produto = request.GET.get("produto")
    if produto:
        filtro["itens.nome_produto"] = {"$regex": produto, "$options": "i"}

    return filtro


# ══════════════════════════════════════
#  PRODUTOS
# ══════════════════════════════════════

@method_decorator(csrf_exempt, name='dispatch')
class ProdutoListCreate(View):

    def get(self, request):
        try:
            categoria = request.GET.get('categoria')
            status    = request.GET.get('status', 'ativo')
            busca     = request.GET.get('busca', '').strip()

            produtos = Produto.objects.filter(status=status)
            if categoria:
                produtos = produtos.filter(categoria=categoria)
            if busca:
                from mongoengine.queryset.visitor import Q
                produtos = Produto.objects.filter(
                    Q(nome__icontains=busca) |
                    Q(sku__icontains=busca)  |
                    Q(categoria__icontains=busca)
                ).filter(status=status)

            data = [documento_para_dict(p) for p in produtos]
            return JsonResponse({'total': len(data), 'data': data}, safe=False)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    def post(self, request):
        try:
            body = json.loads(request.body)

            if not body.get('nome'):
                return JsonResponse({'erro': 'Nome obrigatorio.'}, status=400)
            if not body.get('sku'):
                return JsonResponse({'erro': 'SKU obrigatorio.'}, status=400)

            produto = Produto(
                sku            = body.get('sku'),
                nome           = body.get('nome'),
                descricao      = body.get('descricao', ''),
                fabricante     = body.get('fabricante', ''),
                preco_custo    = float(body.get('preco_custo', 0)),
                preco_venda    = float(body.get('preco_venda', 0)),
                estoque        = int(body.get('estoque', 0)),
                estoque_minimo = int(body.get('estoque_minimo', 5)),
                unidade        = body.get('unidade', 'un'),
                categoria      = body.get('categoria', 'medicamento'),
                lote           = body.get('lote', ''),
                status         = body.get('status', 'ativo'),
            )
            if body.get('validade'):
                produto.validade = datetime.strptime(body['validade'][:10], '%Y-%m-%d')

            produto.save()
            return JsonResponse({'mensagem': 'Produto criado com sucesso!', 'id': str(produto.id)}, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ProdutoDetail(View):

    def get(self, request, id):
        try:
            produto = Produto.objects.get(id=id)
            return JsonResponse(documento_para_dict(produto))
        except Produto.DoesNotExist:
            return JsonResponse({'erro': 'Produto nao encontrado'}, status=404)

    def put(self, request, id):
        try:
            body    = json.loads(request.body)
            produto = Produto.objects.get(id=id)
            campos  = ['sku','nome','descricao','fabricante','preco_custo','preco_venda',
                       'estoque','estoque_minimo','unidade','categoria','lote','status']
            for campo in campos:
                if campo in body:
                    valor = body[campo]
                    if campo in ['preco_custo', 'preco_venda']:
                        valor = float(valor)
                    elif campo in ['estoque', 'estoque_minimo']:
                        valor = int(valor)
                    setattr(produto, campo, valor)
            if 'validade' in body and body['validade']:
                produto.validade = datetime.strptime(body['validade'][:10], '%Y-%m-%d')
            produto.atualizado = datetime.now()
            produto.save()
            return JsonResponse({'mensagem': 'Produto atualizado com sucesso!'})
        except Produto.DoesNotExist:
            return JsonResponse({'erro': 'Produto nao encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)

    def delete(self, request, id):
        try:
            produto = Produto.objects.get(id=id)
            produto.delete()
            return JsonResponse({'mensagem': 'Produto removido com sucesso!'})
        except Produto.DoesNotExist:
            return JsonResponse({'erro': 'Produto nao encontrado'}, status=404)


class ProdutoMetricas(View):

    def get(self, request):
        try:
            todos    = Produto.objects.all()
            ativos   = Produto.objects.filter(status='ativo')
            inativos = Produto.objects.filter(status='inativo')
            criticos = [p for p in ativos if p.estoque <= p.estoque_minimo]

            return JsonResponse({
                'total':    todos.count(),
                'ativos':   ativos.count(),
                'inativos': inativos.count(),
                'criticos': len(criticos),
            })
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)


# ══════════════════════════════════════
#  CLIENTES
# ══════════════════════════════════════

@method_decorator(csrf_exempt, name='dispatch')
class ClienteListCreate(View):

    def get(self, request):
        try:
            status   = request.GET.get('status', '')
            clientes = Cliente.objects.filter(status=status) if status else Cliente.objects.all()
            data     = [documento_para_dict(c) for c in clientes]
            return JsonResponse({'total': len(data), 'data': data}, safe=False)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    def post(self, request):
        try:
            body    = json.loads(request.body)
            cliente = Cliente(
                nome     = body.get('nome'),
                cpf      = body.get('cpf', ''),
                telefone = body.get('telefone', ''),
                email    = body.get('email') or None,
                endereco = body.get('endereco', ''),
                status   = body.get('status', 'ativo'),
            )
            cliente.save()
            return JsonResponse({'mensagem': 'Cliente criado com sucesso!', 'id': str(cliente.id)}, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ClienteDetail(View):

    def get(self, request, id):
        try:
            cliente = Cliente.objects.get(id=id)
            return JsonResponse(documento_para_dict(cliente))
        except Cliente.DoesNotExist:
            return JsonResponse({'erro': 'Cliente nao encontrado'}, status=404)

    def put(self, request, id):
        try:
            body    = json.loads(request.body)
            cliente = Cliente.objects.get(id=id)
            for campo, valor in body.items():
                setattr(cliente, campo, valor)
            cliente.atualizado = datetime.now()
            cliente.save()
            return JsonResponse({'mensagem': 'Cliente atualizado com sucesso!'})
        except Cliente.DoesNotExist:
            return JsonResponse({'erro': 'Cliente nao encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)

    def delete(self, request, id):
        try:
            cliente = Cliente.objects.get(id=id)
            cliente.delete()
            return JsonResponse({'mensagem': 'Cliente removido com sucesso!'})
        except Cliente.DoesNotExist:
            return JsonResponse({'erro': 'Cliente nao encontrado'}, status=404)


# ══════════════════════════════════════
#  VENDAS
# ══════════════════════════════════════

@method_decorator(csrf_exempt, name='dispatch')
class VendaListCreate(View):

    def get(self, request):
        try:
            status = request.GET.get('status')
            vendas = Venda.objects.all() if not status else Venda.objects.filter(status=status)
            data   = [documento_para_dict(v) for v in vendas]
            return JsonResponse({'total': len(data), 'data': data}, safe=False)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    def post(self, request):
        try:
            body   = json.loads(request.body)
            itens_body = body.get('itens', [])

            if not itens_body:
                return JsonResponse({'erro': 'A venda deve conter ao menos um item.'}, status=400)

            status_venda = body.get('status', 'concluida')

            # Valida estoque de cada item
            if status_venda == 'concluida':
                for item in itens_body:
                    try:
                        produto = Produto.objects.get(id=item['produto_id'])
                    except Produto.DoesNotExist:
                        return JsonResponse({'erro': 'Produto nao encontrado: ' + item.get('nome_produto','')}, status=400)
                    if produto.estoque < item['quantidade']:
                        return JsonResponse({
                            'erro': 'Estoque insuficiente para ' + produto.nome +
                                    '. Disponivel: ' + str(produto.estoque) + ' ' + produto.unidade
                        }, status=400)

            # Monta itens embedded
            itens_obj = []
            for item in itens_body:
                itens_obj.append(ItemVenda(
                    produto_id   = item.get('produto_id', ''),
                    nome_produto = item.get('nome_produto', ''),
                    quantidade   = int(item.get('quantidade', 1)),
                    preco_unit   = float(item.get('preco_unit', 0)),
                    preco_custo  = float(item.get('preco_custo', 0)),
                    subtotal     = float(item.get('subtotal', 0)),
                    unidade      = item.get('unidade', ''),
                ))

            venda = Venda(
                cliente_id      = body.get('cliente_id', ''),
                cliente_nome    = body.get('cliente_nome', ''),
                itens           = itens_obj,
                subtotal        = float(body.get('subtotal', 0)),
                total           = float(body.get('total', 0)),
                desconto        = float(body.get('desconto', 0)),
                forma_pagamento = body.get('forma_pagamento', 'dinheiro'),
                status          = status_venda,
            )
            venda.save()

            # Decrementa estoque apenas se concluida
            if status_venda == 'concluida':
                for item in itens_body:
                    Produto.objects(id=item['produto_id']).update_one(dec__estoque=int(item['quantidade']))

            return JsonResponse({'mensagem': 'Venda registrada com sucesso!', 'id': str(venda.id)}, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class VendaDetail(View):

    def get(self, request, id):
        try:
            venda = Venda.objects.get(id=id)
            return JsonResponse(documento_para_dict(venda))
        except Venda.DoesNotExist:
            return JsonResponse({'erro': 'Venda nao encontrada'}, status=404)


# ══════════════════════════════════════
#  RELATORIOS EXISTENTES
# ══════════════════════════════════════


@method_decorator(csrf_exempt, name='dispatch')
class BiVendasView(View):
    def get(self, request):
        try:
            from pymongo import MongoClient
            from datetime import datetime, timedelta
            client = MongoClient('127.0.0.1', 27017)
            db     = client['sj_reports']
            meses  = int(request.GET.get('meses', 6))

            hoje  = datetime.utcnow()
            inicio = datetime(hoje.year, hoje.month, 1) - timedelta(days=30*(meses-1))

            pipeline = [
                { "$match": { "criado": { "$gte": inicio }, "status": "concluida" } },
                { "$group": {
                    "_id": {
                        "ano": { "$year": "$criado" },
                        "mes": { "$month": "$criado" }
                    },
                    "faturamento": { "$sum": "$total" },
                    "lucro":       { "$sum": { "$subtract": ["$total", { "$sum": { "$map": {
                        "input": { "$ifNull": ["$itens", []] },
                        "as": "item",
                        "in": { "$multiply": [
                            { "$ifNull": ["$$item.preco_custo", 0] },
                            { "$ifNull": ["$$item.quantidade", 0] }
                        ]}
                    }}}] } },
                    "quantidade":  { "$sum": 1 },
                    "ticket":      { "$avg": "$total" },
                    "cancelamentos": { "$sum": 0 },
                }},
                { "$sort": { "_id.ano": 1, "_id.mes": 1 } }
            ]

            # Cancelamentos por mes
            pipeline_canc = [
                { "$match": { "criado": { "$gte": inicio }, "status": "cancelada" } },
                { "$group": {
                    "_id": { "ano": { "$year": "$criado" }, "mes": { "$month": "$criado" } },
                    "cancelamentos": { "$sum": 1 }
                }}
            ]

            nomes = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
            canc_map = {}
            for c in db.vendas.aggregate(pipeline_canc):
                key = (c['_id']['ano'], c['_id']['mes'])
                canc_map[key] = c['cancelamentos']

            resultado = []
            for r in db.vendas.aggregate(pipeline):
                ano = r['_id']['ano']
                mes = r['_id']['mes']
                key = (ano, mes)
                resultado.append({
                    'mes':           f"{nomes[mes-1]}/{str(ano)[2:]}",
                    'faturamento':   round(r['faturamento'], 2),
                    'lucro':         round(r['lucro'], 2),
                    'quantidade':    r['quantidade'],
                    'ticket':        round(r['ticket'], 2),
                    'cancelamentos': canc_map.get(key, 0),
                })

            # Vendas por hora do dia
            pipeline_hora = [
                { "$match": { "status": "concluida" } },
                { "$group": {
                    "_id":       { "$hour": "$criado" },
                    "quantidade": { "$sum": 1 },
                    "total":      { "$sum": "$total" }
                }},
                { "$sort": { "_id": 1 } }
            ]
            por_hora = [
                { "hora": r["_id"], "quantidade": r["quantidade"], "total": round(r["total"], 2) }
                for r in db.vendas.aggregate(pipeline_hora)
            ]

            # Vendas por categoria de produto
            pipeline_cat = [
                { "$match": { "status": "concluida" } },
                { "$unwind": "$itens" },
                { "$lookup": {
                    "from": "produtos",
                    "let": { "pid": { "$toObjectId": "$itens.produto_id" } },
                    "pipeline": [{ "$match": { "$expr": { "$eq": ["$_id", "$$pid"] } } }],
                    "as": "produto"
                }},
                { "$unwind": { "path": "$produto", "preserveNullAndEmptyArrays": True } },
                { "$group": {
                    "_id":        { "$ifNull": ["$produto.categoria", "outro"] },
                    "quantidade": { "$sum": "$itens.quantidade" },
                    "total":      { "$sum": "$itens.subtotal" }
                }},
                { "$sort": { "total": -1 } }
            ]
            por_categoria = [
                { "categoria": r["_id"], "quantidade": r["quantidade"], "total": round(r["total"], 2) }
                for r in db.vendas.aggregate(pipeline_cat)
            ]

            return JsonResponse({
                'mensal':       resultado,
                'por_hora':     por_hora,
                'por_categoria': por_categoria,
            }, safe=False)

        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BiEstoqueView(View):
    def get(self, request):
        try:
            from pymongo import MongoClient
            from datetime import datetime, timedelta
            client = MongoClient('127.0.0.1', 27017)
            db     = client['sj_reports']
            meses  = int(request.GET.get('meses', 6))

            hoje   = datetime.utcnow()
            inicio = datetime(hoje.year, hoje.month, 1) - timedelta(days=30*(meses-1))
            nomes  = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

            # Saida por mes (via vendas concluidas)
            saida_pipeline = [
                { "$match": { "criado": { "$gte": inicio }, "status": "concluida" } },
                { "$unwind": "$itens" },
                { "$group": {
                    "_id": { "ano": { "$year": "$criado" }, "mes": { "$month": "$criado" } },
                    "qtd_saida":   { "$sum": "$itens.quantidade" },
                    "valor_saida": { "$sum": "$itens.subtotal" },
                }},
                { "$sort": { "_id.ano": 1, "_id.mes": 1 } }
            ]

            saida_map = {}
            for r in db.vendas.aggregate(saida_pipeline):
                key = (r['_id']['ano'], r['_id']['mes'])
                saida_map[key] = { 'qtd': r['qtd_saida'], 'valor': round(r['valor_saida'], 2) }

            # Monta resultado mensal
            mensal = []
            for i in range(meses):
                dt  = datetime(hoje.year, hoje.month, 1) - timedelta(days=30*i)
                key = (dt.year, dt.month)
                s   = saida_map.get(key, { 'qtd': 0, 'valor': 0 })
                mensal.insert(0, {
                    'mes':        f"{nomes[dt.month-1]}/{str(dt.year)[2:]}",
                    'qtd_saida':  s['qtd'],
                    'valor_saida': s['valor'],
                })

            # Valor total do estoque atual
            val_est = list(db.produtos.aggregate([
                { "$group": { "_id": None, "total": { "$sum": { "$multiply": ["$estoque", "$preco_custo"] } } } }
            ]))
            valor_estoque = round(val_est[0]['total'], 2) if val_est else 0

            # Produtos com validade proxima (60 dias)
            limite_val = datetime.utcnow() + timedelta(days=60)
            vencendo = list(db.produtos.find(
                { "validade": { "$lte": limite_val, "$gte": datetime.utcnow() }, "status": "ativo" },
                { "nome": 1, "validade": 1, "estoque": 1, "unidade": 1 }
            ).sort("validade", 1).limit(10))
            for p in vencendo:
                p['_id'] = str(p['_id'])
                if 'validade' in p:
                    p['validade'] = p['validade'].strftime('%Y-%m-%d')

            # Produtos criticos
            criticos = list(db.produtos.find(
                { "$expr": { "$lte": ["$estoque", "$estoque_minimo"] }, "status": "ativo" },
                { "nome": 1, "estoque": 1, "estoque_minimo": 1, "unidade": 1 }
            ).limit(10))
            for p in criticos:
                p['_id'] = str(p['_id'])

            # Produtos mais vendidos (giro)
            giro_pipeline = [
                { "$match": { "status": "concluida" } },
                { "$unwind": "$itens" },
                { "$group": {
                    "_id":  "$itens.nome_produto",
                    "qtd":  { "$sum": "$itens.quantidade" },
                    "total":{ "$sum": "$itens.subtotal" },
                }},
                { "$sort": { "qtd": -1 } },
                { "$limit": 10 }
            ]
            giro = [{ "nome": r["_id"], "qtd": r["qtd"], "total": round(r["total"], 2) }
                    for r in db.vendas.aggregate(giro_pipeline)]

            return JsonResponse({
                'mensal':         mensal,
                'valor_estoque':  valor_estoque,
                'vencendo':       vencendo,
                'criticos':       criticos,
                'giro':           giro,
            }, safe=False)

        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

class RelatorioDiarioList(View):

    def get(self, request):
        try:
            relatorios = RelatorioDiario.objects.all()
            data       = [documento_para_dict(r) for r in relatorios]
            return JsonResponse({'total': len(data), 'data': data}, safe=False)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)


class EstoqueCritico(View):

    def get(self, request):
        try:
            produtos = Produto.objects.filter(status='ativo')
            criticos = [p for p in produtos if p.estoque <= p.estoque_minimo]
            data     = [documento_para_dict(p) for p in criticos]
            return JsonResponse({'total': len(data), 'data': data}, safe=False)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)


class TicketMedio(View):

    def get(self, request):
        try:
            vendas = Venda.objects.filter(status='concluida')
            total  = sum(v.total for v in vendas)
            qtd    = vendas.count()
            ticket = round(total / qtd, 2) if qtd > 0 else 0
            return JsonResponse({
                'qtd_vendas':   qtd,
                'total':        total,
                'ticket_medio': ticket,
            })
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)


# ══════════════════════════════════════
#  RELATORIOS — GRAFICOS
# ══════════════════════════════════════

class KpisView(View):
    def get(self, request):
        try:
            db     = get_db()
            filtro = _filtro_base(request)

            pipeline = [
                {"$match": filtro},
                {"$group": {
                    "_id": None,
                    "faturamento":  {"$sum": "$total"},
                    "total_vendas": {"$sum": 1},
                    "custo_total":  {"$sum": {
                        "$sum": {
                            "$map": {
                                "input": {"$ifNull": ["$itens", []]},
                                "as":    "item",
                                "in": {"$multiply": [
                                    {"$ifNull": ["$$item.preco_custo", 0]},
                                    {"$ifNull": ["$$item.quantidade", 0]},
                                ]}
                            }
                        }
                    }},
                }},
            ]

            res    = list(db.vendas.aggregate(pipeline))
            fat    = res[0]["faturamento"]  if res else 0
            cst    = res[0]["custo_total"]  if res else 0
            tot    = res[0]["total_vendas"] if res else 0
            lucro  = fat - cst
            margem = round(lucro / fat * 100, 1) if fat > 0 else 0
            ticket = round(fat / tot, 2)          if tot > 0 else 0

            f2 = {k: v for k, v in filtro.items() if k != "status"}
            cancelamentos = db.vendas.count_documents({**f2, "status": "cancelada"})
            pendentes     = db.vendas.count_documents({**f2, "status": "pendente"})

            return JsonResponse({
                "faturamento":   round(fat,   2),
                "custo_total":   round(cst,   2),
                "lucro":         round(lucro, 2),
                "margem_pct":    margem,
                "ticket_medio":  ticket,
                "total_vendas":  tot,
                "cancelamentos": cancelamentos,
                "pendentes":     pendentes,
            })
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)


class FaturamentoPorDiaView(View):
    def get(self, request):
        try:
            db     = get_db()
            filtro = _filtro_base(request)

            pipeline = [
                {"$match": filtro},
                {"$addFields": {
                    "custo_venda": {"$sum": {"$map": {
                        "input": {"$ifNull": ["$itens", []]},
                        "as":    "item",
                        "in": {"$multiply": [
                            {"$ifNull": ["$$item.preco_custo", 0]},
                            {"$ifNull": ["$$item.quantidade", 0]},
                        ]}
                    }}}
                }},
                {"$group": {
                    "_id": {
                        "ano": {"$year":       "$criado"},
                        "mes": {"$month":      "$criado"},
                        "dia": {"$dayOfMonth": "$criado"},
                    },
                    "faturamento": {"$sum": "$total"},
                    "custo":       {"$sum": "$custo_venda"},
                }},
                {"$sort": {"_id.ano": 1, "_id.mes": 1, "_id.dia": 1}},
            ]

            data = []
            for r in db.vendas.aggregate(pipeline):
                d   = r["_id"]
                fat = round(r["faturamento"], 2)
                cst = round(r["custo"],       2)
                data.append({
                    "data":        f"{d['ano']:04d}-{d['mes']:02d}-{d['dia']:02d}",
                    "faturamento": fat,
                    "lucro":       round(fat - cst, 2),
                })

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)


class ComparativoMensalView(View):
    MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

    def get(self, request):
        try:
            db   = get_db()
            n    = int(request.GET.get("meses", 6))
            hoje = datetime.now(tz=timezone.utc)
            st   = request.GET.get("status")

            match = {"criado": {"$gte": hoje - timedelta(days=n * 31)}}
            if st:
                match["status"] = st

            pipeline = [
                {"$match": match},
                {"$addFields": {
                    "custo_venda": {"$sum": {"$map": {
                        "input": {"$ifNull": ["$itens", []]},
                        "as":    "item",
                        "in": {"$multiply": [
                            {"$ifNull": ["$$item.preco_custo", 0]},
                            {"$ifNull": ["$$item.quantidade", 0]},
                        ]}
                    }}}
                }},
                {"$group": {
                    "_id": {
                        "ano": {"$year":  "$criado"},
                        "mes": {"$month": "$criado"},
                    },
                    "faturamento": {"$sum": "$total"},
                    "custo":       {"$sum": "$custo_venda"},
                }},
                {"$sort":  {"_id.ano": 1, "_id.mes": 1}},
                {"$limit": n},
            ]

            data = []
            for r in db.vendas.aggregate(pipeline):
                d   = r["_id"]
                fat = round(r["faturamento"], 2)
                cst = round(r["custo"],       2)
                data.append({
                    "mes":         f"{self.MESES_PT[d['mes']-1]}/{str(d['ano'])[2:]}",
                    "faturamento": fat,
                    "lucro":       round(fat - cst, 2),
                })

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)


class ProdutosMaisVendidosView(View):
    def get(self, request):
        try:
            db     = get_db()
            filtro = _filtro_base(request)
            limite = int(request.GET.get("limite", 10))

            pipeline = [
                {"$match": filtro},
                {"$unwind": {"path": "$itens", "preserveNullAndEmptyArrays": False}},
                {"$group": {
                    "_id":   "$itens.nome_produto",
                    "qtd":   {"$sum": {"$ifNull": ["$itens.quantidade", 0]}},
                    "total": {"$sum": {"$multiply": [
                        {"$ifNull": ["$itens.preco_custo", 0]},
                        {"$ifNull": ["$itens.quantidade", 0]},
                    ]}},
                }},
                {"$sort":  {"qtd": -1}},
                {"$limit": limite},
            ]

            data = [
                {"nome": r["_id"] or "—", "qtd": r["qtd"], "total": round(r["total"], 2)}
                for r in db.vendas.aggregate(pipeline)
            ]

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)


class ListaProdutosView(View):
    def get(self, request):
        try:
            db    = get_db()
            nomes = sorted([n for n in db.vendas.distinct("itens.nome_produto") if n])
            return JsonResponse(nomes, safe=False)
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)


class ListaStatusView(View):
    def get(self, request):
        try:
            db    = get_db()
            lista = sorted([s for s in db.vendas.distinct("status") if s])
            return JsonResponse(lista, safe=False)
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)
