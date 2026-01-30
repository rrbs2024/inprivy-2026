from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
import mercadopago
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from core.decorators import trial_5_minutos
from .models import UserClone, TimelinePost, Associado, ForumCategoria, ForumTopico, ForumResposta, TimelineComentario, Seguindo, Evento, PresencaEvento, Grupo, MensagemAssociado, Conversa, TipoPlano, Assinatura

from .forms import AssociadoForm, TimelinePostForm, MeuPerfilForm

# ================================
# VIEW - PÁGINA INICIAL
# ================================
def iniciar(request):
    return render(request, 'inprivy/iniciar.html')

# ================================
# VIEW - TERMOS
# ================================
def termos(request):
    if request.method == 'POST':
        return redirect('register')
    return render(request, 'inprivy/termos.html')

# ================================
# VIEW - REGISTER
# ================================
def register(request):
    if request.method == 'POST':
        form = AssociadoForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['associado_nome']

            # Verifica duplicidade de nome (login futuro)
            if Associado.objects.filter(associado_nome=nome).exists():
                form.add_error('associado_nome', 'Esse nome já está sendo usado como login.')
            else:
                # Salva o associado normalmente
                associado = form.save(commit=False)
                associado.associado_uf = 'PE'
                associado.status_id = 1 # PENDENTE INPRIVY
                associado.save()
                return redirect('login')
    else:
        form = AssociadoForm()

    return render(request, 'inprivy/register.html', {'form': form})

# =============================================================================================================
# VIEW - TEMPO DE DEGUSTAÇÃO PARA USER SEM PLANO ATIVO
# =============================================================================================================
@login_required
@trial_5_minutos  # decorator apenas para status 6 (inadimplente)
def home_public(request):
    return render(request, 'inprivy/base_public.html')

# ================================
# VIEW - PÓS LOGIN
# ================================
@login_required
def pos_login(request):
    user = request.user

    # admin verdadeiro
    if user.id == 1:
        return redirect('home_admin')

    # todo o resto é usuário comum
    return redirect('home_public')

# =============================================================================================================
# VIEW - LOGIN CUSTOMIZADO COM STATUS
# =============================================================================================================
class LoginCustomView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = False

    def form_valid(self, form):
        user = form.get_user()

        # se for admin, ignora userclone e loga normalmente
        if user.id == 1:
            return super().form_valid(form)

        associado = Associado.objects.get(usuarioadm=user)  # pega o associado do user
        status_id = associado.status_id

        # 🚫 bloqueados (NUNCA LOGA)
        bloqueados = {
            1: 'Seu cadastro está pendente de verificação do Admin.',
            2: 'Seu plano precisa de 3 indicações.',
            5: 'Seu acesso foi suspenso.',
            7: 'Sua conta foi excluída.',
        }

        if status_id in bloqueados:
            messages.error(self.request, bloqueados[status_id])
            return self.form_invalid(form)

        # ✅ agora SIM pode logar
        super().form_valid(form)

        # redirecionamentos válidos
        if status_id == 4:
            return redirect('planos')

        if status_id in (3, 6):
            if status_id == 6:
                self.request.session['mensagem_degustacao'] = (
                    '⚠️ Você pode usar o sistema por 5 minutos.'
                )
            return redirect('home_public')

        # fallback
        logout(self.request)
        return redirect('login')
    
# ===============================================================================================================
# VIEW PUBLIC - LOGOUT
# ===============================================================================================================

def sair_view(request):
    logout(request)
    return redirect('iniciar')

# ===============================================================================================================
# VIEW PUBLIC - TIMELINE
# ===============================================================================================================

@login_required
def timeline(request):
    associado = request.user.associado
    seguindo_ids = list(associado.segue.values_list('seguido__id', flat=True))
    seguindo_ids.append(associado.id)    
    posts = TimelinePost.objects.filter(
        associado__status=3,               # só associados ativos
        associado__id__in=seguindo_ids    # só quem você segue
    ).order_by('-criado_em')

    return render(request, 'inprivy/timeline.html', {'posts': posts})

