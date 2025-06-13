import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
# #from .models import Account
import datetime
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from uuid import uuid4


@login_required(login_url='account:signin')
@csrf_exempt
def create_cart_item_api_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            account_uuid = data.get('account_uuid')
            product_uuid = data.get('product_uuid')
            quantity = int(data.get('quantity'))

            # Tìm cart đang hoạt động
            cart = Cart.objects.filter(account_uuid=account_uuid, active=True).first()
            if not cart:
                return JsonResponse({'error': 'Cart not found'}, status=404)

            # Kiểm tra sản phẩm
            from product.models import Product
            product = Product.objects.get(uuid=product_uuid, active=True)

            # Nếu đã có item → update
            cart_item = CartItem.objects.filter(cart_uuid=cart.uuid, product_uuid=product_uuid, active=True).first()
            if cart_item:
                cart_item.quantity += quantity
                cart_item.name = product.product_name
                cart_item.unit_price = product.sale_price
                cart_item.save()
            else:
                # Tạo mới
                CartItem.objects.create(
                    name=product.product_name,
                    cart_uuid=cart.uuid,
                    product_uuid=product_uuid,
                    quantity=quantity,
                    unit_price=product.sale_price,
                )
            return JsonResponse({"status": "success", 'message': 'CartItem created'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# @login_required(login_url='account:signin')
# @csrf_exempt
# def update_cart_item_api_view(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             account_uuid = data.get("account_uuid")
#             product_uuid = data.get("product_uuid")
#             quantity = int(data.get("quantity"))
#
#             cart = Cart.objects.filter(account_uuid=account_uuid, active=True).first()
#             if not cart:
#                 return JsonResponse({'error': 'Cart not found'}, status=404)
#             # Kiểm tra cart_item tồn tại
#             cart_item = CartItem.objects.filter(cart_uuid=cart.uuid, product_uuid=product_uuid, active=True).first()
#             if not cart_item:
#                 return JsonResponse({"error": "CartItem not found"}, status=404)
#
#             from product.models import Product  # Đảm bảo bạn có model Product phù hợp
#             # Lấy thông tin sản phẩm (để cập nhật lại đơn giá nếu cần)
#             product = Product.objects.get(uuid=product_uuid, active=True)
#
#             # Cập nhật cart_item
#             cart_item.quantity = quantity
#             cart_item.name = product.product_name
#             cart_item.unit_price = product.sale_price
#             cart_item.save()
#
#             return JsonResponse({"message": "CartItem updated"}, status=200)
#
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)
#
#     return JsonResponse({"error": "Method not allowed"}, status=405)


@api_view(['GET'])
@login_required(login_url='login')
def cart_item_list_api_view(request):
    user = request.user

    # Lấy giỏ hàng hiện tại (active) của người dùng
    cart = Cart.objects.filter(account_uuid=user.uuid, active=True).first()
    if not cart:
        return Response({
            "status": "error",
            "message": "Không tìm thấy giỏ hàng.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)

    cart_items = CartItem.objects.filter(cart_uuid=cart.uuid, active=True).order_by('-created_at')

    items_data = []
    for item in cart_items:
        # print(item.get_thumbnail)
        items_data.append({
            "cart_uuid": item.cart_uuid,
            "product_uuid": str(item.product_uuid),
            "name": item.name,
            "thumbnail": item.get_thumbnail,
            "unit_price": item.unit_price,
            "quantity": item.quantity,
            "total_item_price": item.get_total_item_price,
        })
    if items_data:
        response_data = {
            "status": "success",
            "message": "Lấy thông tin giỏ hàng thành công.",
            "data": {
                "cart_uuid": str(cart.uuid),
                "total_all_item_price": cart.get_total_all_item_price,
                "items": items_data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "status": "empty",
            "message": "Giỏ hàng của bạn đang trống.",
            "data": {
                "cart_uuid": str(cart.uuid),
                "items": []
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)


@csrf_exempt
@login_required
def update_cart_item_api_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_uuid = data.get("product_uuid")
        quantity = int(data.get("quantity", 1))

        cart = Cart.objects.filter(account_uuid=request.user.uuid, active=True).first()
        if not cart:
            return JsonResponse({'error': 'Cart not found'}, status=404)

        cart_item = CartItem.objects.filter(cart_uuid=cart.uuid, product_uuid=product_uuid, active=True).first()
        if not cart_item:
            return JsonResponse({'error': 'Item not found'}, status=404)

        cart_item.quantity = quantity
        cart_item.save()
        return JsonResponse({'status': 'success'})


@csrf_exempt
@login_required
def remove_cart_item_by_product_uuid_api_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_uuid = data.get("product_uuid")

            cart = Cart.objects.filter(account_uuid=request.user.uuid, active=True).first()
            if not cart:
                return JsonResponse({'error': 'Cart not found'}, status=404)

            cart_item = CartItem.objects.filter(cart_uuid=cart.uuid, product_uuid=product_uuid, active=True).first()
            if not cart_item:
                return JsonResponse({'error': 'Item not found'}, status=404)

            cart_item.active = False
            cart_item.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)