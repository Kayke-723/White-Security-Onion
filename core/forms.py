# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Formulário de registro estendido
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)  # obrigar email

    class Meta:
        model = User                # cria instância do modelo User
        fields = ('username', 'email', 'password1', 'password2')  # campos exibidos

    # validação extra: garantir que o email seja único
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Esse e-mail já está em uso.")
        return email
