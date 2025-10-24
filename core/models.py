from django.db import models


from django.db import models
from django.contrib.auth.models import User


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




