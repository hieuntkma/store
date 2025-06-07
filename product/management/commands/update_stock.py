from django.core.management.base import BaseCommand
from product.models import Product

class Command(BaseCommand):
    help = "Cập nhật stock_quantity = 100 cho tất cả sản phẩm"

    def handle(self, *args, **kwargs):
        updated = 0
        products = Product.objects.all()
        for product in products:
            product.stock_quantity = 100
            product.save(update_fields=["stock_quantity", "updated_at"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Đã cập nhật {updated} sản phẩm thành công."))