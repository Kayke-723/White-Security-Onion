from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
from .models import Log, Process
from django.contrib.auth.models import User
from datetime import datetime
import logging

logger = logging.getLogger('core')


def registrar_log(message, user=None, level='INFO'):
    """
    Registra evento:
    - grava no arquivo via logging (handler definido no settings)
    - grava no banco na tabela core_log
    """
   
    if level == 'INFO':
        logger.info(message)
    elif level == 'WARNING':
        logger.warning(message)
    elif level == 'ERROR':
        logger.error(message)
    else:
        logger.debug(message)

    # gravar no banco
    log = Log(level=level, message=message, user=user if isinstance(user, User) else None)
    log.save()

def index(request):
    """
    Rota '/' - página inicial / dashboard.
    Mostra links para os módulos e, se autenticado, o usuário.
    """
    return render(request, "core/index.html", {"user": request.user if request.user.is_authenticated else None})


def signup_view(request):
    """
    Exibe o formulário de cadastro e cria usuário.
    Usa SignUpForm que lida com hashing de senha via UserCreationForm.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  
            registrar_log(f"Novo usuário cadastrado: {user.username}", user=user)
            login(request, user)  
            messages.success(request, "Cadastro realizado com sucesso.")
            return redirect('index')
        else:
            messages.error(request, "Erro no cadastro. Verifique os campos.")
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})


# Login
def login_view(request):
    """
    Trata login: autentica e inicia sessão.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)  # verifica credenciais
        if user is not None:
            login(request, user) 
            registrar_log(f"Login realizado: {user.username}", user=user)
            return redirect('index')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
            registrar_log(f"Tentativa de login falha: {username}", level='WARNING')
    return render(request, 'core/login.html')


# Logout
def logout_view(request):
    """
    Encerra sessão do usuário.
    """
    username = request.user.username if request.user.is_authenticated else 'anon'
    logout(request)
    registrar_log(f"Logout: {username}")
    return redirect('index')


@login_required
def conversao_view(request):
    """
    Recebe um valor e a base desejada e realiza conversões entre decimal/bin/hex/oct.
    """
    result = None
    if request.method == 'POST':
        value = request.POST.get('value', '').strip()
        base = request.POST.get('base') 
        try:
     
            if base == 'dec':
                num = int(value, 10)
            elif base == 'bin':
                num = int(value, 2)
            elif base == 'hex':
                num = int(value, 16)
            elif base == 'oct':
                num = int(value, 8)
            else:
                raise ValueError("Base inválida")

            result = {
                'decimal': str(num),
                'binary': bin(num)[2:],      
                'hex': hex(num)[2:].upper(), 
                'oct': oct(num)[2:]          
            }
            registrar_log(f"Conversão efetuada por {request.user.username}: {value} em {base} -> {result}", user=request.user)
        except Exception as e:
            messages.error(request, f"Erro na conversão: {e}")
            registrar_log(f"Erro conversão: {value} base={base} - {e}", user=request.user, level='ERROR')
    return render(request, 'core/conversao.html', {'result': result})




