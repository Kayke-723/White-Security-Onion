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
import base64
from cryptography.fernet import Fernet


@csrf_exempt
def criptografar_mensagem(request):
    """
    Recebe uma mensagem e uma chave secreta, e devolve a mensagem criptografada.
    """
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método inválido'}, status=405)

    try:
        data = json.loads(request.body)
        mensagem = data.get('mensagem')
        secret = data.get('secretKey')

        if not mensagem or not secret:
            return JsonResponse({'erro': 'Mensagem e chave são obrigatórias'}, status=400)

        # 🔐 Gera chave baseada na secretKey
        key = base64.urlsafe_b64encode(secret.ljust(32)[:32].encode())
        f = Fernet(key)

        encrypted = f.encrypt(mensagem.encode()).decode()
        return JsonResponse({'mensagem_criptografada': encrypted})

    except Exception as e:
        return JsonResponse({'erro': f'Erro ao criptografar: {str(e)}'}, status=500)


@csrf_exempt
def descriptografar_mensagem(request):
    """
    Recebe a mensagem criptografada e a chave, devolve o texto original.
    """
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método inválido'}, status=405)

    try:
        data = json.loads(request.body)
        criptografada = data.get('mensagem')
        secret = data.get('secretKey')

        if not criptografada or not secret:
            return JsonResponse({'erro': 'Mensagem e chave são obrigatórias'}, status=400)

        key = base64.urlsafe_b64encode(secret.ljust(32)[:32].encode())
        f = Fernet(key)

        decrypted = f.decrypt(criptografada.encode()).decode()
        return JsonResponse({'mensagem_original': decrypted})

    except Exception as e:
        return JsonResponse({'erro': f'Erro ao descriptografar: {str(e)}'}, status=500)
    

def help_gesto_view(request):
    return render(request, 'core/gesto/help_gesto.html')

def termos_view(request):
    return render(request, 'core/termos.html')

def cadastro_gesto(request):
    return render(request, 'core/gesto/cadastro_gesto.html')

def sucesso(request):
    return render(request, 'core/gesto/sucesso.html')

def login_gesto(request):
    return render(request, 'core/gesto/login_gesto.html')


@csrf_exempt
def salvar_gesto(request):
    """
    Cadastra um novo usuário com gesto associado.
    - Se o usuário não existir, ele é criado automaticamente.
    - Se já existir e tiver gesto, o sistema bloqueia o novo cadastro.
    """
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método inválido'}, status=405)

    # 🔹 Lê o corpo da requisição JSON
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    username = data.get('username')
    email = data.get('email')
    keypoints = data.get('keypoints')

    if not username or not email or not keypoints:
        return JsonResponse({'erro': 'Campos obrigatórios ausentes'}, status=400)

    # 🔹 Verifica se já existe o usuário
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email}
    )

    # Se o usuário já existia, verifica se tem gesto
    if not created:
        if Gesto.objects.filter(user=user).exists():
            return JsonResponse({
                'erro': 'Este usuário já possui um gesto cadastrado.'
            }, status=400)

    # 🔹 Cria e associa o gesto
    Gesto.objects.create(user=user, keypoints=keypoints)

    # Retorno amigável
    mensagem = (
        'Usuário e gesto cadastrados com sucesso!'
        if created else
        'Gesto cadastrado com sucesso!'
    )

    return JsonResponse({'mensagem': mensagem})

import math

