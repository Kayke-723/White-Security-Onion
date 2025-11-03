from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class Gesto(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="gesto",
        verbose_name="Usuário"
    )
    keypoints = models.JSONField(verbose_name="Dados do gesto")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gesto de {self.user.username}"
    
class Gesto(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    keypoints = models.JSONField()  # Armazena os 21 pontos (x, y, z)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gesto de {self.user.username}"
    
class Log(models.Model):
   
    timestamp = models.DateTimeField(auto_now_add=True) 
    level = models.CharField(max_length=20, default='INFO')  
    message = models.TextField()  # mensagem de log
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # usuário opcional

    def __str__(self):
        return f"[{self.timestamp}] {self.level}: {self.message[:50]}"



class Process(models.Model):
    name = models.CharField(max_length=100)         
    burst_time = models.IntegerField(default=1)     
    priority = models.IntegerField(default=1)       
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (burst={self.burst_time}, prio={self.priority})"




