from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('conversao/', views.conversao_view, name='conversao'),
    path('about/', views.about_view, name='about'),
    path('home/', views.home_view, name='home'),
    path('terms/', views.terms_view, name='terms_conditions'),
    path('profile/', views.profile_view, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('login_gesto', views.login_gesto, name='login_gesto'),
    path('api/valida_gesto/', views.valida_gesto, name='valida_gesto'),
    path('cadastro_gesto', views.cadastro_gesto, name='cadastro_gesto'),
    path('salvar_gesto/', views.salvar_gesto, name='salvar_gesto'),
    path('sucesso/', views.sucesso, name='sucesso'),

]
