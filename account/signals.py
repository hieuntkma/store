from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile
from cart.models import Cart

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Tạo profile tương ứng cho user vừa tạo
        UserProfile.objects.create(
            account=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            name=f"{instance.first_name} {instance.last_name}".strip()
        )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(
            name=f"Giỏ hàng của {instance.username}",
            account_uuid=instance.uuid,
            active=True
        )
