from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
import json

from .models import Produto


def documento_para_dict(doc):
    dados = doc.to_mongo().to_dict()
    dados['id'] = str(dados.pop('_id'))

    for campo, valor in dados.items():
        if isinstance(valor, datetime):
            dados[campo] = valor.isoformat()

    return dados


@method_decorator(csrf_exempt, name='dispatch')
class ProdutoListCreate(View):

    def get(self, request):
        try:
            categoria = request.GET.get('categoria')
            status = request.GET.get('status', 'ativo')
            busca = request.GET.get('busca', '').strip()

            produtos = Produto.objects.filter(status=status)

            if categoria:
                produtos = produtos.filter(categoria=categoria)

            if busca:
                produtos_filtrados = []

                for produto in produtos:
                    nome = produto.nome or ''
                    categoria_produto = produto.categoria or ''
                    lote = produto.lote or ''

                    if (
                        busca.lower() in nome.lower()
                        or busca.lower() in categoria_produto.lower()
                        or busca.lower() in lote.lower()
                    ):
                        produtos_filtrados.append(produto)

                produtos = produtos_filtrados

            dados = [documento_para_dict(produto) for produto in produtos]

            return JsonResponse({
                'total': len(dados),
                'data': dados
            })

        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)

    def post(self, request):
        try:
            body = json.loads(request.body)

            produto = Produto(
                nome=body.get('nome'),
                descricao=body.get('descricao', ''),
                preco_custo=float(body.get('preco_custo', 0)),
                preco_venda=float(body.get('preco_venda', 0)),
                estoque=int(body.get('estoque', 0)),
                estoque_minimo=int(body.get('estoque_minimo', 5)),
                unidade=body.get('unidade', 'un'),
                categoria=body.get('categoria', 'medicamento'),
                lote=body.get('lote', ''),
                status=body.get('status', 'ativo'),
            )

            if body.get('validade'):
                produto.validade = datetime.strptime(body['validade'][:10], '%Y-%m-%d')

            produto.save()

            return JsonResponse({
                'mensagem': 'Produto criado com sucesso!',
                'id': str(produto.id)
            }, status=201)

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
            body = json.loads(request.body)
            produto = Produto.objects.get(id=id)

            campos = [
                'nome',
                'descricao',
                'preco_custo',
                'preco_venda',
                'estoque',
                'estoque_minimo',
                'unidade',
                'categoria',
                'lote',
                'status',
            ]

            for campo in campos:
                if campo in body:
                    valor = body[campo]

                    if campo in ['preco_custo', 'preco_venda']:
                        valor = float(valor)

                    if campo in ['estoque', 'estoque_minimo']:
                        valor = int(valor)

                    setattr(produto, campo, valor)

            if body.get('validade'):
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
            todos = Produto.objects.all()
            ativos = Produto.objects.filter(status='ativo')
            inativos = Produto.objects.filter(status='inativo')

            criticos = 0

            for produto in ativos:
                if produto.estoque <= produto.estoque_minimo:
                    criticos += 1

            return JsonResponse({
                'total': todos.count(),
                'ativos': ativos.count(),
                'inativos': inativos.count(),
                'criticos': criticos
            })

        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)


class BiEstoqueView(View):

    def get(self, request):
        try:
            produtos = Produto.objects.filter(status='ativo')

            criticos = []

            for produto in produtos:
                if produto.estoque <= produto.estoque_minimo:
                    criticos.append({
                        '_id': str(produto.id),
                        'id': str(produto.id),
                        'nome': produto.nome,
                        'estoque': produto.estoque,
                        'estoque_minimo': produto.estoque_minimo,
                        'unidade': produto.unidade,
                    })

            return JsonResponse({
                'criticos': criticos
            })

        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)