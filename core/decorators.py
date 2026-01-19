from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout

from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.contrib import messages
from functools import wraps

def trial_5_minutos(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        userclone = request.user.userclone

        # Ativo = entra normal
        if userclone.status and userclone.status.id == 3:
            return view_func(request, *args, **kwargs)

        # Inadimplente = trial de 5 minutos
        if userclone.status and userclone.status.id == 5:
            agora = datetime.now()
            inicio_trial = request.session.get('trial_inicio')

            if not inicio_trial:
                # marca início do trial
                request.session['trial_inicio'] = agora.isoformat()

                # seta mensagem de degustação na session (NÃO usa messages)
                request.session['mensagem_degustacao'] = (
                    'Você está inadimplente e pode usar o sistema por apenas 5 minutos.'
                )

                return view_func(request, *args, **kwargs)

            inicio_trial = datetime.fromisoformat(inicio_trial)

            # verifica se passou 5 minutos
            if agora - inicio_trial > timedelta(minutes=5):
                logout(request)
                messages.error(
                    request,
                    'Seu tempo de degustação expirou. Regularize seu plano para continuar.'
                )
                return redirect('login')

            return view_func(request, *args, **kwargs)

        # Outros status = bloqueio
        logout(request)
        messages.error(
            request,
            'Seu acesso não está liberado.'
        )
        return redirect('login')

    return wrapper
