from django.core.management.base import BaseCommand
from cart.models import CartItem, Cart
from uuid import uuid4, UUID
import random

class Command(BaseCommand):
    help = 'Tạo nhanh nhiều CartItem cho Cart cố định'

    def handle(self, *args, **options):
        count = 5  # bạn có thể thay đổi số lượng tại đây
        for i in range(count):
            item = CartItem.objects.create(
                name=f"Demo Item {i+1}",
                cart_uuid='a6969a4f-8d74-4e42-9b50-8c21e5564802',
                product_uuid=uuid4(),  # giả lập sản phẩm
                quantity=random.randint(1, 5),
                unit_price=random.randint(10000, 50000),
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Tạo {item.name} - SL: {item.quantity}, Giá: {item.unit_price}"))

        self.stdout.write(self.style.SUCCESS(f"🎉 Đã tạo {count} CartItem trong Cart UUID: "))
