# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True) 

    class Meta:
        model = User               
        fields = ('username', 'email', 'password1', 'password2') 
        
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica o mesmo estilo a todos os campos do formulário
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'border border-white rounded-2xl p-2 w-64 focus:outline-none focus:ring-2 focus:ring-blue-500 text-white bg-transparent placeholder-gray-300'
            })
  
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Esse e-mail já está em uso.")
        return email
