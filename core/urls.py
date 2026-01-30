from django.urls import path, include
from . import views_public, views_admin
from django.contrib.auth import views as auth_views
from .views_public import LoginCustomView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    

#===========================================================================================================
# ENDPOINT - PROCESSO INICIAL
#===========================================================================================================
        
    # ======================
    # PÚBLICO
    # ======================
    path('', views_public.iniciar, name='iniciar'),
   
    path('pos-login/', views_public.pos_login, name='pos_login'),
    path('sair/', views_public.sair_view, name='sair'),

    # ======================
    # USUÁRIO COMUM
    # ======================
    path('usercomum/', views_public.home_public, name='home_public'),
    
    # ======================
    # ADMIN INPRIVY (SEU SISTEMA)
    # ======================
    path('painel/', views_admin.home_admin, name='home_admin'),

    # ======================
    # PÁGINAS INICIAIS
    # ======================
    path('termos/', views_public.termos, name='termos'),
    path('register/', views_public.register, name='register'),


#======================================================================================================================
# ENDPOINT - VERIFICA STATUS DO USER NO LOGIN
#======================================================================================================================

    path('login/', LoginCustomView.as_view(), name='login'),

#=========================================
# ENDPOINT - PERFIL
#=========================================

    path('perfil/', views_admin.listar_perfil, name='listar_perfil'),
    path('perfil/adicionar', views_admin.adicionar_perfil, name='adicionar_perfil'),
    path('perfil/editar/<int:id>', views_admin.editar_perfil, name='editar_perfil'),
    path('perfil/excluir/<int:id>', views_admin.excluir_perfil, name='excluir_perfil'),
    path('perfil/imprimir', views_admin.imprimir_perfil, name='imprimir_perfil'),    

# ======================
# ASSOCIADO (ADMIN)
# ======================
    
    path('associado/', views_admin.listar_associado_admin, name='listar_associado_admin'),
    path('associado/adicionar/', views_admin.adicionar_associado, name='adicionar_associado'),
    path('associado/editar/<int:id>/', views_admin.editar_associado, name='editar_associado'),
    path('associado/excluir/<int:id>/', views_admin.excluir_associado, name='excluir_associado'),
    path('associado/imprimir/', views_admin.imprimir_associado, name='imprimir_associado'),

# ======================
# ENDPOINT - TIMELINE
# ======================
    
    path('timeline/', views_public.timeline, name='timeline'),

# =================================
# ENDPOINT - TIMELINE - POSTAGEM
# =================================

    path('timeline/postar/', views_public.postar_timeline, name='postar_timeline'),

# =================================
# ENDPOINT - TIMELINE - MEU PERFIL
# =================================

    path('meu-perfil/', views_public.meu_perfil, name='meu_perfil'),

# =================================
# ENDPOINT - TIMELINE - FORUM
# =================================

    path('forum/', views_public.forum_home, name='forum_home'),
    path('categoria/<int:categoria_id>/', views_public.forum_categoria, name='forum_categoria'),
    path('categoria/<int:categoria_id>/novo/', views_public.forum_novo_topico, name='forum_novo_topico'),
    path('topico/<int:topico_id>/', views_public.forum_topico, name='forum_topico'),
    path('topico/<int:topico_id>/responder/', views_public.forum_responder, name='forum_responder'),
    path('topico/<int:topico_id>/editar/', views_public.forum_editar_topico, name='forum_editar_topico'),


    path('fotolog/', views_public.fotolog, name='fotolog'),

    path('timeline/comentar/<int:post_id>/', views_public.comentar_timeline, name='comentar_timeline'),

    path('conteudo/', views_public.conteudo, name='conteudo'),

    path('associados/', views_public.listar_associado, name='listar_associado'),

    path('seguir/<int:associado_id>/', views_public.seguir_associado, name='seguir'),
    path('deixar/<int:associado_id>/', views_public.deixar_de_seguir, name='deixar'),

    path('associado/<int:associado_id>/seguidores/', views_public.meus_seguidores_seguindo, name='meus_seguidores_seguindo'),

    path('eventos/criar/', views_public.criar_evento, name='criar_evento'),

    path('eventos/', views_public.lista_eventos, name='lista_eventos'),
    path('eventos/presenca/<int:evento_id>/', views_public.toggle_presenca, name='toggle_presenca'),

    path('agenda/', views_public.agenda, name='agenda'),

    path('grupos/criar/', views_public.criar_grupo, name='criar_grupo'),
    path('grupos/<int:id>/', views_public.detalhe_grupo, name='detalhe_grupo'),
    path('grupos/', views_public.listar_grupos, name='listar_grupos'),
    path('grupos/<int:id>/editar/', views_public.editar_grupo, name='editar_grupo'),
    path('grupos/<int:id>/excluir/', views_public.excluir_grupo, name='excluir_grupo'),

    path('mensagens/', views_public.inbox_mensagens, name='inbox_mensagens'),
    path('mensagens/enviar/', views_public.enviar_mensagem, name='enviar_mensagem'),
    path('mensagens/<int:id>/', views_public.detalhe_mensagem, name='detalhe_mensagem'),

    path('planos/', views_public.planos, name='planos'),
    path('planos/<int:plano_id>/', views_public.assinar_plano, name='assinar_plano'),

    path('pagar_assinatura/<int:assinatura_id>/', views_public.pagar_assinatura, name='pagar_assinatura'),

    # URLs de retorno do pagamento
    path('assinaturas/<int:assinatura_id>/sucesso/', views_public.assinatura_sucesso, name='assinatura_sucesso'),
    path('assinaturas/<int:assinatura_id>/falha/', views_public.assinatura_falha, name='assinatura_falha'),
    path('assinaturas/<int:assinatura_id>/pendente/', views_public.assinatura_pendente, name='assinatura_pendente'),

    path('webhook/mercadopago/', views_public.webhook_mercadopago, name='webhook_mercadopago'),

    
    


           
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)