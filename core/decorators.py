from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout

from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.contrib import messages
from functools import wraps
from core.models import Associado  # ← ERA ISSO, SUA GALINHA

def trial_5_minutos(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect('login')

        # 🔥 Associado vem do USER
        try:
            associado = Associado.objects.get(usuarioadm=user)
        except Associado.DoesNotExist:
            return view_func(request, *args, **kwargs)

        # 🔒 Só status 6 (inadimplente)
        if associado.status.id != 6:
            return view_func(request, *args, **kwargs)

        agora = datetime.now()
        inicio_trial = request.session.get('trial_inicio')

        if not inicio_trial:
            request.session['trial_inicio'] = agora.isoformat()
            request.session['mensagem_degustacao'] = (
                'Você está inadimplente e pode usar o sistema por apenas 5 minutos.'
            )
            return view_func(request, *args, **kwargs)

        inicio_trial = datetime.fromisoformat(inicio_trial)

        if agora - inicio_trial > timedelta(minutes=5):
            logout(request)
            messages.error(
                request,
                'Seu tempo de degustação expirou. Regularize seu plano para continuar.'
            )
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper