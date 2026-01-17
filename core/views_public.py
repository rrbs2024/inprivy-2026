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

from .models import Associado, UserClone
from .forms import AssociadoForm

# Create your views here.

# ================================
# VIEW - PÁGINA INICIAL
# ================================

def iniciar(request):
    return render(request, 'inprivy/iniciar.html')

@login_required(login_url='/login/')
def home(request):    
    return render(request, 'inprivy/home.html')

def sair_view(request):
    logout(request)
    return redirect('iniciar')
#==============================================================================================================

# =============================================================================================================
# VIEW - TERMOS DE ASSOCIAÇÃO
# =============================================================================================================

def termos(request):
    if request.method == 'POST':
        return redirect('register')

    return render(request, 'inprivy/termos.html')
#==============================================================================================================

#=====================================================
# VIEW - REGISTER - ASSOCIADO
#=====================================================

def register(request):
    if request.method == 'POST':
        form = AssociadoForm(request.POST)
        if form.is_valid():
            associado = form.save(commit=False)
            associado.usuarioadm = request.user if request.user.is_authenticated else None
            associado.save()
            return redirect('login')  # ou home, ou onde tu quiser, sua safada
    else:
        form = AssociadoForm()

    return render(request, 'inprivy/register.html', {'form': form})
#======================================================================================================================

# ================================
# VIEW - PÁGINA INICIAL PÚBLICA
# ================================
def iniciar(request):
    return render(request, 'inprivy/iniciar.html')

# ================================
# VIEW - PÓS LOGIN
# ================================
@login_required
def pos_login(request):
    userclone = request.user.userclone  # pega info extra do usuário

    if userclone.is_admin:
        return redirect('home_admin')  # chama a view do admin
    else:
        return redirect('home_public')   # chama a view do usuário comum

# ================================
# VIEW - HOME DO USUÁRIO COMUM
# ================================
@login_required
def home_public(request):
    return render(request, 'inprivy/base_public.html')  # esse template vai estender base_public.html

# ================================
# LOGOUT
# ================================
def sair_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('iniciar')