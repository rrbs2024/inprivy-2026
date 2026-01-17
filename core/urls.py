from django.contrib import admin
from django.urls import path, include
from . import views_public, views_admin
from django.contrib.auth import views as auth_views
from django.core.exceptions import PermissionDenied


urlpatterns = [
    
    
#======================================================================================================================
# ENDPOINT - PROCESSO INICIAL
#======================================================================================================================
        
    # ======================
    # PÚBLICO
    # ======================
    path('', views_public.iniciar, name='iniciar'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('pos-login/', views_public.pos_login, name='pos_login'),
    path('sair/', views_public.sair_view, name='sair'),

    # ======================
    # USUÁRIO COMUM
    # ======================
    path('home/', views_public.home_public, name='home_public'),

    # ======================
    # ADMIN INPRIVY (SEU SISTEMA)
    # ======================
    path('painel/', views_admin.home_admin, name='home_admin'),

    # ======================
    # PÁGINAS INICIAIS
    # ======================
    path('termos/', views_public.termos, name='termos'),
    path('register/', views_public.register, name='register'),

    # ======================
    # ASSOCIADO (ADMIN)
    # ======================
    path('associado/', views_admin.listar_associado, name='listar_associado'),
    path('associado/adicionar/', views_admin.adicionar_associado, name='adicionar_associado'),
    path('associado/editar/<int:id>/', views_admin.editar_associado, name='editar_associado'),
    path('associado/excluir/<int:id>/', views_admin.excluir_associado, name='excluir_associado'),
    path('associado/imprimir/', views_admin.imprimir_associado, name='imprimir_associado'),





    
    
]