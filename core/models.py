from django.db import models
from django.contrib.auth.models import User

# Create your models here.


#=============================================================================================================
# CLASSE MODEL - ADMIN - PERFIL
#=============================================================================================================

class Perfil(models.Model):
    perfil_razaosocial = models.CharField("Razão Social", max_length=100)
    perfil_nomefantasia = models.CharField("Nome de Fantasia",max_length=30)
    perfil_cnpj = models.CharField("CNPJ", max_length=18)
    perfil_inscest = models.CharField("Inscrição Estadual", max_length=30, blank=True, null=True)
    perfil_inscmun = models.CharField("Incrição Municipal", max_length=30, blank=True, null=True)
    perfil_email = models.CharField("E-mail", max_length=50)
    perfil_endereco = models.CharField("Endereço", max_length=100)
    perfil_numero = models.CharField("Número", max_length=20, blank=True, null=True)
    perfil_complemento = models.CharField("Complemento", max_length=30, blank=True, null=True)
    perfil_bairro = models.CharField("Bairro", max_length=50)
    perfil_cidade = models.CharField("Cidade", max_length=50)
    perfil_cep = models.CharField("CEP", max_length=9)
    perfil_uf = models.CharField("UF", max_length=2)
    perfil_telefone1 = models.CharField("Telefone-1", max_length=20)
    perfil_telefone2 = models.CharField("Telefone-2", max_length=20)
    perfil_observacoes = models.TextField("Observações", blank=True, null=True)
    perfil_datafundacao = models.DateField("Data da Fundação")
    perfil_datacadastro = models.DateTimeField("Data do Cadastro", auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Usuário")

    def __str__(self):
        return self.perfil_razaosocial 
    
    class Meta:
        verbose_name = "Perfil(Empresa)"           # Nome no singular no admin
        verbose_name_plural = "Perfis(Empresas)"   # Nome no plural no admin

#===========================================================================================================================#

# =====================================
# CLASSE MODEL - ADMIN - USUÁRIO-PERFIL
# =====================================

class UsuarioPerfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "Usuário x Perfil"           # Nome no singular no admin
        verbose_name_plural = "Usuários X Perfis"  # Nome no plural no admin

#===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - ADMIN - Status da Associação
#=============================================================================================================

class StatusAssociacao(models.Model):
    statusassociacao_descricao = models.CharField("Descrição", max_length=30)
    
    def __str__(self):
        return self.statusassociacao_descricao 
    
    class Meta:
        verbose_name = "Status Associação"           # Nome no singular no admin
        verbose_name_plural = "Status Associações"  # Nome no plural no admin
    
#===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - ADMIN - Tipo de Associado
#=============================================================================================================

class TipoAssociado(models.Model):
    tipoassociado_descricao = models.CharField("Descrição", max_length=30)
    
    def __str__(self):
        return self.tipoassociado_descricao 
    
    class Meta:
        verbose_name = "Tipo de Associado"           # Nome no singular no admin
        verbose_name_plural = "Tipos de Associados"  # Nome no plural no admin
    
#===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - ADMIN - Tipo de Plano
#=============================================================================================================

class TipoPlano(models.Model):
    tipoplano_descricao = models.CharField("Descrição", max_length=30)
    
    def __str__(self):
        return self.tipoplano_descricao 
    
    class Meta:
        verbose_name = "Tipo de Plano"           # Nome no singular no admin
        verbose_name_plural = "Tipos de Planos"  # Nome no plural no admin
    
#===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - ADMIN - Gênero
#=============================================================================================================

class Genero(models.Model):
    genero_descricao = models.CharField("Descrição", max_length=30)
    
    def __str__(self):
        return self.genero_descricao     
    class Meta:
        verbose_name = "Gênero"           # Nome no singular no admin
        verbose_name_plural = "Gêneros"  # Nome no plural no admin
    
#===========================================================================================================================#

#======================================================================================================================
# CLASSE MODEL - USERS-CLONE
#======================================================================================================================
class UserClone(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    apelido = models.CharField(max_length=50)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    bio = models.TextField(blank=True)
    is_admin = models.BooleanField(default=False)
    tri_indica = models.IntegerField(null=True, blank=True)
    tipoplano = models.ForeignKey(TipoPlano, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Tipo de Plano")
    status = models.ForeignKey(StatusAssociacao, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Status da Associação")

    def __str__(self):
        return self.apelido
#======================================================================================================================
    
#======================================================================================================================
# CLASSE MODEL - ADMIN - STATUS DO ASSOCIADO
#======================================================================================================================
class StatusAssociado(models.Model):   
    descricao = models.CharField(max_length=30)    

    def __str__(self):
        return self.descricao    
    class Meta:
        verbose_name = "Status Associado"           # Nome no singular no admin
        verbose_name_plural = "Status Associados"  # Nome no plural no admin
#======================================================================================================================

#=============================================================================================================
# CLASSE MODEL - ASSOCIADO
#=============================================================================================================

class Associado(models.Model):    
    associado_nome = models.CharField("Nome do Associado",max_length=100)   
    tipoassociado = models.ForeignKey(TipoAssociado, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Tipo Associado")  
    associado_email = models.CharField("E-mail", max_length=50)    
    associado_telefone = models.CharField("Telefone-2", max_length=20)
    associado_uf = models.CharField("UF do Associado", max_length=2, null=True, blank=True)
    tipoplano = models.ForeignKey(TipoPlano, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Tipo do Plano")
    associado_datacadastro = models.DateTimeField("Data do Cadastro", auto_now_add=True)  
    #================================================================================================================================
    associado_observacoes = models.TextField("Observações", blank=True, null=True)    
    associado_codigo = models.CharField("Código Interno", max_length=30, blank=True, null=True)  
    associado_avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  
    status = models.ForeignKey(StatusAssociacao, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Status Associação")
    usuarioadm = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.associado_nome    
    
#===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - ASSOCIADO x PADRINHO
#=============================================================================================================

class AssociadoPadrinho(models.Model):        
    indicado  = models.OneToOneField(Associado, on_delete=models.CASCADE, related_name='padrinhos')  # 1 associado = 1 conjunto de padrinhos
    padrinho1 = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='padrinho1_de')
    padrinho2 = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='padrinho2_de')
    padrinho3 = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='padrinho3_de')
    assocpadrinho_datacadastro = models.DateTimeField("Data do Cadastro", auto_now_add=True)      
    assocpadrinho_observacoes = models.TextField("Observações", blank=True, null=True)
    usuarioadm = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Usuário")
    
    
    def __str__(self):
        return f"{self.indicado.nome} - Padrinhos: {self.padrinho1.nome}, {self.padrinho2.nome}, {self.padrinho3.nome}"
        
#===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - ASSOCIADO x AMIGO
#=============================================================================================================

class AssociadoAmigo(models.Model):        
    origem  = models.OneToOneField(Associado, on_delete=models.CASCADE, related_name='amigo_origem')  # 1 associado = 1 conjunto de padrinhos
    amigo = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='meu_amigo')    
    assocamigo_datacadastro = models.DateTimeField("Data do Cadastro", auto_now_add=True)      
    assocamigo_observacoes = models.TextField("Observações", blank=True, null=True)
    usuarioadm = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Usuário")
    
    
    def __str__(self):
        return f"{self.origem.nome} - Amigo: {self.amigo.nome}"
        
#===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - ASSOCIADO x APADRINHADO
#=============================================================================================================

class AssociadoApadrinhado(models.Model):        
    padrinho  = models.OneToOneField(Associado, on_delete=models.CASCADE, related_name='padrinho')  # 1 associado = 1 conjunto de padrinhos
    apadrinhado = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='apadrinhado')    
    assocapad_datacadastro = models.DateTimeField("Data do Cadastro", auto_now_add=True)      
    assocapad_observacoes = models.TextField("Observações", blank=True, null=True)
    usuarioadm = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Usuário")
    
    
    def __str__(self):
        return f"{self.padrinho.nome} - Amigo: {self.apadrinhado.nome}"
        
#===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - MENSAGEM ASSOCIADO 
#=============================================================================================================
class MensagemAssociado(models.Model):
    remetente = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='mensagens_enviadas'
    )
    destinatario = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='mensagens_recebidas'
    )
    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"De {self.remetente} para {self.destinatario}"
    #===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - TIMELINE 
#=============================================================================================================

class TimelinePost(models.Model):
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    texto = models.TextField()

    imagem = models.ImageField(
        upload_to='timeline/imagens/',
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to='timeline/videos/',
        blank=True,
        null=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"Post de {self.associado} em {self.criado_em}"
