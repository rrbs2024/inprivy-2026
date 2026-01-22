from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect

from core.decorators import trial_5_minutos
from .models import UserClone, TimelinePost, Associado, ForumCategoria, ForumTopico, ForumResposta, TimelineComentario

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
        userclone = user.userclone

        # 🚫 usuário sem status
        if not userclone.status:
            logout(self.request)
            messages.error(self.request, 'Usuário sem status definido.')
            return self.render_to_response(self.get_context_data(form=form))

        # ✅ ATIVO → entra normal
        if userclone.status.id == 3:
            return super().form_valid(form)

        # 🟡 INADIMPLENTE → entra em degustação
        if userclone.status.id == 5:
            self.request.session['mensagem_degustacao'] = (
                '⚠️ Você está inadimplente, mas pode usar o sistema por 5 minutos para degustação.'
            )
            return super().form_valid(form)

        # 🔒 BLOQUEIOS
        logout(self.request)

        if userclone.status.id == 1:
            messages.error(self.request, 'Seu cadastro está pendente da administração INPRIVY.')
        elif userclone.status.id == 2:
            messages.error(self.request, 'Seu plano necessita de 3 (três) indicações para ser ativado.')
        elif userclone.status.id == 4:
            messages.error(self.request, 'Seu acesso foi suspenso.')
        elif userclone.status.id == 6:
            messages.error(self.request, 'Sua conta foi excluída.')
        else:
            messages.error(self.request, 'Seu acesso não está liberado.')

        return self.render_to_response(self.get_context_data(form=form))

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
    posts = TimelinePost.objects.filter(ativo=True)
    return render(request, 'inprivy/timeline.html', {'posts': posts})

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
    topicos = categoria.topicos.filter(ativo=True).order_by('-criado_em')
    return render(request, 'inprivy/forum_categoria.html', {
        'categoria': categoria,
        'topicos': topicos
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
    respostas = topico.respostas.filter(ativa=True).order_by('criada_em')
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
    associado = get_object_or_404(Associado, usuarioadm=request.user)
    postagens = TimelinePost.objects.filter(
        associado=associado,
        ativo=True
    ).order_by('-criado_em')

    return render(request, 'inprivy/fotolog.html', {
        'postagens': postagens
    })

# =====================================================================================================================
# VIEW PUBLIC - COMENTAR TIMELINE
# =====================================================================================================================

@login_required
def comentar_timeline(request, post_id):
    post = get_object_or_404(TimelinePost, id=post_id, ativo=True)
    associado = get_object_or_404(Associado, usuarioadm=request.user)

    if request.method == 'POST':
        texto = request.POST.get('texto')
        if texto:
            TimelineComentario.objects.create(
                post=post,
                autor=associado,
                texto=texto
            )

    return redirect('timeline')