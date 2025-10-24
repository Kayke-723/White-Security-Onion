from django.contrib import admin


from django.contrib import admin
from .models import Log, Process

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'message', 'user')
    list_filter = ('level', 'timestamp')

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'burst_time', 'priority', 'created_at')


