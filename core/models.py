from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


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
    tipoplano_observacoes = models.TextField("Observações", blank=True)
    tipoplano_valor = models.DecimalField(max_digits=8, decimal_places=2)
    tipoplano_duracao = models.PositiveIntegerField(default=30)  # validade do plano
    
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

    def __str__(self):
        return self.apelido
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
    tri_indica = models.IntegerField(null=True, blank=True)
    status = models.ForeignKey(StatusAssociacao, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Status Associação")
    usuarioadm = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def ativo(self):
        return self.status.id if self.status else None  # devolve o ID do status, tipo 3

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
# CLASSE MODEL - TIMELINE 
#=============================================================================================================

class TimelinePost(models.Model):
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='timeline_posts'
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

    class Meta:
        ordering = ['-criado_em']   
   
    def status_associado(self):
        # Pegar o valor de ATIVO do associado
        ativo = self.associado.ativo
        return ativo

    def __str__(self):
        return f"Post de {self.associado} em {self.criado_em}"

#=============================================================================================================
# CLASSE MODEL - ADMIN - FORUM CATEGORIA
#=============================================================================================================
class ForumCategoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Categoria de Forum"           # Nome no singular no admin
        verbose_name_plural = "Categorias de Foruns"  # Nome no plural no admin
        
#=============================================================================================================
# CLASSE MODEL - FORUM TOPICO
#=============================================================================================================

class ForumTopico(models.Model):
    categoria = models.ForeignKey(ForumCategoria, on_delete=models.CASCADE, related_name='topicos')
    autor = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='topicos')
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

#=============================================================================================================
# CLASSE MODEL - FORUM RESPOSTA
#=============================================================================================================

class ForumResposta(models.Model):
    topico = models.ForeignKey(
        ForumTopico,
        on_delete=models.CASCADE,
        related_name='respostas'
    )
    autor = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='respostas'
    )
    conteudo = models.TextField()
    criada_em = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)
    
#=============================================================================================================
# CLASSE MODEL - COMENTÁRIOS TIMELINE
#=============================================================================================================
class TimelineComentario(models.Model):
    post = models.ForeignKey(
        TimelinePost,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    autor = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE
    )
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f'Comentário de {self.autor} no post {self.post.id}'

#=============================================================================================================
# CLASSE MODEL - QUEM SEGUE QUEM
#=============================================================================================================
class Seguindo(models.Model):
    seguidor = models.ForeignKey(
        Associado,
        related_name='segue',
        on_delete=models.CASCADE
    )
    seguido = models.ForeignKey(
        Associado,
        related_name='seguidores',
        on_delete=models.CASCADE
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seguidor', 'seguido')

    def __str__(self):
        return f"{self.seguidor.associado_nome} segue {self.seguido.associado_nome}"
    
#=============================================================================================================
# CLASSE MODEL - EVENTO
#=============================================================================================================

class Evento(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    local = models.CharField(max_length=100, blank=True, null=True)

    midia = models.FileField(
        upload_to='eventos/',
        blank=True,
        null=True
    )

    criado_por = models.ForeignKey(
        'Associado',
        on_delete=models.PROTECT,
        related_name='eventos_criados'
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    # Apenas associado COMERCIAL pode criar evento
    def pode_criar(self):
        return self.criado_por.tipoplano_id == 4
    
#=============================================================================================================
# CLASSE MODEL - PRESENÇA-EVENTO
#=============================================================================================================
class PresencaEvento(models.Model):
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='presencas_eventos'
    )

    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='presencas'
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('associado', 'evento')

    def __str__(self):
        return f'{self.associado} - {self.evento}'

#=============================================================================================================
# CLASSE MODEL - GRUPO
#=============================================================================================================

class Grupo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    criador = models.ForeignKey(
        'Associado',
        on_delete=models.CASCADE,
        related_name='grupos_criados'
    )
    membros = models.ManyToManyField(
        'Associado',
        related_name='grupos',
        blank=True
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

#===========================================================================================================================#

#=============================================================================================================
# CLASSE MODEL - CONVERSA
#=============================================================================================================
class Conversa(models.Model):
    participante1 = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='conversas1')
    participante2 = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='conversas2')
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participante1', 'participante2')  # garante uma conversa única entre dois associados

    def __str__(self):
        return f"Conversa entre {self.participante1} e {self.participante2}"
    
#=============================================================================================================
# CLASSE MODEL - MENSAGEM ASSOCIADO 
#=============================================================================================================
class MensagemAssociado(models.Model):
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name='mensagens')
    remetente = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f"De {self.remetente} para {self.conversa}"

#=============================================================================================================
# CLASSE MODEL - ASSINATURA(PLANOS)
#=============================================================================================================
class Assinatura(models.Model):
    associado = models.ForeignKey(Associado, on_delete=models.CASCADE)
    tipoplano = models.ForeignKey(TipoPlano, on_delete=models.PROTECT)

    ativa = models.BooleanField(default=False)
    pago = models.BooleanField(default=False)
    assinada = models.BooleanField(default=False)
    plano_confirmado = models.BooleanField(default=False)

    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.associado} - {self.tipoplano.tipoplano_descricao}"