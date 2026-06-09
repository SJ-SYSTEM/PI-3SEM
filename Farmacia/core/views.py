from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


def index(request):
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()

        usuario = User.objects.filter(email=email).first()

        if usuario is not None:
            user = authenticate(request, username=usuario.username, password=senha)

            if user is not None:
                login(request, user)
                return redirect('dashboard')

        messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'core/login.html')


def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        usuario = request.POST.get('usuario', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()

        if User.objects.filter(username=usuario).exists():
            messages.error(request, 'Esse usuário já existe.')
            return render(request, 'core/cadastro.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Esse e-mail já está cadastrado.')
            return render(request, 'core/cadastro.html')

        User.objects.create_user(
            username=usuario,
            email=email,
            password=senha,
            first_name=nome
        )

        messages.success(request, 'Usuário cadastrado com sucesso!')
        return redirect('login')

    return render(request, 'core/cadastro.html')


@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')
