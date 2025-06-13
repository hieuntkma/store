import os
import json
import uuid
import re
from django.core.files import File
from django.core.management.base import BaseCommand
from product.models import Product, ProductImage, ProductThumbnail
from django.utils.timezone import now as djnow

CATEGORY_MAPPING = {
    "Thực phẩm tươi sống": "e48a2bba-5c48-4ac4-baa1-49252d4d98a1",
    "Các loại hạt": "86df7725-1b58-43fd-8259-854da6573b37",
    "Hải sản": "90d14910-1482-4285-bdc7-8bd2bb3b7ba2",
    "Hoa quả": "97d0bc88-dbb8-43f3-8283-62dc3bb347f5",
    "Rau củ": "b05f5a47-4bca-4950-b2f9-ec7a31618cd4"
}

# Chuyển "Nấm Lim xanh" → "nam-lim-xanh"
def slugify(name):
    slug = name.lower()
    slug = re.sub(r"[àáạảãâầấậẩẫăằắặẳẵ]", "a", slug)
    slug = re.sub(r"[èéẹẻẽêềếệểễ]", "e", slug)
    slug = re.sub(r"[ìíịỉĩ]", "i", slug)
    slug = re.sub(r"[òóọỏõôồốộổỗơờớợởỡ]", "o", slug)
    slug = re.sub(r"[ùúụủũưừứựửữ]", "u", slug)
    slug = re.sub(r"[ỳýỵỷỹ]", "y", slug)
    slug = re.sub(r"[đ]", "d", slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")

class Command(BaseCommand):
    help = "Import products and images from crawl_data folder"

    def handle(self, *args, **kwargs):
        base_path = "crawl_data"
        info_path = os.path.join(base_path+"/Product_Image", "thong_tin.json")

        if not os.path.exists(info_path):
            self.stdout.write(self.style.ERROR("❌ File thong_tin_san_pham_da_phan_loai.json không tồn tại"))
            return

        with open(info_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for product_data in data:
            try:
                product_name = product_data["title"]
                folder_name = slugify(product_name)
                product_dir = os.path.join(base_path, "Product_Image", folder_name)

                if not os.path.exists(product_dir):
                    self.stdout.write(self.style.WARNING(f"⚠️ Không tìm thấy thư mục ảnh cho: {product_name} ({folder_name})"))
                    continue

                product_uuid = uuid.uuid4()
                category_name = product_data.get("category", "Hoa quả")
                category_uuid = CATEGORY_MAPPING.get(category_name)

                product = Product.objects.create(
                    name=product_name,
                    uuid=product_uuid,
                    product_name=product_name,
                    desc=product_data["description"],
                    price=product_data.get("compare_at_price", 0),
                    sale_price=product_data.get("price", 0),
                    categories_uuid=uuid.UUID(category_uuid),
                    created_at=djnow(),
                    updated_at=djnow()
                )

                images = sorted([
                    img for img in os.listdir(product_dir)
                    if img.lower().endswith((".jpg", ".jpeg", ".png"))
                ])

                for idx, image_file in enumerate(images):
                    image_path = os.path.join(product_dir, image_file)
                    with open(image_path, "rb") as img_f:
                        django_file = File(img_f)
                        if idx == 0:
                            ProductThumbnail.objects.create(
                                name=f"{product_name}_thumbnail",
                                uuid=uuid.uuid4(),
                                product_uuid=product_uuid,
                                thumbnail=django_file,
                                created_at=djnow(),
                                updated_at=djnow()
                            )
                        ProductImage.objects.create(
                            name=f"{product_name}_image_{idx+1}",
                            uuid=uuid.uuid4(),
                            product_uuid=product_uuid,
                            image=django_file,
                            created_at=djnow(),
                            updated_at=djnow()
                        )

                self.stdout.write(self.style.SUCCESS(f"✅ Đã thêm sản phẩm: {product_name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Lỗi khi xử lý {product_data.get('title')}: {e}"))
