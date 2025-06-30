from django.db import models
from uuid import uuid4 as UUID4

from django.db.models import Avg
from django.utils.timezone import now as djnow


# Create your models here.


class Categories(models.Model):
    name = models.CharField(max_length=128, editable=True, unique=True)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
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
        return self.name + " - " + str(self.uuid)

    def save(self, *args, **kwargs):
        self.updated_at = djnow()
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=128,
                            editable=True,
                            unique=False)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
    categories_uuid = models.UUIDField(default=UUID4,
                                       max_length=64,
                                       unique=False,
                                       editable=True)
    desc = models.TextField(blank=True,
                            null=True,
                            editable=True)
    price = models.IntegerField(default=0,
                                editable=True,
                                null=False,
                                blank=False)
    sale_price = models.IntegerField(default=0,
                                     editable=True,
                                     null=False,
                                     blank=False)
    stock_quantity = models.IntegerField(default=1,
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
        return self.name + str(self.uuid)

    def save(self, *args, **kwargs):
        self.updated_at = djnow()
        super().save(*args, **kwargs)

    def get_categories(self):
        try:
            categories = Categories.objects.filter(uuid=self.categories_uuid, active=True).first()
            return categories.name
        except Categories.DoesNotExist:
            return None

    @property
    def get_thumbnail(self):
        try:
            thumbnail = ProductThumbnail.objects.filter(product_uuid=self.uuid, active=True).first()
            return thumbnail.thumbnail.url
        except Exception as xx:
            print(xx)
            return None

    @property
    def get_image(self):
        try:
            images = ProductImage.objects.filter(product_uuid=self.uuid, active=True)
            return images
        except Exception as xx:
            print(xx)
            return None

    def get_feedback_stars(self):
        try:
            from cart.models import Feedback
            avg_rating = Feedback.objects.filter(
                product_uuid=self.uuid,
                # active=True,
                rating__isnull=False
            ).aggregate(avg=Avg('rating'))['avg']

            return round(avg_rating, 1) if avg_rating is not None else 0
        except Exception as e:
            print("Lỗi tính feedback:", e)
            return 0


class ProductImage(models.Model):
    name = models.CharField(max_length=128,
                            editable=True,
                            unique=False)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
    product_uuid = models.UUIDField(default=UUID4,
                                    max_length=64,
                                    unique=False,
                                    editable=True)
    image = models.ImageField(upload_to='product_image_upload/%Y/%m/%d/',
                              blank=True,
                              null=True,
                              # default='default/default_product_thumbnail.png'
                              )
    active = models.BooleanField(default=True,
                                 null=False,
                                 blank=False,
                                 editable=True)
    created_at = models.DateTimeField(default=djnow)
    updated_at = models.DateTimeField(default=djnow)

    def __str__(self):
        return f"Image{self.name}"


class ProductThumbnail(models.Model):
    name = models.CharField(max_length=128,
                            editable=True,
                            unique=False)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
    product_uuid = models.UUIDField(default=UUID4,
                                    max_length=64,
                                    unique=False,
                                    editable=True)
    thumbnail = models.ImageField(upload_to='product_thumbnail_upload/%Y/%m/%d/',
                                  blank=True,
                                  null=True,
                                  # default='default/default_product_thumbnail.png'
                                  )
    active = models.BooleanField(default=True,
                                 null=False,
                                 blank=False,
                                 editable=True)
    created_at = models.DateTimeField(default=djnow)
    updated_at = models.DateTimeField(default=djnow)

    def __str__(self):
        return f"Image{self.name}"


class Feedback(models.Model):
    name = models.CharField(max_length=128,
                            editable=True,
                            unique=False)
    uuid = models.UUIDField(default=UUID4,
                            unique=True,
                            editable=False)
    product_uuid = models.UUIDField(default=UUID4,
                                    max_length=64,
                                    unique=False,
                                    editable=True)
    account_uuid = models.UUIDField(default=UUID4,
                                    max_length=64,
                                    unique=False,
                                    editable=True)
    order_uuid = models.UUIDField(default=UUID4,
                                  max_length=64,
                                  unique=False,
                                  editable=True)
    comment = models.TextField(blank=True,
                               null=True,
                               editable=True)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        blank=True,
        null=True,
        help_text="Đánh giá từ 1 đến 5 sao"
    )
    feedback_image = models.ImageField(upload_to='feedback_image_upload/%Y/%m/%d/',
                                       blank=True,
                                       null=True)
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
# class Meta:
#     unique_together = ("order_uuid", "product_uuid")

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# @receiver(post_save, sender=Product)
# def create_default_product_image(sender, instance, created, **kwargs):
#     if created:
#         from .models import ProductImage, ProductThumbnail
#         # Kiểm tra nếu chưa có image nào mới tạo
#         if not ProductImage.objects.filter(product_uuid=instance.uuid).exists():
#             ProductImage.objects.create(
#                 name=f"Image for {instance.name}",
#                 product_uuid=instance.uuid,
#                 active=True,
#                 # image và thumbnail sẽ dùng default nên không cần chỉ định
#             )
#         # Kiểm tra nếu chưa có image nào mới tạo
#         if not ProductThumbnail.objects.filter(product_uuid=instance.uuid).exists():
#             ProductThumbnail.objects.create(
#                 name=f"Image for {instance.name}",
#                 product_uuid=instance.uuid,
#                 active=True,
#                 # image và thumbnail sẽ dùng default nên không cần chỉ định
#             )
