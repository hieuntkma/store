import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now as djnow
from .models import *
from cart.models import *
import datetime
from django.db import transaction
from uuid import uuid4
from django.core.paginator import Paginator
from django.utils.timesince import timesince


@require_POST
def create_order_api_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Phương thức không hợp lệ'}, status=405)

    try:
        cart_item_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu không hợp lệ'}, status=400)

    try:
        with transaction.atomic():
            # 1. Tạo Order
            order_uuid = uuid4()
            order = Order.objects.create(
                uuid=order_uuid,
                name=f"Đơn hàng {order_uuid}",
                account_uuid=request.user.uuid,
                total_price=cart_item_data['total_price'],
                shipping_price=cart_item_data['shipping_price'],
                status="pending"
            )

            # 2. Tạo từng OrderItem
            for item in cart_item_data['items']:
                OrderItem.objects.create(
                    name=item['name'],
                    uuid=uuid4(),
                    order_uuid=order_uuid,
                    product_uuid=item['product_uuid'],
                    unit_price=item['unit_price'],
                    product_name=item['name'],
                    quantity=item['quantity']
                )

            # 3. Tạo Bill
            Bill.objects.create(
                name=f"Thông nhin nhận hàng của {order_uuid}",
                uuid=uuid4(),
                order_uuid=order_uuid,
                recipient_name=f"{cart_item_data['last_name']} {cart_item_data['first_name']}",
                first_name=cart_item_data['first_name'],
                last_name=cart_item_data['last_name'],
                delivery_address=cart_item_data['delivery_address'],
                note=cart_item_data.get('note', ''),
                recipient_phone=cart_item_data['phone'],
                recipient_email=cart_item_data.get('email', '')
            )

            cart = Cart.objects.filter(account_uuid=request.user.uuid, active=True).first()
            if cart:
                CartItem.objects.filter(cart_uuid=cart.uuid, active=True).update(active=False)
        return JsonResponse({'success': True, 'message': 'Đặt hàng thành công!'}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# @require_GET
@login_required
def get_user_orders_api_view(request):
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        orders = Order.objects.filter(account_uuid=request.user.uuid).order_by('-created_at')
        paginator = Paginator(orders, page_size)
        page_obj = paginator.get_page(page)

        order_list = []
        for order in page_obj:
            order_list.append({
                'uuid': str(order.uuid),
                'code': str(order.uuid),
                'created_at': order.created_at,
                'created_at_human': timesince(order.created_at, djnow()) + ' trước',
                'total_price': order.total_price,
                'shipping_price': order.shipping_price,
                'payment_status': 'Đã thanh toán' if order.status == 'delivered' else 'Chưa thanh toán',
                'delivery_status': order.get_status_display() if hasattr(order, 'get_status_display') else order.status
            })

        return JsonResponse({
            'success': True,
            'orders': order_list,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
        }, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_order_detail_api_view(request, uuid):
    try:
        order = Order.objects.filter(uuid=uuid, account_uuid=request.user.uuid).first()
        items = OrderItem.objects.filter(order_uuid=order.uuid)
        bill = Bill.objects.filter(order_uuid=order.uuid).first()

        return JsonResponse({
            "data": {
                "uuid": str(order.uuid),
                "code": order.name,
                "status": order.get_status_display(),
                "payment_status": "Đã thanh toán" if order.status == "delivered" else "Chưa thanh toán",
                "total_price": order.total_price,
                "created_at": order.created_at,
                'shipping_price': order.shipping_price,

                # 🆕 Thông tin người nhận hàng
                "recipient_name": bill.recipient_name,
                "delivery_address": bill.delivery_address,
                "recipient_phone": bill.recipient_phone,
                "recipient_email": bill.recipient_email,
                "note": bill.note,

                # Danh sách sản phẩm
                "items": [
                    {
                        "product_uuid": item.product_uuid,
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "total": item.unit_price * item.quantity,
                        "thumbnail": item.get_thumbnail
                    }
                    for item in items
                ]
            }
        }, status=200)

    except Order.DoesNotExist:
        return JsonResponse({"error": "Đơn hàng không tồn tại hoặc bạn không có quyền truy cập."}, status=404)

    except Exception as e:
        return JsonResponse({"error": "Lỗi máy chủ nội bộ.", "detail": str(e)}, status=500)


@csrf_exempt
def cancel_order_api_view(request, order_uuid):
    if request.method == "POST":
        try:
            order = Order.objects.get(uuid=order_uuid)
            if order.status in ['pending', 'confirmed']:
                order.status = 'cancelled'
                order.save()
                return JsonResponse({"message": "Order cancelled"}, status=200)
            else:
                return JsonResponse({"error": "Không thể hủy đơn trong trạng thái hiện tại"}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Không tìm thấy đơn hàng"}, status=404)
