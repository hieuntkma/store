from django.db import models
from uuid import uuid4 as UUID4
from django.utils.timezone import now as djnow
from django.db.models import Sum

from product.models import *


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

    # def get_best_seller_products(self, limit=None):
    #     """
    #     Trả về danh sách gồm các product_uuid và tổng số lượng đã bán
    #     (chỉ tính các đơn hàng đã giao thành công), sắp xếp từ cao đến thấp.
    #     """
    #     from django.db.models import Sum
    #     best_sellers = (
    #         OrderItem.objects.filter(
    #             active=True,
    #             order_uuid__in=Order.objects.filter(status='delivered', active=True).values('uuid')
    #         )
    #         .values('product_uuid')
    #         .annotate(total_quantity=Sum('quantity'))
    #         .order_by('-total_quantity')
    #     )
    #
    #     if limit:
    #         best_sellers = best_sellers[:limit]
    #
    #     return list(best_sellers)


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
