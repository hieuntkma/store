from django.db import models
from uuid import uuid4 as UUID4
from django.utils.timezone import now as djnow

from product.models import *


# Create your models here.

class Cart(models.Model):
    name = models.CharField(max_length=128, editable=True, unique=False)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
    account_uuid = models.UUIDField(default=UUID4,
                                    max_length=64,
                                    unique=True,
                                    editable=True)
    active = models.BooleanField(default=True,
                                 null=False,
                                 blank=False,
                                 editable=True)
    created_at = models.DateTimeField(default=djnow)
    updated_at = models.DateTimeField(default=djnow)

    def __str__(self):
        return self.name + "-" + str(self.uuid)

    def save(self, *args, **kwargs):
        self.updated_at = djnow()
        super().save(*args, **kwargs)

    @property
    def get_total_all_item_price(self):
        try:
            sum_all_item_price = 0
            cart_items = CartItem.objects.filter(active=True, cart_uuid=self.uuid)
            for cart_item in cart_items:
                sum_all_item_price += cart_item.get_total_item_price
            return sum_all_item_price
        except Exception as xx:
            print(xx)


class CartItem(models.Model):
    name = models.CharField(max_length=128, editable=True, unique=False)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
    cart_uuid = models.UUIDField(default=UUID4,
                                 max_length=64,
                                 unique=False,
                                 editable=True)
    product_uuid = models.UUIDField(default=UUID4,
                                    max_length=64,
                                    unique=False,
                                    editable=True)
    quantity = models.IntegerField(default=1,
                                   editable=True,
                                   blank=False,
                                   null=False)
    unit_price = models.IntegerField(default=0,
                                     editable=True,
                                     null=False,
                                     blank=False)
    active = models.BooleanField(default=True,
                                 null=False,
                                 blank=False,
                                 editable=True)
    created_at = models.DateTimeField(default=djnow)
    updated_at = models.DateTimeField(default=djnow)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.updated_at = djnow()
        super().save(*args, **kwargs)

    @property
    def get_total_item_price(self):
        return self.unit_price * self.quantity

    @property
    def get_thumbnail(self):
        try:
            thumbnail = ProductThumbnail.objects.filter(product_uuid=self.product_uuid, active=True).first()
            return thumbnail.thumbnail.url
        except Exception as xx:
            print(xx)
            return None
