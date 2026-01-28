from core.models import MensagemAssociado, Conversa
from django.db.models import Q

def mensagens_nao_lidas(request):
    # default
    total = 0

    if request.user.is_authenticated and not request.user.is_superuser:
        associado = getattr(request.user, 'associado', None)

        if associado:
            # pega todas as conversas do associado
            conversas = Conversa.objects.filter(
                Q(participante1=associado) | Q(participante2=associado)
            )

            # conta mensagens não lidas enviadas por outra pessoa
            total = MensagemAssociado.objects.filter(
                conversa__in=conversas,
                lida=False
            ).exclude(remetente=associado).count()

    return {
        'mensagens_nao_lidas': total
    }