# ===============================================================================================================
# VIEW PUBLIC - POSTAR TIMELINE
# ===============================================================================================================

@login_required
def postar_timeline(request):
    associado = get_object_or_404(Associado, usuarioadm=request.user)

    if request.method == 'POST':
        form = TimelinePostForm(request.POST, request.FILES)
        if form.is_valid():
            # salva na timeline (post oficial)
            post_timeline = form.save(commit=False)
            post_timeline.associado = associado
            post_timeline.save()

            return redirect('timeline')
    else:
        form = TimelinePostForm()

    return render(request, 'inprivy/postar_timeline.html', {'form': form})

# =====================================================================================================================
# VIEW PUBLIC - MEU PERFIL
# =====================================================================================================================

@login_required
def meu_perfil(request):
    associado = get_object_or_404(Associado, usuarioadm=request.user)

    if request.method == 'POST':
        form = MeuPerfilForm(request.POST, request.FILES, instance=associado)
        if form.is_valid():
            form.save()  # salva os dados do Associado

            # Atualiza o email no UserClone também
            if hasattr(associado, 'userclone'):
                associado.userclone.email = associado.associado_email
                associado.userclone.save()

            return redirect('meu_perfil')
    else:
        form = MeuPerfilForm(instance=associado)

    return render(request, 'inprivy/meu_perfil.html', {'form': form, 'associado': associado})

# ===============================================================================================================
# VIEW PUBLIC - FORUM
# =============================================================================================================

@login_required
def forum_home(request):
    categorias = ForumCategoria.objects.all()
    return render(request, 'inprivy/forum_home.html', {'categorias': categorias})


@login_required
def forum_categoria(request, categoria_id):
    categoria = get_object_or_404(ForumCategoria, id=categoria_id)

    # Pega todos os tópicos da categoria
    todos_topicos = categoria.topicos.all()

    # Filtra apenas tópicos cujo autor esteja ativo
    topicos_ativos = [t for t in todos_topicos if t.autor.ativo == 3]

    # Ordena do mais recente para o mais antigo
    topicos_ativos.sort(key=lambda t: t.criado_em, reverse=True)

    return render(request, 'inprivy/forum_categoria.html', {
        'categoria': categoria,
        'topicos': topicos_ativos
    })


@login_required
def forum_novo_topico(request, categoria_id):
    categoria = get_object_or_404(ForumCategoria, id=categoria_id)
    associado = get_object_or_404(Associado, usuarioadm=request.user)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        conteudo = request.POST.get('conteudo')

        ForumTopico.objects.create(
            categoria=categoria,
            autor=associado,
            titulo=titulo,
            conteudo=conteudo
        )
        return redirect('forum_categoria', categoria_id=categoria.id)

    # Ao criar novo tópico, renderiza o formulário da categoria
    return render(request, 'inprivy/forum_novo_topico.html', {
    'categoria': categoria
})


@login_required
def forum_topico(request, topico_id):
    topico = get_object_or_404(ForumTopico, id=topico_id, ativo=True)
    respostas = topico.respostas.filter(ativa=True).order_by('criada_em')
    return render(request, 'inprivy/forum_topico.html', {
        'topico': topico,
        'respostas': respostas
    })


@login_required
def forum_responder(request, topico_id):
    topico = get_object_or_404(ForumTopico, id=topico_id)
    associado = get_object_or_404(Associado, usuarioadm=request.user)

    if request.method == 'POST':
        conteudo = request.POST.get('conteudo')

        ForumResposta.objects.create(
            topico=topico,
            autor=associado,
            conteudo=conteudo
        )
    return redirect('forum_topico', topico_id=topico.id)


@login_required
def forum_editar_topico(request, topico_id):
    topico = get_object_or_404(ForumTopico, id=topico_id, autor__usuarioadm=request.user)

    if request.method == 'POST':
        topico.titulo = request.POST.get('titulo')
        topico.conteudo = request.POST.get('conteudo')
        topico.save()
        return redirect('forum_topico', topico_id=topico.id)

    return render(request, 'inprivy/forum_editar_topico.html', {
        'topico': topico
    })


