import json
import random
from uuid import uuid4

from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

import datetime

from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Categories, Product, Feedback


def category_list_api_view(request):
    if request.method == "GET":
        categories = Categories.objects.filter(active=True)[:5]
        data = [
            {
                "uuid": str(cat.uuid),
                "name": cat.name,
                "desc": cat.desc,
                "created_at": cat.created_at
            }
            for cat in categories
        ]
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


def product_list_api(request):
    page = request.GET.get('page', 1)  # Mặc định là trang 1
    per_page = 9  # 9 sản phẩm mỗi trang

    products = Product.objects.filter(active=True).order_by('-created_at')
    paginator = Paginator(products, per_page)

    try:
        current_page = paginator.page(page)
    except Exception:
        return JsonResponse({'error': 'Trang không tồn tại'}, status=404)

    data = []
    for product in current_page:
        data.append({
            'uuid': str(product.uuid),
            'name': product.name,
            'product_name': product.product_name,
            'desc': product.desc,
            'price': product.price,
            'thumbnail_url': product.get_thumbnail,
            'sale_price': product.sale_price,
            'stock_quantity': product.stock_quantity,
            'quantity': product.quantity,
            'categories': product.get_categories(),
            'created_at': product.created_at,
            'updated_at': product.updated_at,
        })

    return JsonResponse({
        'results': data,
        'total_pages': paginator.num_pages,
        'current_page': current_page.number,
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
    }, safe=False)


def filter_products_api(request):
    page = request.GET.get('page', 1)
    price_range = request.GET.get('price_range', '')
    category_name = request.GET.get('category', '')
    per_page = 9

    products = Product.objects.filter(active=True)

    # Lọc theo khoảng giá
    if price_range:
        if '+' in price_range:
            min_price = int(price_range.replace('+', ''))
            products = products.filter(sale_price__gte=min_price)
        elif '-' in price_range:
            min_price, max_price = map(int, price_range.split('-'))
            products = products.filter(sale_price__gte=min_price, sale_price__lte=max_price)

    # Lọc theo danh mục sản phẩm
    if category_name:
        from product.models import Categories
        category = Categories.objects.filter(name=category_name, active=True).first()
        if category:
            products = products.filter(categories_uuid=category.uuid)
    sort_by = request.GET.get('sort_by', '')

    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'oldest':
        products = products.order_by('created_at')
    elif sort_by == 'price_asc':
        products = products.order_by('sale_price')
    elif sort_by == 'price_desc':
        products = products.order_by('-sale_price')

    paginator = Paginator(products, per_page)

    try:
        current_page = paginator.page(page)
    except:
        return JsonResponse({'error': 'Trang không tồn tại'}, status=404)

    data = []
    for product in current_page:
        data.append({
            'uuid': str(product.uuid),
            'name': product.name,
            'product_name': product.product_name,
            'desc': product.desc,
            'price': product.price,
            'thumbnail_url': product.get_thumbnail,
            'sale_price': product.sale_price,
            'stock_quantity': product.stock_quantity,
            'quantity': product.quantity,
            'categories': product.get_categories(),
            'created_at': product.created_at,
            'updated_at': product.updated_at,
        })

    return JsonResponse({
        'results': data,
        'total_pages': paginator.num_pages,
        'current_page': current_page.number,
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
    })


@require_GET
def related_product_list_api_view(request, uuid):
    product = get_object_or_404(Product, uuid=uuid, active=True)

    related_products = Product.objects.filter(
        categories_uuid=product.categories_uuid,
        active=True
    ).exclude(uuid=product.uuid).order_by('-created_at')[:8]

    data = [
        {
            "uuid": str(p.uuid),
            "product_name": p.product_name,
            "thumbnail": str(p.get_thumbnail),
            "category": str(p.get_categories()),
            "price": int(p.price),
            "sale_price": int(p.sale_price) if p.sale_price else None,
        }
        for p in related_products
    ]

    return JsonResponse({"products": data})


from order.models import OrderItem  # Đảm bảo đúng import
from django.db.models import Sum
from order.models import Order
from django.urls import reverse


@csrf_exempt
def best_seller_products_api_view(request):
    """
    API trả về danh sách sản phẩm bán chạy nhất (đã giao thành công).
    Optional: ?limit=6 để giới hạn số lượng trả về.
    """
    limit = request.GET.get('limit')
    try:
        limit = int(limit) if limit else 6
    except ValueError:
        return JsonResponse({'error': 'limit must be an integer'}, status=400)

    # Truy vấn các sản phẩm bán chạy
    best_sellers = (
        OrderItem.objects.filter(
            active=True,
            order_uuid__in=Order.objects.filter(status='delivered', active=True).values('uuid')
        )
        .values('product_uuid')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:limit]
    )

    product_uuids = [item['product_uuid'] for item in best_sellers]
    products = Product.objects.filter(uuid__in=product_uuids, active=True)

    # Trả dữ liệu kèm URL
    data = []
    for p in products:
        data.append({
            'uuid': str(p.uuid),
            'name': p.name,
            'price': p.price,
            'sale_price': p.sale_price,
            'thumbnail': p.get_thumbnail if hasattr(p, 'get_thumbnail') else '',
            'detail_url': reverse('product:shop_detail', args=[str(p.uuid)])
        })

    return JsonResponse({'data': data}, status=200)


def product_detail(request, uuid):
    try:
        product = Product.objects.get(uuid=uuid)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

    data = {
        'uuid': str(product.uuid),
        'name': product.name,
        'product_name': product.product_name,
        'desc': product.desc,
        'price': product.price,
        'sale_price': product.sale_price,
        'stock_quantity': product.stock_quantity,
        'quantity': product.quantity,
        'active': product.active,
        'image_url': '//product.hstatic.net/200000281397/product/upload_b16e299053954c0aa68414585267970e_large.jpg',
        'categories': product.get_categories(),
        'created_at': product.created_at,
        'updated_at': product.updated_at,
    }

    return JsonResponse(data, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_feedback_api_view(request):
    """
    API để người dùng gửi đánh giá sản phẩm.
    Yêu cầu: Đã đăng nhập, đã mua hàng, gửi đủ thông tin.
    """
    try:
        account_uuid = request.user.uuid
        product_uuid = request.data.get('product_uuid')
        order_uuid = request.data.get('order_uuid')
        comment = request.data.get('comment')
        rating = request.data.get('rating')
        feedback_image = request.FILES.get('feedback_image')

        if not product_uuid or not order_uuid or not rating:
            return Response({'error': 'Thiếu thông tin bắt buộc.'}, status=status.HTTP_400_BAD_REQUEST)

        # (Tùy chọn) kiểm tra order có thực sự thuộc user không
        from order.models import Order
        if not Order.objects.filter(uuid=order_uuid, account_uuid=account_uuid, active=True).exists():
            return Response({'error': 'Không tìm thấy đơn hàng phù hợp.'}, status=status.HTTP_404_NOT_FOUND)

        Feedback.objects.create(
            name=f"Feedback by {request.user}",
            product_uuid=product_uuid,
            order_uuid=order_uuid,
            account_uuid=account_uuid,
            comment=comment,
            rating=rating,
            feedback_image=feedback_image
        )

        return Response({'status': 'success', 'message': 'Đánh giá đã được gửi.'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
