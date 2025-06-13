from django.core.management.base import BaseCommand
from order.models import OrderItem
from uuid import uuid4
import random

class Command(BaseCommand):
    help = 'Tạo nhiều OrderItem để test dữ liệu'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Số lượng OrderItem cần tạo')

    def handle(self, *args, **options):
        count = options['count']
        for i in range(count):
            item = OrderItem.objects.create(
                name=f"OrderItem #{i + 1}",
                uuid=uuid4(),
                order_uuid=uuid4(),  # bạn có thể thay bằng order thực nếu muốn
                product_uuid=uuid4(),
                unit_price=random.randint(10000, 50000),
                product_name=f"Sản phẩm {random.randint(1, 100)}",
                quantity=random.randint(1, 5)
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Tạo OrderItem: {item.name}'))

        self.stdout.write(self.style.SUCCESS(f'🎉 Tạo thành công {count} OrderItem!'))