# =====================================================================================================================
# VIEW PUBLIC - FOTOLOG
# =====================================================================================================================

@login_required
def fotolog(request):
    # pega o associado logado
    associado = get_object_or_404(Associado, usuarioadm=request.user)
    
    # só continua se o status for 3
    if associado.ativo != 3:
        postagens = []  # não mostra nada se não for ativo
    else:
        # pega só posts do associado com imagem ou vídeo
        postagens = TimelinePost.objects.filter(
            associado=associado
        ).exclude(imagem__isnull=True, video__isnull=True).order_by('-criado_em')

    return render(request, 'inprivy/fotolog.html', {
        'postagens': postagens
    })


# =====================================================================================================================
# VIEW PUBLIC - COMENTAR TIMELINE
# =====================================================================================================================

@login_required
def comentar_timeline(request, post_id):
    post = get_object_or_404(TimelinePost, id=post_id)
    associado = get_object_or_404(Associado, usuarioadm=request.user)

# Checa se o associado tá ativo via @property
    if associado.ativo != 3:
        return redirect('timeline')  # ou mostrar mensagem de bloqueio
    if request.method == 'POST':
        texto = request.POST.get('texto')
        if texto:
            TimelineComentario.objects.create(
                post=post,
                autor=associado,
                texto=texto
            )

    return redirect('timeline')

# =====================================================================================================================
# VIEW PUBLIC - CONTEÚDO
# ===================================================================================================================

@login_required
def conteudo(request):
    # Pega todos os posts cujos associados têm status = 3
    posts = TimelinePost.objects.filter(
        associado__status=3
    ).order_by('-criado_em')

    return render(request, 'inprivy/conteudo.html', {
        'posts': posts
    })

# =====================================================================================================================
# VIEW PUBLIC - QUEM SEGUE QUEM
# =====================================================================================================================

@login_required
def seguir_associado(request, associado_id):
    seguidor = request.user.associado
    seguido = get_object_or_404(Associado, id=associado_id)

    # não permite que siga a si mesmo
    if seguidor != seguido:
        Seguindo.objects.get_or_create(seguidor=seguidor, seguido=seguido)

    return redirect('listar_associado')

@login_required
def deixar_de_seguir(request, associado_id):
    seguidor = request.user.associado
    seguido = get_object_or_404(Associado, id=associado_id)

    Seguindo.objects.filter(seguidor=seguidor, seguido=seguido).delete()
    return redirect('listar_associado')

# =====================================================================================================================
# VIEW PUBLIC - LISTAR ASSOCIADOS
# =====================================================================================================================

@login_required
def listar_associado(request):
    associados = Associado.objects.filter(status=3).exclude(usuarioadm=request.user)
    seguindo_ids = request.user.associado.segue.values_list('seguido__id', flat=True)
    return render(request, 'inprivy/listar_associado.html', {
        'associados': associados,
        'seguindo_ids': list(seguindo_ids)
    })

# =====================================================================================================================
# VIEW PUBLIC - LISTAR SEGUIDORES E SEGUINDO
# =====================================================================================================================

@login_required
def meus_seguidores_seguindo(request, associado_id):
    associado = get_object_or_404(Associado, id=associado_id, status=3)

    # Quem ele segue
    seguindo = Seguindo.objects.filter(seguidor=associado).select_related('seguido')

    # Quem o segue
    seguidores = Seguindo.objects.filter(seguido=associado).select_related('seguidor')

    # IDs que o usuário logado segue, pra botão funcionar
    seguindo_ids = request.user.associado.segue.values_list('seguido__id', flat=True)

    return render(request, 'inprivy/lista_seguidores_seguindo.html', {
        'associado': associado,
        'seguindo': seguindo,
        'seguidores': seguidores,
        'seguindo_ids': seguindo_ids
    })

# =======================================================================================
# VIEW PUBLIC - CRIAR EVENTO
# =======================================================================================

