from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('conversao/', views.conversao_view, name='conversao'),
]
