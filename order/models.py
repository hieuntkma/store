from django.db import models
from uuid import uuid4 as UUID4
from django.utils.timezone import now as djnow
from django.db.models import Sum

from product.models import *
from account.models import *


# Create your models here.

class Order(models.Model):
    name = models.CharField(max_length=128,
                            editable=True,
                            unique=False)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
    account_uuid = models.UUIDField(default=UUID4,
                                    max_length=64,
                                    unique=False,
                                    editable=True,
                                    null=True,
                                    blank=True
                                    )
    total_price = models.IntegerField(default=0,
                                      editable=True,
                                      null=True,
                                      blank=True)
    status = models.CharField(max_length=50,
                              default="pending",
                              choices=(
                                  ("pending", "Chờ xử lý"),
                                  ("confirmed", "Đã xác nhận"),
                                  ("shipping", "Đang giao hàng"),
                                  ("delivered", "Đã nhận hàng"),
                                  ("cancelled", "Đã hủy"),
                              ),
                              editable=True,
                              unique=False
                              )
    shipping_price = models.IntegerField(default=0,
                                         editable=True,
                                         null=False,
                                         blank=False)
    desc = models.TextField(blank=True,
                            null=True,
                            editable=True)
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

    def get_order_items(self):
        order_items = OrderItem.objects.filter(order_id=self.uuid)
        return order_items

    def get_user_name(self):
        user = Account.objects.filter(uuid=self.account_uuid).first()
        return user.username

    def get_bill(self):
        bill = Bill.objects.filter(order_id=self.uuid).first()
        return bill

    def get_total(self):
        bill = Bill.objects.all().count()
        return bill
    def get_revenue(self):
        bills = Bill.objects.all()
        revenue = 0
        for bill in bills:
            revenue += bill.total_price
        return revenue


class OrderItem(models.Model):
    name = models.CharField(max_length=128,
                            editable=True,
                            unique=False)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
    order_uuid = models.UUIDField(default=UUID4,
                                  max_length=64,
                                  unique=False,
                                  editable=True)
    product_uuid = models.UUIDField(default=UUID4,
                                    max_length=64,
                                    unique=False,
                                    editable=True)
    unit_price = models.IntegerField(default=0,
                                     editable=True,
                                     null=False,
                                     blank=False)
    product_name = models.CharField(max_length=200,
                                    editable=True,
                                    null=False,
                                    blank=False)
    quantity = models.IntegerField(default=1,
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
    def get_thumbnail(self):
        try:
            thumbnail = ProductThumbnail.objects.filter(product_uuid=self.product_uuid, active=True).first()
            return thumbnail.thumbnail.url
        except Exception as xx:
            print(xx)
            return None


class Bill(models.Model):
    name = models.CharField(max_length=128,
                            editable=True,
                            unique=False)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
    order_uuid = models.UUIDField(default=UUID4,
                                  max_length=64,
                                  unique=False,
                                  editable=True)
    recipient_name = models.CharField(max_length=200,
                                      editable=True,
                                      null=False,
                                      blank=False)
    first_name = models.CharField(max_length=200,
                                  editable=True,
                                  null=False,
                                  blank=False)
    last_name = models.CharField(max_length=200,
                                 editable=True,
                                 null=False,
                                 blank=False)
    delivery_address = models.TextField(blank=False,
                                        null=False,
                                        editable=True)
    note = models.TextField(blank=True,
                            null=True,
                            editable=True)
    recipient_phone = models.CharField(max_length=200,
                                       editable=True,
                                       null=False,
                                       blank=False)
    recipient_email = models.CharField(max_length=200,
                                       editable=True,
                                       null=True,
                                       blank=True)
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

    def get_recipient_name(self):
        self.recipient_name = f"{self.first_name} {self.last_name} "
        self.save()