@login_required
def criar_evento(request):
    associado = request.user.associado

    if associado.tipoplano_id != 4:
        messages.error(request, "Só Associados do plano comercial!!")
        return redirect('base_public')

    if request.method == 'POST':
        Evento.objects.create(
            titulo=request.POST.get('titulo'),
            descricao=request.POST.get('descricao'),
            inicio=request.POST.get('inicio'),
            fim=request.POST.get('fim'),
            local=request.POST.get('local'),
            midia=request.FILES.get('midia'),  # 👈 AQUI
            criado_por=associado
        )

    return render(request, 'inprivy/criar_evento.html')

# =======================================================================================
# VIEW PUBLIC - LISTA EVENTOS
# =======================================================================================

@login_required
def lista_eventos(request):
    associado = request.user.associado

    eventos = Evento.objects.all().order_by('inicio')

    presencas = PresencaEvento.objects.filter(
        associado=associado
    ).values_list('evento_id', flat=True)

    return render(request, 'inprivy/lista_eventos.html', {
        'eventos': eventos,
        'presencas': presencas
    })

# =======================================================================================
# VIEW PUBLIC - TOGGLE PRESENÇA
# =======================================================================================

@login_required
def toggle_presenca(request, evento_id):
    associado = request.user.associado
    evento = get_object_or_404(Evento, id=evento_id)

    presenca = PresencaEvento.objects.filter(
        associado=associado,
        evento=evento
    )

    if presenca.exists():
        presenca.delete()   # DESMARCA
    else:
        PresencaEvento.objects.create(
            associado=associado,
            evento=evento
        )   # MARCA

    return redirect('lista_eventos')


# =======================================================================================
# VIEW PUBLIC - AGENDA
# =======================================================================================

@login_required
def agenda(request):
    associado = request.user.associado

    # Puxa apenas os eventos que o usuário marcou "EU VOU"
    presencas = PresencaEvento.objects.filter(
        associado=associado
    ).select_related('evento').order_by('evento__inicio')

    eventos = [p.evento for p in presencas]

    return render(request, 'inprivy/agenda.html', {
        'eventos': eventos
    })

# =======================================================================================
# VIEW PUBLIC - CRIAR GRUPOS
# =======================================================================================

@login_required
def criar_grupo(request):
    associado = request.user.associado  # pegando o associado logado
    if associado.ativo != 3:  # só ativos podem criar grupo
        messages.error(request, "Somente associados ativos podem criar grupos.")
        return redirect('base_public')

    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')

        if nome.strip() == '':
            messages.error(request, "O nome do grupo é obrigatório.")
            return redirect('criar_grupo')

        grupo = Grupo.objects.create(
            nome=nome,
            descricao=descricao,
            criador=associado
        )
        grupo.membros.add(associado)  # o criador já entra automaticamente no grupo
        messages.success(request, f"Grupo '{nome}' criado com sucesso!")
        return redirect('detalhe_grupo', id=grupo.id)

    return render(request, 'inprivy/criar_grupo.html')

# =======================================================================================
# VIEW PUBLIC - DETALHE GRUPO
# =======================================================================================

@login_required
def detalhe_grupo(request, id):
    grupo = get_object_or_404(Grupo, id=id)
    associado = request.user.associado

    # Verifica se o associado já está no grupo
    esta_no_grupo = grupo.membros.filter(id=associado.id).exists()

    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'entrar':
            grupo.membros.add(associado)
            messages.success(request, "Você entrou no grupo!")
            return redirect('detalhe_grupo', id=grupo.id)
        elif acao == 'sair':
            grupo.membros.remove(associado)
            messages.success(request, "Você saiu do grupo!")
            return redirect('detalhe_grupo', id=grupo.id)

    context = {
        'grupo': grupo,
        'esta_no_grupo': esta_no_grupo
    }
    return render(request, 'inprivy/detalhe_grupo.html', context)

# =======================================================================================
# VIEW PUBLIC - LISTAR GRUPOS
# =======================================================================================

