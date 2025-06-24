import json
import os
import random
from uuid import uuid4

from django.core.exceptions import ValidationError, ObjectDoesNotExist
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
from django.utils.timezone import now as djnow

import datetime

from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *


# region HNT Category
@login_required(login_url='account:signin')
def create_category_api_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            name = data.get("name")
            desc = data.get("desc", "")

            if not name:
                return JsonResponse({"error": "Tên danh mục là bắt buộc."}, status=400)

            category = Categories.objects.create(
                name=name,
                desc=desc,
                active=True,
                created_at=djnow()
            )

            return JsonResponse({
                "success": True,
                "message": "Tạo danh mục thành công.",
                "data": {
                    "uuid": str(category.uuid),
                    "name": category.name,
                    "desc": category.desc,
                    "created_at": category.created_at,
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Dữ liệu không hợp lệ (không phải JSON)."}, status=400)


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


@login_required(login_url='account:signin')
def admin_category_list_api_view(request):
    if request.method == "GET":
        page = request.GET.get("page", 1)
        # per_page = request.GET.get("per_page", 10)  # lấy từ query param
        # try:
        #     per_page = int(per_page)
        # except ValueError:
        #     per_page = 10
        categories = Categories.objects.filter(active=True).order_by("-created_at")
        # paginator = Paginator(categories, per_page)

        # try:
        #     current_page = paginator.page(page)
        # except Exception:
        #     return JsonResponse({"error": "Trang không tồn tại."}, status=404)

        data = [
            {
                "uuid": str(cat.uuid),
                "name": cat.name,
                "desc": cat.desc,
                "created_at": cat.created_at
            }
            # for cat in current_page
            for cat in categories
        ]

        return JsonResponse({
            "results": data,
            # "total_pages": paginator.num_pages,
            # "current_page": current_page.number,
            # "has_next": current_page.has_next(),
            # "has_previous": current_page.has_previous(),
        }, safe=False)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required(login_url='account:signin')
def edit_category_api_view(request, cat_uuid):
    try:
        category = Categories.objects.get(uuid=cat_uuid)
    except Categories.DoesNotExist:
        return JsonResponse({"error": "Không tìm thấy danh mục."}, status=404)

    if request.method == "GET":
        data = {
            "uuid": str(category.uuid),
            "name": category.name,
            "desc": category.desc,
            "created_at": category.created_at,
        }
        return JsonResponse(data)

    elif request.method in ["PUT", "POST"]:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Dữ liệu không hợp lệ."}, status=400)

        name = data.get("name")
        desc = data.get("desc")

        if not name:
            return JsonResponse({"error": "Tên danh mục là bắt buộc."}, status=400)

        # Kiểm tra trùng tên với danh mục khác
        if Categories.objects.filter(name=name).exclude(uuid=cat_uuid).exists():
            return JsonResponse({"error": "Danh mục đã tồn tại."}, status=400)

        category.name = name
        category.desc = desc or ""
        category.save()

        return JsonResponse({
            "success": True,
            "message": "Cập nhật danh mục thành công.",
            "data": {
                "uuid": str(category.uuid),
                "name": category.name,
                "desc": category.desc,
                "updated_at": category.updated_at
            }
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required(login_url='account:signin')
def delete_category_api_view(request, cat_uuid):
    if request.method in ["POST", "DELETE"]:  # Cho phép cả POST nếu bạn không dùng AJAX DELETE
        try:
            category = Categories.objects.get(uuid=cat_uuid, active=True)
        except Categories.DoesNotExist:
            return JsonResponse({"error": "Danh mục không tồn tại."}, status=404)

        category.delete()

        return JsonResponse({
            "success": True,
            "message": f"Đã xóa danh mục: {category.name}"
        }, status=200)

    return JsonResponse({"error": "Phương thức không được hỗ trợ."}, status=405)


# region HNT Product
def product_list_api(request):
    page = request.GET.get('page', 1)  # Mặc định là trang 1
    # per_page = 9  # 9 sản phẩm mỗi trang

    products = Product.objects.filter(active=True).order_by('-created_at')
    # paginator = Paginator(products, per_page)

    # try:
    #     current_page = paginator.page(page)
    # except Exception:
    #     return JsonResponse({'error': 'Trang không tồn tại'}, status=404)

    data = []
    # for product in current_page:
    for product in products:
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
            'status': product.active
        })

    return JsonResponse({
        'results': data,
        # 'total_pages': paginator.num_pages,
        # 'current_page': current_page.number,
        # 'has_next': current_page.has_next(),
        # 'has_previous': current_page.has_previous(),
    }, safe=False)


@login_required(login_url='account:signin')
def admin_create_product_api_view(request):
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ request.POST
            product_name = request.POST.get('product_name')
            categories_uuid = request.POST.get('categories')
            desc = request.POST.get('desc')
            price = int(request.POST.get('price_raw', 0))
            sale_price = int(request.POST.get('sale_price_raw', 0))
            stock_quantity = int(request.POST.get('stock_quantity', 1))
            is_visible = request.POST.get('is_visible', 'true').lower() == 'true'

            # Kiểm tra dữ liệu cơ bản
            if not product_name or not categories_uuid or price < 0 or stock_quantity < 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Dữ liệu không hợp lệ'
                }, status=400)

            # Tạo sản phẩm mới
            product = Product(
                product_name=product_name,
                name=product_name,
                # uuid=uuid.uuid4(),
                categories_uuid=categories_uuid,
                desc=desc,
                price=price,
                sale_price=sale_price,
                stock_quantity=stock_quantity,
                quantity=stock_quantity,
                active=is_visible,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            product.save()
            print(request.FILES)
            # Xử lý upload hình ảnh sản phẩm
            if 'images' in request.FILES:
                images = request.FILES.getlist('images')
                for image in images:
                    try:
                        product_image = ProductImage(
                            name=image.name,
                            # uuid=uuid.uuid4(),  # Thêm uuid để tránh lỗi
                            product_uuid=product.uuid,
                            image=image,
                            active=True,
                            created_at=timezone.now(),
                            updated_at=timezone.now()
                        )
                        product_image.save()
                    except ValidationError as e:
                        product.delete()  # Xóa sản phẩm nếu ảnh không hợp lệ
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Lỗi khi lưu ảnh: {str(e)}'
                        }, status=400)
                    except Exception as e:
                        product.delete()  # Xóa sản phẩm nếu có lỗi khác
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Lỗi không xác định khi lưu ảnh: {str(e)}'
                        }, status=500)

            # Xử lý upload thumbnail
            if 'thumbnail' in request.FILES:
                thumbnail = request.FILES['thumbnail']
                try:
                    product_thumbnail = ProductThumbnail(
                        name=thumbnail.name,
                        # uuid=uuid.uuid4(),  # Thêm uuid để tránh lỗi
                        product_uuid=product.uuid,
                        thumbnail=thumbnail,
                        active=True,
                        created_at=timezone.now(),
                        updated_at=timezone.now()
                    )
                    product_thumbnail.save()
                except ValidationError as e:
                    product.delete()  # Xóa sản phẩm nếu thumbnail không hợp lệ
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Lỗi khi lưu thumbnail: {str(e)}'
                    }, status=400)
                except Exception as e:
                    product.delete()  # Xóa sản phẩm nếu có lỗi khác
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Lỗi không xác định khi lưu thumbnail: {str(e)}'
                    }, status=500)

            return JsonResponse({
                'status': 'success',
                'message': 'Sản phẩm đã được tạo thành công',
                'product': {
                    'uuid': str(product.uuid),
                    'name': product.name,
                    'price': product.price,
                    'sale_price': product.sale_price,
                    'stock_quantity': product.stock_quantity,
                    'active': product.active
                }
            }, status=201)

        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Dữ liệu không hợp lệ: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Lỗi server: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Phương thức không được hỗ trợ'
    }, status=405)


