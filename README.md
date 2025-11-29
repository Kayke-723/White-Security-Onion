# White Security — Projeto A3 (Simulador)

**Resumo rápido**
White Security é um protótipo web (Django) com interfaces experimentais de interação por gesto (MediaPipe) e ferramenta didática de criptografia. O objetivo é demonstrar técnicas interativas de reconhecimento de mãos e aplicações simples de segurança (criptografia simétrica) com uma interface moderna.

## Funcionalidades principais
1. **Login por gesto** — usuário cadastra um gesto (keypoints da mão) e pode autenticar usando a webcam.
2. **Criptografia de mensagem** — interface para criptografar/descriptografar mensagens com uma secretKey definida pelo usuário (uso didático).

## Como rodar (resumido)
1. Crie e ative um virtualenv:
```bash
python -m venv .venv
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate    # Windows
```
2. Instale dependências:
```bash
pip install -r requirements.txt
```
3. Rode migrations:
```bash
python manage.py migrate
```
4. Rode o servidor:
```bash
python manage.py runserver
```
Abra `http://127.0.0.1:8000/`.

## Notes
- Configure MEDIA_ROOT/MEDIA_URL em settings.py (já presente).
- Não comite `SECRET_KEY` em repositórios públicos. Aprendi da pior forma.