@login_required
def listar_grupos(request):
    grupos = Grupo.objects.all()  # pega todos os grupos do sistema

    context = {
        'grupos': grupos
    }
    return render(request, 'inprivy/listar_grupos.html', context)

# =======================================================================================
# VIEW PUBLIC - EDITAR GRUPO
# =======================================================================================

@login_required
def editar_grupo(request, id):
    grupo = get_object_or_404(Grupo, id=id)

    # Só o criador pode editar
    if grupo.criador != request.user.associado:
        messages.error(request, "Somente o criador do grupo pode editar.")
        return redirect('detalhe_grupo', id=grupo.id)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        grupo.nome = nome
        grupo.descricao = descricao
        grupo.save()
        messages.success(request, "Grupo atualizado com sucesso!")
        return redirect('detalhe_grupo', id=grupo.id)

    context = {'grupo': grupo}
    return render(request, 'inprivy/editar_grupo.html', context)

# =======================================================================================
# VIEW PUBLIC - EXCLUIR GRUPO
# =======================================================================================

@login_required
def excluir_grupo(request, id):
    grupo = get_object_or_404(Grupo, id=id)

    # Só o criador pode excluir
    if grupo.criador != request.user.associado:
        messages.error(request, "Somente o criador do grupo pode excluir.")
        return redirect('detalhe_grupo', id=grupo.id)

    if request.method == 'POST':
        grupo.delete()
        messages.success(request, "Grupo excluído com sucesso!")
        return redirect('listar_grupos')

    context = {'grupo': grupo}
    return render(request, 'inprivy/excluir_grupo.html', context)

# =======================================================================================
# VIEW PUBLIC - INBOX(MENSAGEM ASSOCIADO)
# =======================================================================================

@login_required
def inbox_mensagens(request):
    associado = request.user.associado

    # pega todas as conversas em que o associado participa
    conversas = Conversa.objects.filter(
        Q(participante1=associado) | Q(participante2=associado)
    ).order_by('-criada_em')

    lista_conversas = []
    for conversa in conversas:
        ultima_mensagem = conversa.mensagens.last()  # pega a última mensagem da conversa
        # identifica quem é o outro participante
        outro = conversa.participante1 if conversa.participante2 == associado else conversa.participante2
        # verifica se há mensagens não lidas enviadas pelo outro
        nao_lida = conversa.mensagens.filter(remetente=outro, lida=False).exists()

        lista_conversas.append({
            'conversa': conversa,
            'ultimo_remetente': ultima_mensagem.remetente if ultima_mensagem else None,
            'ultima_mensagem': ultima_mensagem.mensagem if ultima_mensagem else '',
            'outro': outro,
            'nao_lida': nao_lida
        })

    return render(request, 'inprivy/inbox_mensagens.html', {'lista_conversas': lista_conversas})

# =======================================================================================
# VIEW PUBLIC - ENVIAR MENSAGEM
# =======================================================================================

@login_required
def enviar_mensagem(request):
    associado = request.user.associado
    destinatario_id = request.GET.get('destinatario_id')

    # identifica o destinatário (outro participante)
    destinatario = None
    if destinatario_id:
        destinatario = get_object_or_404(Associado, id=destinatario_id)

    if request.method == 'POST':
        texto = request.POST.get('mensagem')

        # pega o destinatário do form se existir (apenas como backup)
        if not destinatario:
            destinatario = get_object_or_404(Associado, id=request.POST.get('destinatario'))

        # procura conversa existente entre os dois
        conversa = Conversa.objects.filter(
            (Q(participante1=associado) & Q(participante2=destinatario)) |
            (Q(participante1=destinatario) & Q(participante2=associado))
        ).first()

        # se não existir, cria uma nova conversa
        if not conversa:
            conversa = Conversa.objects.create(
                participante1=associado,
                participante2=destinatario
            )

        # cria a mensagem dentro da conversa
        MensagemAssociado.objects.create(
            conversa=conversa,
            remetente=associado,
            mensagem=texto
        )

        return redirect('inbox_mensagens')

    return render(
        request,
        'inprivy/enviar_mensagem.html',
        {
            'associados': Associado.objects.exclude(id=associado.id),
            'destinatario': destinatario
        }
    )

