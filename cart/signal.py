from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Cart
from account.models import Account
from uuid import uuid4

User = get_user_model()

@receiver(post_save, sender=Account)
def create_cart_for_new_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(
            name=f"Cart for {instance.username}",
            account_uuid=instance.uuid,  # Giả sử User có field `uuid`
            uuid=uuid4(),
            active=True
        )