@csrf_exempt
def valida_gesto(request):
    """
    Validação estrita de gesto:
    - aceita apenas POST com 'username' e 'keypoints' (lista de [x,y,z])
    - normaliza por wrist (landmark 0) e por escala (max dist -> 1)
    - compara ponto-a-ponto e retorna ok somente se avg_dist < THRESHOLD
    - autentica com login(request, user) em caso de sucesso
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método inválido'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

    username = data.get('username')
    incoming = data.get('keypoints')

    if not username:
        return JsonResponse({'status': 'error', 'message': 'Nome de usuário não informado'}, status=400)

    # Requer keypoints (não aceitar fallback por texto)
    if not incoming or not isinstance(incoming, list):
        return JsonResponse({'status': 'error', 'message': 'Keypoints não fornecidos'}, status=400)

    # Recupera usuário e gesto salvo
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Usuário não encontrado'}, status=404)

    gesto = getattr(user, 'gesto', None)  # usa related_name se definido
    if not gesto:
        # tenta filtro fallback
        gesto = Gesto.objects.filter(user=user).first()
    if not gesto:
        return JsonResponse({'status': 'fail', 'message': 'Usuário não possui gesto cadastrado'}, status=404)

    saved = gesto.keypoints

    # ---- Funções utilitárias ----
    def to_triplets(points):
        trip = []
        for p in points:
            if isinstance(p, dict):
                x = float(p.get('x', 0.0))
                y = float(p.get('y', 0.0))
                z = float(p.get('z', 0.0))
            else:
                # assume lista/tuple [x,y,z]
                try:
                    x = float(p[0])
                    y = float(p[1])
                    z = float(p[2]) if len(p) > 2 else 0.0
                except Exception:
                    return None
            trip.append((x, y, z))
        return trip

    a = to_triplets(saved)
    b = to_triplets(incoming)

    if not a or not b:
        return JsonResponse({'status': 'error', 'message': 'Formato de keypoints inválido'}, status=400)

    # requer número mínimo de pontos (ex: 21 para MediaPipe Hands)
    MIN_POINTS = 10
    if len(a) < MIN_POINTS or len(b) < MIN_POINTS:
        return JsonResponse({'status': 'error', 'message': 'Keypoints insuficientes'}, status=400)

    # Trunca ou expande para o menor comprimento — preferimos exigir igual comprimento idealmente
    n = min(len(a), len(b))
    a = a[:n]
    b = b[:n]

    # Normalizar com referência no wrist (landmark 0 se existir)
    def normalize_by_origin_scale(points):
        # escolhe origin como ponto 0 (se existir), senão centro médio
        if len(points) > 0:
            ox, oy, oz = points[0]
        else:
            ox = sum(p[0] for p in points) / len(points)
            oy = sum(p[1] for p in points) / len(points)
            oz = sum(p[2] for p in points) / len(points)
        centered = [ (x-ox, y-oy, z-oz) for (x,y,z) in points ]
        # escala por maior distância ao origin (evita divisão por zero)
        maxd = max(math.sqrt(x*x + y*y + z*z) for x,y,z in centered)
        scale = maxd if maxd > 1e-8 else 1.0
        normalized = [ (x/scale, y/scale, z/scale) for x,y,z in centered ]
        return normalized

    a_norm = normalize_by_origin_scale(a)
    b_norm = normalize_by_origin_scale(b)

    # calcula distância média
    total = 0.0
    for pa, pb in zip(a_norm, b_norm):
        dx = pa[0] - pb[0]
        dy = pa[1] - pb[1]
        dz = pa[2] - pb[2]
        total += math.sqrt(dx*dx + dy*dy + dz*dz)
    avg_dist = total / n

    # ajuste fino do threshold: valores razoáveis começam ~0.05-0.18 dependendo do pré-processamento
    THRESHOLD = 0.12

    logger.info("valida_gesto: user=%s avg_dist=%.6f n=%d", username, avg_dist, n)

    if avg_dist < THRESHOLD:
        # autentica o usuário (cria sessão)
        login(request, user)
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

    return render(request, 'core/profile.html', {'form': form})



def terms_view(request):
    return render(request, 'core/terms_conditions.html')

def about_view(request):
    return render(request, 'core/about.html')

@login_required
def home_view(request):
    return render(request, 'core/home.html')

@login_required
def msgCriptografia_view(request):
    return render(request, 'core/funcoes/Mensagem/msgCriptografia.html')


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
    return render(request, 'core/funcoes/conversao/conversao.html', {'result': result})




