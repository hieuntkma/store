import os
import json
from uuid import uuid4
from django.core.files import File
from django.core.management.base import BaseCommand
from product.models import Product, ProductImage, ProductThumbnail

# Map tên danh mục sang UUID có sẵn
CATEGORY_UUID_MAP = {
    "Thịt tươi sống": "3adb4434-73fc-4165-971c-6f95c5ea223f",
    "Các loại hạt": "26491d99-aaf0-4333-a57a-0beaeb4f28d8",
    "Hải sản": "afd6cf83-e32f-4246-b390-f3916795a416",
    "Hoa quả": "2f741aab-0cdf-4123-a46f-0caef9631883",
    "Rau củ": "ba228fc0-4b0f-4c24-af14-edb373074da6"
}

class Command(BaseCommand):
    help = 'Import products from Product_Image_2'

    def handle(self, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "crawl/Product_Image")
        if not os.path.exists(base_path):
            self.stdout.write(self.style.ERROR(f"❌ Không tìm thấy thư mục: {base_path}"))
            return

        for folder in os.listdir(base_path):
            product_dir = os.path.join(base_path, folder)
            if not os.path.isdir(product_dir):
                continue

            json_path = os.path.join(product_dir, f"{folder}.json")
            if not os.path.exists(json_path):
                self.stdout.write(self.style.WARNING(f"⚠️ Bỏ qua {folder}: không có file JSON"))
                continue

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Lấy UUID danh mục
            category_uuid = CATEGORY_UUID_MAP.get(data["category"])
            if not category_uuid:
                self.stdout.write(self.style.WARNING(f"⚠️ Bỏ qua {folder}: không có danh mục hợp lệ"))
                continue

            # Xử lý giá
            original_price = data["original_price"]
            sale_price = data["sale_price"]
            if original_price == 0:
                original_price = sale_price + 20000

            # Tạo sản phẩm
            product_uuid = uuid4()
            product = Product.objects.create(
                uuid=product_uuid,
                name=data["title"],
                product_name=data["title"],
                desc=data["description"],
                price=original_price,
                sale_price=sale_price,
                categories_uuid=category_uuid,
                quantity=1,
                stock_quantity=1,
                active=True
            )

            # Duyệt toàn bộ ảnh
            images = [f for f in os.listdir(product_dir) if f.startswith(folder) and f.endswith(".png")]
            images.sort()

            for image_name in images:
                image_path = os.path.join(product_dir, image_name)
                with open(image_path, "rb") as img_file:
                    product_image = ProductImage.objects.create(
                        uuid=uuid4(),
                        product_uuid=product_uuid,
                        name=image_name,
                        active=True
                    )
                    product_image.image.save(image_name, File(img_file), save=True)

            # Thumbnail lấy đúng ảnh _1
            thumbnail_image_name = f"{folder}_1.png"
            thumbnail_path = os.path.join(product_dir, thumbnail_image_name)

            if os.path.exists(thumbnail_path):
                with open(thumbnail_path, "rb") as thumb_file:
                    product_thumbnail = ProductThumbnail.objects.create(
                        uuid=uuid4(),
                        product_uuid=product_uuid,
                        name=thumbnail_image_name,
                        active=True
                    )
                    product_thumbnail.thumbnail.save(thumbnail_image_name, File(thumb_file), save=True)
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Không tìm thấy ảnh thumbnail cho {folder}"))

            self.stdout.write(self.style.SUCCESS(f"✅ Đã tạo sản phẩm: {data['title']}"))