# =======================================================================================
# VIEW PUBLIC - DETALHE MENSAGEM
# =======================================================================================

@login_required
def detalhe_mensagem(request, id):
    associado = request.user.associado

    mensagem = get_object_or_404(MensagemAssociado, id=id)

    # segurança: só o destinatário pode ver
    if mensagem.destinatario != associado:
        return HttpResponseForbidden("Você não tem permissão para ver esta mensagem.")

    # marca como lida
    if not mensagem.lida:
        mensagem.lida = True
        mensagem.save()

    return render(
        request,
        'inprivy/detalhe_mensagem.html',
        {'mensagem': mensagem}
    )

# =======================================================================================
# VIEW PUBLIC - LISTAR PLANOS
# =======================================================================================

@login_required
def planos(request):
    associado = request.user.associado

    # Verifica se já existe assinatura pendente
    assinatura_existente = Assinatura.objects.filter(
        associado=associado       
    ).first()

    if assinatura_existente and assinatura_existente.assinada == False:
        # Já existe assinatura pendente → vai direto para assinar plano
        return redirect('assinar_plano', plano_id=assinatura_existente.tipoplano.id)
    
    if assinatura_existente and assinatura_existente.assinada == True:
        # Já existe assinatura concluída → vai direto para pagar assinatura
        return redirect('pagar_assinatura',assinatura_id=assinatura_existente.id)     

    # Caso não exista assinatura → lista todos os planos normalmente
    
    planos_disponiveis = TipoPlano.objects.all().order_by('tipoplano_valor')
    return render(request, 'inprivy/planos.html', {
    'planos': planos_disponiveis})      

# =======================================================================================
# VIEW PUBLIC - ASSINAR PLANO
# =======================================================================================

@login_required
def assinar_plano(request, plano_id):
    associado = request.user.associado
    plano = get_object_or_404(TipoPlano, id=plano_id)

    # Verifica se já existe assinatura pendente para este associado
    assinatura_existente = Assinatura.objects.filter(
        associado=associado,
        assinada = True
    ).first()  # pega a primeira, se existir

    if request.method == 'POST':
        if  assinatura_existente:
            assinatura_existente.assinada = True
            assinatura_existente.save()
            assinatura = assinatura_existente
        else:
            assinatura = Assinatura.objects.create(
            associado=associado,
            tipoplano=plano,
            data_fim=timezone.now().date() + timedelta(days=plano.tipoplano_duracao),
            ativa=False,
            pago=False,
            assinada=True
        )
        return redirect('pagar_assinatura', assinatura_id=assinatura.id)
    
    return render(request, 'inprivy/assinar_plano.html', {
        'plano': plano,
        'assinatura_existente': assinatura_existente
    })

# =======================================================================================
# VIEW PUBLIC - PAGAR ASSINATURA
# =======================================================================================

@login_required
def pagar_assinatura_origem(request, assinatura_id):
    assinatura = get_object_or_404(Assinatura, id=assinatura_id, associado=request.user.associado)

    if request.method == 'POST':
        # Simula pagamento
        assinatura.pago = True
        assinatura.ativa = True
        assinatura.save()

        # 👉 muda status do associado
        associado = assinatura.associado
        associado.status_id = 3
        associado.save()

        # Aqui ainda não muda status.id do usuário
        return render(request, 'inprivy/pagar_assinatura_sucesso.html', {
            'assinatura': assinatura
        })

    return render(request, 'inprivy/pagar_assinatura.html', {
        'assinatura': assinatura
    })

# =======================================================================================
# VIEW PUBLIC - MERCADO PAGO
# =======================================================================================

