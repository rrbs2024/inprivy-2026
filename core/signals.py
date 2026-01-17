from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserClone


@receiver(post_save, sender=User)
def criar_userclone(sender, instance, created, **kwargs):
    if created:
        UserClone.objects.create(
            user=instance,
            apelido=instance.username,
            is_admin=False
        )
