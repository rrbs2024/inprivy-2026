from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserClone, Associado


@receiver(post_save, sender=User)
def criar_userclone(sender, instance, created, **kwargs):
    if created:
        try:
            # Pegar o associado relacionado a esse user
            associado = Associado.objects.get(usuarioadm=instance)

            UserClone.objects.create(
                user=instance,
                apelido=instance.username,
                tipoplano=associado.tipoplano,
                status=associado.status
            )
        except Associado.DoesNotExist:
            # Se não houver associado, cria só com apelido
            UserClone.objects.create(
                user=instance,
                apelido=instance.username
            )
