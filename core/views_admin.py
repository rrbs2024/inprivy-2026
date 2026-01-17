from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from datetime import date
from datetime import datetime
from django.db import  IntegrityError
from django.contrib import messages
from django.http import JsonResponse

from django.template.loader import get_template
from django.http import HttpResponse
from django.template.loader import render_to_string

from io import BytesIO
from django.db.models import Q, F, Value, CharField
from django.utils.dateparse import parse_date
from itertools import chain
from operator import attrgetter
from decimal import Decimal
from django.core.exceptions import PermissionDenied
from django.db.models.functions import Length

from .models import Perfil, UsuarioPerfil, User, Associado
from .forms import  PerfilForm, AssociadoAdminForm

# Create your views here.

# ================================
# VIEW - PÁGINA INICIAL
# ================================

def iniciar(request):
    return render(request, 'inprivy/iniciar.html')

@login_required(login_url='/login/')
def home(request):
    perfil = request.user.usuarioperfil.perfil  # pega o perfil do usuário logado
    return render(request, 'inprivy/home_admin.html', {'perfil': perfil})

def sair_view(request):
    logout(request)
    return redirect('iniciar')
#======================================================================================================================

#=====================================================
# CLASSE VIEW - PERFIL
#=====================================================

@login_required()
def listar_perfil(request):
    # Só lista o perfil do usuário logado
    perfis = Perfil.objects.filter(usuario=request.user)
    return render(request, 'saco/perfil_listar.html', {'perfis': perfis})

@login_required()
def adicionar_perfil(request):
    # Usuário só pode ter um perfil, então opcional: bloqueia adicionar se já tiver perfil
    if not request.user.is_superuser:
        if Perfil.objects.filter(usuario=request.user).exists():
            raise PermissionDenied("Você já tem perfil.")

    if request.method == 'POST':
        form = PerfilForm(request.POST)
        if form.is_valid():
            perfil_obj = form.save(commit=False)
            perfil_obj.usuario = request.user  # associa o perfil ao usuário
            perfil_obj.save()
            return redirect('listar_perfil')
    else:
        form = PerfilForm()
    return render(request, 'saco/perfil_form.html', {'form': form})

@login_required()
def editar_perfil(request, id):
    tipo = get_object_or_404(Perfil, pk=id)

    if tipo.usuario != request.user:
        raise PermissionDenied()

    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            return redirect('listar_perfil')
    else:
        form = PerfilForm(instance=tipo)
    return render(request, 'saco/perfil_form.html', {'form': form})

@login_required()
def excluir_perfil(request, id):
    tipo = get_object_or_404(Perfil, pk=id)

    if tipo.usuario != request.user:
        raise PermissionDenied()

    if request.method == 'POST':
        tipo.delete()
        return redirect('listar_perfil')
    return render(request, 'saco/perfil_excluir.html', {'tipo': tipo})

@login_required()
def imprimir_perfil(request):
    # Só imprime o perfil do usuário logado
    perfil_imp = Perfil.objects.filter(usuario=request.user).order_by('perfil_razaosocial')
    return render(request, 'saco/perfil_imprimir.html', {'perfil_imp': perfil_imp})
#======================================================================================================================

#======================================================================================================================
# VIEW - ADM INPRIVY - ASSOCIADO
#======================================================================================================================

@login_required()
def listar_associado(request):    
    associados = Associado.objects.order_by ('id')  # filtra por perfil
    return render(request, 'inprivy/associado_listar.html', {'associados': associados})

@login_required()
def adicionar_associado(request):
    if request.method == 'POST':
        form = AssociadoAdminForm(request.POST)
        if form.is_valid():
            associado = form.save(commit=False)
            associado.usuarioadm = request.user  # usuário logado
            associado.save()
            return redirect('listar_associado')
        else:
            messages.error(request, 'Formulário inválido. Verifique os campos.')
    else:
        form = AssociadoAdminForm()

    return render(request, 'inprivy/associado_form.html', {'form': form})

@login_required()
def editar_associado(request, id):
    associado = get_object_or_404(Associado, pk=id)

    if request.method == 'POST':
        form = AssociadoAdminForm(request.POST, instance=associado)
        if form.is_valid():
            form.save()
            return redirect('listar_associado')
    else:
        form = AssociadoAdminForm(instance=associado)

    return render(request, 'inprivy/associado_form.html', {'form': form})

@login_required()
def excluir_associado(request, id):
    associado = get_object_or_404(Associado, pk=id)     
    if request.method == 'POST':
        associado.delete()
        return redirect('listar_associado')
    return render(request, 'inprivy/associado_excluir.html', {'associado': associado})

@login_required()
def imprimir_associado(request):   
    associado_imp = Associado.objects.all().order_by ('id')  # filtra por perfil    
    return render(request, 'inprivy/associado_imprimir.html', {'associado_imp': associado_imp} )

#======================================================================================================================

# =====================================================================================================================
# VIEW - HOME ADMIN
# =====================================================================================================================

@login_required
def home_admin(request):
    if not request.user.userclone.is_admin:
        raise PermissionDenied("Você não é admin, sua safada.")
    return render(request, 'inprivy/home_admin.html')
