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

from core.decorators import trial_5_minutos
from .models import UserClone, TimelinePost, Associado, ForumCategoria, ForumTopico, ForumResposta, TimelineComentario, Seguindo, Evento, PresencaEvento

from .forms import AssociadoForm, TimelinePostForm, MeuPerfilForm


# =============================================================================================================
# VIEW - TEMPO DE DEGUSTAÇÃO PARA USER SEM PLANO ATIVO
# =============================================================================================================
@login_required
@trial_5_minutos
def home_public(request):
    return render(request, 'inprivy/base_public.html')


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
                associado.save()
                return redirect('login')
    else:
        form = AssociadoForm()

    return render(request, 'inprivy/register.html', {'form': form})

# ================================
# VIEW - PÓS LOGIN
# ================================
@login_required
def pos_login(request):
    userclone = request.user.userclone

    if userclone.is_admin:
        return redirect('home_admin')
    else:
        return redirect('home_public')


# =============================================================================================================
# VIEW - LOGIN CUSTOMIZADO COM STATUS
# =============================================================================================================
class LoginCustomView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not user:
            messages.error(self.request, 'Usuário ou senha inválidos.')
            return self.render_to_response(self.get_context_data(form=form))

        userclone = user.userclone  # aqui já podemos acessar seguro

        # 🚫 usuário sem status, exceto admin
        if userclone.id != 1 and (not userclone.status or userclone.status is None):
            logout(self.request)
            messages.error(self.request, 'Usuário sem status definido.')
            return self.render_to_response(self.get_context_data(form=form))

        # ✅ ATIVO → entra normal
        if userclone.status.id == 3:
            return super().form_valid(form)

        # 🟡 INADIMPLENTE → entra em degustação
        if userclone.status.id == 6:
            self.request.session['mensagem_degustacao'] = (
                '⚠️ Você está inadimplente, mas pode usar o sistema por 5 minutos para degustação.'
            )
            return super().form_valid(form)

        # 🔒 BLOQUEIOS
        logout(self.request)

        status_msgs = {
            1: 'Seu cadastro está pendente da administração INPRIVY.',
            2: 'Seu plano necessita de 3 (três) indicações para ser ativado.',
            4: 'Escolha um plano e faça o pagamento.',
            5: 'Seu acesso foi suspenso.',
            7: 'Sua conta foi excluída.'
        }

        messages.error(self.request, status_msgs.get(userclone.status.id, 'Seu acesso não está liberado.'))

        return self.render_to_response(self.get_context_data(form=form))
    
    # chamada quando o form é inválido (login ou senha errados)
    def form_invalid(self, form):
        messages.error(self.request, 'Login ou senha incorretos.')
        return super().form_invalid(form)

# =====================================================================================================================
# VIEW PUBLIC - LOGOUT
# =====================================================================================================================

def sair_view(request):
    logout(request)
    return redirect('iniciar')

# =====================================================================================================================
# VIEW PUBLIC - TIMELINE
# =====================================================================================================================

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

# =====================================================================================================================
# VIEW PUBLIC - POSTAR TIMELINE
# =====================================================================================================================

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

# =====================================================================================================================
# VIEW PUBLIC - FORUM
# =====================================================================================================================

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
    associado = get_object_or_404(Associado, user=request.user)

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
    return render(request, 'inprivy/forum_categoria.html', {'categoria': categoria, 'topicos': categoria.topicos.filter(ativo=True)})


@login_required
def forum_topico(request, topico_id):
    topico = get_object_or_404(ForumTopico, id=topico_id, ativo=True)
    respostas = topico.respostas.filter(ativo=3).order_by('criada_em')
    return render(request, 'inprivy/forum_topico.html', {
        'topico': topico,
        'respostas': respostas
    })


@login_required
def forum_responder(request, topico_id):
    topico = get_object_or_404(ForumTopico, id=topico_id)
    associado = get_object_or_404(Associado, user=request.user)

    if request.method == 'POST':
        conteudo = request.POST.get('conteudo')

        ForumResposta.objects.create(
            topico=topico,
            autor=associado,
            conteudo=conteudo
        )
    return redirect('forum_topico', topico_id=topico.id)

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
