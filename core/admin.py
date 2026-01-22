from django.contrib import admin
from django.db.models.functions import Length
from .models import Perfil, UsuarioPerfil, StatusAssociacao, TipoAssociado, TipoPlano, Genero, StatusAssociado, ForumCategoria

# Register your models here.

#===============================================================================================
admin.site.register(UsuarioPerfil)

#===============================================================================================
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil_razaosocial', 'perfil_nomefantasia', 'perfil_cnpj', 'perfil_inscest', 'perfil_inscmun', 'perfil_email', 'perfil_endereco', 'perfil_numero', 'perfil_complemento','perfil_bairro', 'perfil_cidade', 'perfil_cep', 'perfil_uf', 'perfil_telefone1', 'perfil_telefone2', 'perfil_observacoes', 'perfil_datafundacao', 'perfil_datacadastro', 'usuario')
    list_filter = ('perfil_uf',)
    search_fields = ('id', id)
    
    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(cod_len=Length('id'))
                .order_by('cod_len','id'))
#===============================================================================================    
@admin.register(StatusAssociacao)
class StatusAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'statusassociacao_descricao')
    list_filter = ()
    search_fields = ('id', id)
    
    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(cod_len=Length('id'))
                .order_by('cod_len','id'))

#===============================================================================================

#===============================================================================================    
@admin.register(TipoAssociado)
class TipoAssociadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipoassociado_descricao')
    list_filter = ()
    search_fields = ('id', id)
    
    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(cod_len=Length('id'))
                .order_by('cod_len','id'))

#===============================================================================================

#===============================================================================================    
@admin.register(TipoPlano)
class TipoPlanoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipoplano_descricao')
    list_filter = ()
    search_fields = ('id', id)
    
    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(cod_len=Length('id'))
                .order_by('cod_len','id'))

#===============================================================================================

#===============================================================================================    
@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('id', 'genero_descricao')
    list_filter = ()
    search_fields = ('id', id)
    
    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(cod_len=Length('id'))
                .order_by('cod_len','id'))

#===============================================================================================

#===============================================================================================    
@admin.register(StatusAssociado)
class StatusAssociadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao')
    list_filter = ()
    search_fields = ('id', id)
    
    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(cod_len=Length('id'))
                .order_by('cod_len','id'))

#===============================================================================================

@admin.register(ForumCategoria)
class ForumCategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'descricao')
    list_filter = ()
    search_fields = ('id', id)
    
    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(cod_len=Length('id'))
                .order_by('cod_len','id'))

#===============================================================================================