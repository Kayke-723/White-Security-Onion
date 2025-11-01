from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, UpdateProfileForm
from .models import Log, Process
from django.contrib.auth.models import User
from datetime import datetime
import logging
from django.http import JsonResponse
import json
from .models import Gesto
from django.views.decorators.csrf import csrf_exempt





def cadastro_gesto(request):
    return render(request, 'core/gesto/cadastro_gesto.html')

def sucesso(request):
    return render(request, 'core/gesto/sucesso.html')

def login_gesto(request):
    return render(request, 'core/gesto/login_gesto.html')


@csrf_exempt
def salvar_gesto(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        keypoints = data.get("keypoints")

        if not username or not keypoints:
            return JsonResponse({"erro": "Dados inválidos"}, status=400)

        # Criar ou obter usuário (não altera senha aqui)
        user, _ = User.objects.get_or_create(username=username)
        gesto, criado = Gesto.objects.update_or_create(
            user=user,
            defaults={"keypoints": keypoints}
        )

        return JsonResponse({"mensagem": "Gesto salvo com sucesso!", "created": criado})

    return JsonResponse({"erro": "Método inválido"}, status=405)

import math

@csrf_exempt
def valida_gesto(request):
    """
    Verifica se o usuário existe e valida o gesto salvo no banco.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método inválido'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

    username = data.get('username')
    incoming_kps = data.get('keypoints')

    # 🔹 Verificar se o nome foi informado
    if not username:
        return JsonResponse({'status': 'error', 'message': 'Nome de usuário não informado'}, status=400)

    # 🔹 Verificar se o usuário existe no banco
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Usuário não encontrado'}, status=404)

    # 🔹 Verificar se o usuário possui gesto cadastrado
    gesto = Gesto.objects.filter(user=user).first()
    if not gesto:
        return JsonResponse({'status': 'fail', 'message': 'Usuário não possui gesto cadastrado'}, status=404)

    # 🔹 Verificar se foram enviados keypoints
    if not incoming_kps:
        return JsonResponse({'status': 'error', 'message': 'Nenhum gesto foi detectado'}, status=400)

    saved_kps = gesto.keypoints

    # 🔹 Comparar o gesto salvo com o gesto atual
    def avg_distance(a, b):
        if not (isinstance(a, list) and isinstance(b, list) and len(a) == len(b)):
            return float('inf')
        total = 0.0
        for pa, pb in zip(a, b):
            try:
                dx = float(pa[0]) - float(pb[0])
                dy = float(pa[1]) - float(pb[1])
                dz = (float(pa[2]) - float(pb[2])) if len(pa) > 2 and len(pb) > 2 else 0.0
                total += math.sqrt(dx*dx + dy*dy + dz*dz)
            except Exception:
                return float('inf')
        return total / len(a)

    avg_dist = avg_distance(saved_kps, incoming_kps)
    THRESHOLD = 0.05

    if avg_dist < THRESHOLD:
        return JsonResponse({'status': 'ok', 'message': 'Login autorizado', 'distance': avg_dist})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Gesto não corresponde', 'distance': avg_dist})



logger = logging.getLogger('core')

@login_required
def profile_view(request):
    return render(request, 'core/profile.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        old_user = request.user  # guarda o usuário atual (antes das alterações)
        old_username = old_user.username
        old_email = old_user.email

        form = UpdateProfileForm(request.POST, instance=old_user)
        if form.is_valid():
            user = form.save()

            # Verifica se o nome foi alterado
            if old_username != user.username:
                registrar_log(f"{user} alterou o nome de '{old_username}' para '{user.username}'", user=user)

            # Verifica se o e-mail foi alterado
            if old_email != user.email:
                registrar_log(f"{user} alterou o e-mail de '{old_email}' para '{user.email}'", user=user)

            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, 'update_profile.html', {'form': form})



def terms_view(request):
    return render(request, 'core/terms_conditions.html')

def about_view(request):
    return render(request, 'core/about.html')

def home_view(request):
    return render(request, 'core/home.html')


def registrar_log(message, user=None, level='INFO'):
  
   
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
    return render(request,"core/index.html", {"user": request.user if request.user.is_authenticated else redirect('login')})

def signup_view(request):
    
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
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)  # verifica credenciais
        if user is not None:
            login(request, user) 
            registrar_log(f"Login realizado: {user.username}", user=user)
            return redirect('home')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
            registrar_log(f"Tentativa de login falha: {username}", level='WARNING')
    return render(request, 'core/login.html')



def logout_view(request):
    
    username = request.user.username if request.user.is_authenticated else 'anon'
    logout(request)
    registrar_log(f"Logout: {username}")
    return redirect('index')


@login_required
def conversao_view(request):
    
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




