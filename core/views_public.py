from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView

from core.decorators import trial_5_minutos
from .models import UserClone
from .forms import AssociadoForm


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


# ================================
# LOGOUT
# ================================
def sair_view(request):
    logout(request)
    return redirect('iniciar')