@login_required
def pagar_assinatura(request, assinatura_id):
    assinatura = get_object_or_404(Assinatura, id=assinatura_id, associado=request.user.associado)
    
    print("METHOD:", request.method)
   
    if request.method == 'POST':
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        # Cria preferência para Bricks
        preference_data = {
            "items": [
                {
                    "title": f"Assinatura {assinatura.tipoplano.tipoplano_descricao}",
                    "quantity": 1,
                    "unit_price": float(assinatura.tipoplano.tipoplano_valor),
                }
            ],
            "back_urls": {
                "success": f"https://elucidative-jesica-brotherly.ngrok-free.dev/assinaturas/{assinatura.id}/sucesso/",
                "failure": f"https://elucidative-jesica-brotherly.ngrok-free.dev/assinaturas/{assinatura.id}/falha/",
                "pending": f"https://elucidative-jesica-brotherly.ngrok-free.dev/assinaturas/{assinatura.id}/pendente/",
            },
            "auto_return": "approved",
            "payment_methods": {"excluded_payment_types": [], "installments": 1}
        }

        preference_response = sdk.preference().create(preference_data)

        # 🚨 DEBUG: imprime a resposta completa no console
        print("===== RESPOSTA MERCADO PAGO =====")
        print(preference_response)
        print("=================================")

        # Pega o ID da preferência para usar no Bricks
        preference_id = preference_response.get("response", {}).get("id")

        if not preference_id:
            return render(request, 'inprivy/pagar_assinatura_falha.html', {
                'assinatura': assinatura,
                'erro': 'Não foi possível gerar a preferência de pagamento. Veja o console para detalhes.'
            })

        # ⚡ Renderiza template com o Bricks e envia preference_id
        return render(request, 'inprivy/pagar_assinatura_bricks.html', {
            'assinatura': assinatura,
            'preference_id': preference_id,
            'public_key': settings.MERCADOPAGO_PUBLIC_KEY
        })

    return render(request, 'inprivy/pagar_assinatura.html', {
        'assinatura': assinatura
    })


#=======================================================================================================
@login_required
def assinatura_sucesso(request, assinatura_id):
    assinatura = get_object_or_404(Assinatura, id=assinatura_id, associado=request.user.associado)

    # Marca pagamento e assinatura como ativa
    assinatura.pago = True
    assinatura.ativa = True
    assinatura.save()

    # Atualiza status do associado
    associado = assinatura.associado
    associado.status_id = 3
    associado.save()

    return render(request, 'inprivy/pagar_assinatura_sucesso.html', {
        'assinatura': assinatura
    })

#=======================================================================================================
@login_required
def assinatura_falha(request, assinatura_id):
    assinatura = get_object_or_404(
        Assinatura,
        id=assinatura_id,
        associado=request.user.associado
    )

    retorno_mp = {
        'status': request.GET.get('status', ''),
        'status_detail': request.GET.get('status_detail', ''),
        'collection_status': request.GET.get('collection_status', ''),
        'payment_id': request.GET.get('payment_id', ''),
    }

    return render(request, 'inprivy/pagar_assinatura_falha.html', {
        'assinatura': assinatura,
        'retorno_mp': retorno_mp
    })



#=======================================================================================================
@login_required
def assinatura_pendente(request, assinatura_id):
    assinatura = get_object_or_404(Assinatura, id=assinatura_id, associado=request.user.associado)
    return render(request, 'inprivy/pagar_assinatura_pendente.html', {
        'assinatura': assinatura
    })

#=======================================================================================================



@csrf_exempt
def webhook_mercadopago(request):
    if request.method == 'POST':
        import mercadopago
        from django.conf import settings

        print("===== WEBHOOK MERCADO PAGO =====")

        data = request.POST or request.GET
        payment_id = data.get('data.id') or data.get('payment_id')

        print("payment_id recebido:", payment_id)

        if not payment_id:
            return HttpResponse(status=200)

        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        payment_info = sdk.payment().get(payment_id)

        print("status real:", payment_info["response"]["status"])
        print("detalhe:", payment_info["response"]["status_detail"])

        print("================================")
        return HttpResponse(status=200)

    return HttpResponse(status=400)

