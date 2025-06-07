from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Product)
admin.site.register(Categories)
admin.site.register(Feedback)
admin.site.register(ProductImage)
admin.site.register(ProductThumbnail)