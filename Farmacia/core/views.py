from django.shortcuts import render

def index(request):
    # Passamos uma mensagem de teste para o HTML
    contexto = {
        'mensagem': 'Dados enviados da views.py com sucesso!'
    }
    return render(request, 'core/index.html', contexto)