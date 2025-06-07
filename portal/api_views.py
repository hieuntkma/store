import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from account.models import Account
import datetime
from product.models import *
from cart.models import *


@require_GET
def category_tab_with_products_api_view(request):
    # ✅ Lấy các category theo tên cố định
    fixed_category_names = ["Rau củ", "Hoa quả", "Hải sản", "Các loại hạt", "Thịt tươi sống"]
    categories = Categories.objects.filter(name__in=fixed_category_names, active=True)

    # ✅ Tạo tab "Tất cả"
    all_products = Product.objects.filter(active=True).order_by("-created_at")[:8]
    tabs = [{
        "title": "Tất cả",
        "slug": "all",
        "products": [
            {
                "name": p.name,
                "price": int(p.price),
                "sale_price": int(p.sale_price) if p.sale_price else None,
                "thumbnail": str(p.get_thumbnail),
                "uuid": str(p.uuid),
                "category": str(p.get_categories())
            }
            for p in all_products
        ]
    }]

    # ✅ Tạo các tab còn lại theo tên danh mục cụ thể
    for cat in categories:
        products = Product.objects.filter(categories_uuid=cat.uuid, active=True).order_by("-created_at")[:8]
        tabs.append({
            "title": cat.name,
            "slug": f"cat-{cat.uuid.hex[:6]}",
            "products": [
                {
                    "name": p.name,
                    "price": int(p.price),
                    "sale_price": int(p.sale_price) if p.sale_price else None,
                    "thumbnail": str(p.get_thumbnail),
                    "uuid": str(p.uuid),
                    "category": cat.name
                }
                for p in products
            ]
        })

    return JsonResponse({"tabs": tabs}, safe=False)


@require_GET
def vegetable_product_list_api_view(request):
    try:
        category = Categories.objects.get(name__icontains="Rau")  # Tìm danh mục chứa từ "Rau"
    except Categories.DoesNotExist:
        return JsonResponse({"products": []})

    products = Product.objects.filter(categories_uuid=category.uuid, active=True).order_by("-created_at")[:10]
    data = [
        {
            "uuid": str(p.uuid),
            "product_name": p.name,
            "thumbnail": str(p.get_thumbnail),
            "category": str(p.get_categories()),
            "price": int(p.price),
            "sale_price": int(p.sale_price) if p.sale_price else None,
        }
        for p in products
    ]

    return JsonResponse({"products": data})
