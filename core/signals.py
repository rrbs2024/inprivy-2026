from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserClone, Associado


@receiver(post_save, sender=User)
def criar_userclone(sender, instance, created, **kwargs):
    if created:
        # ❌ Pula o admin
        if instance.id == 1:
            return

        try:
            # Pegar o associado relacionado a esse user
            associado = Associado.objects.get(usuarioadm=instance)

            UserClone.objects.create(
                user=instance,
                apelido=instance.username                         
               
            )
        except Associado.DoesNotExist:
            # Se não houver associado, cria só com apelido
            UserClone.objects.create(
                user=instance,
                apelido=instance.username
            )