@login_required(login_url='account:signin')
def admin_delete_product_api_view(request, product_uuid):
    if request.method == 'POST':
        try:
            # Tìm sản phẩm dựa trên UUID
            product = Product.objects.get(uuid=product_uuid)

            # Lấy tất cả ảnh sản phẩm liên quan
            product_images = ProductImage.objects.filter(product_uuid=product_uuid)

            # Lấy thumbnail liên quan
            product_thumbnail = ProductThumbnail.objects.filter(product_uuid=product_uuid, active=True).first()

            # Xóa file ảnh khỏi hệ thống tệp trước khi xóa khỏi cơ sở dữ liệu
            media_root = settings.MEDIA_ROOT
            for image in product_images:
                if image.image and os.path.isfile(os.path.join(media_root, image.image.name)):
                    os.remove(os.path.join(media_root, image.image.name))
                image.delete()

            if product_thumbnail and product_thumbnail.thumbnail and os.path.isfile(
                    os.path.join(media_root, product_thumbnail.thumbnail.name)):
                os.remove(os.path.join(media_root, product_thumbnail.thumbnail.name))
                product_thumbnail.delete()

            product.delete()

            return JsonResponse({
                'status': 'success',
                'message': 'Sản phẩm và các tệp liên quan đã được xóa thành công'
            }, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Sản phẩm không tồn tại hoặc đã bị xóa'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Có lỗi xảy ra: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Phương thức không được hỗ trợ'
    }, status=405)


#### simple data table không hỗ trợ phân trang cả FE và BE nên phải list tất cả
@login_required(login_url='account:signin')
def admin_product_list_api_view(request):
    page = request.GET.get('page', 1)  # Mặc định là trang 1
    # per_page = 10  # 9 sản phẩm mỗi trang

    products = Product.objects.all().order_by('-created_at')
    # paginator = Paginator(products, per_page)

    # try:
    #     current_page = paginator.page(page)
    # except Exception:
    #     return JsonResponse({'error': 'Trang không tồn tại'}, status=404)

    data = []
    # for product in current_page:
    for product in products:
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
            'status': product.active
        })

    return JsonResponse({
        'results': data,
        # 'total_pages': paginator.num_pages,
        # 'current_page': current_page.number,
        # 'has_next': current_page.has_next(),
        # 'has_previous': current_page.has_previous(),
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
