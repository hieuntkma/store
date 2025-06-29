from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Feedback
from uuid import uuid4
from order.models import Order  # dùng để kiểm tra đơn hàng nếu cần
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now as djnow
from .models import *
from django.db.models import Avg

# Create your views here.


def shop_detail_view(request, uuid):
    product = get_object_or_404(Product, uuid=uuid, active=True)

    feedbacks = Feedback.objects.filter(product_uuid=uuid, active=True).order_by('-created_at')
    average_rating = feedbacks.aggregate(avg=Avg('rating'))['avg'] or 0

    context = {
        'product': {
            'uuid': str(product.uuid),
            'name': product.name,
            'product_name': product.product_name,
            'desc': product.desc,
            'price': product.price,
            'sale_price': product.sale_price,
            'stock_quantity': product.stock_quantity,
            'quantity': product.quantity,
            'active': product.active,
            'thumbnail': product.get_thumbnail,
            'images': product.get_image,
            'categories': product.get_categories(),
            'created_at': product.created_at,
            'updated_at': product.updated_at,
        },
        'feedbacks': feedbacks,
        'average_rating': round(average_rating, 1)
    }

    return render(request, 'product/fruitable/shop-detail.html', context)



def shop_view(request):
    context = {}
    context["breadcrumb_title"] = "Tất cả"
    context["categories"] = Categories.objects.all()
    selected_category = request.GET.get('category', '')
    context["selected_category"] = selected_category

    return render(request, 'product/fruitable/shop.html', context)


def product_search_view(request):
    context = {}
    query = request.GET.get('q', '').strip()
    products = []

    if query:
        products = Product.objects.filter(product_name__icontains=query, active=True)

    context = {
        'query': query,
        'products': products,
    }
    context['breadcrumb_title'] = "Tìm kiếm"
    return render(request, 'product/fruitable/search_results.html', context)


@login_required(login_url='account:signin')
def feedback_view(request):
    if request.method == "POST":
        product_uuid = request.POST.get("product_uuid")
        order_uuid = request.POST.get("order_uuid")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        feedback_image = request.FILES.get("feedback_image")

        # Nếu thiếu thông tin → quay lại trang hiện tại với mã đơn
        if not (product_uuid and order_uuid and rating):
            messages.error(request, "Vui lòng nhập đầy đủ thông tin bắt buộc.")
            return redirect(f'/product/feedback/?order={order_uuid}')

        # Kiểm tra đơn có thuộc user hay không
        if not Order.objects.filter(uuid=order_uuid, account_uuid=request.user.uuid).exists():
            messages.error(request, "Không tìm thấy đơn hàng tương ứng.")
            return redirect('account:order_list_view')

        # Tạo feedback
        Feedback.objects.create(
            name=f"Feedback của {request.user}",
            uuid=uuid4(),
            product_uuid=product_uuid,
            order_uuid=order_uuid,
            account_uuid=request.user.uuid,
            comment=comment,
            rating=rating,
            feedback_image=feedback_image,
            created_at=djnow(),
            updated_at=djnow()
        )

        messages.success(request, "Đánh giá đã được gửi thành công!")
        return redirect(f'/product/feedback/?order={order_uuid}')

    # ❗ Đây là xử lý GET: người dùng vừa truy cập /product/feedback/?order=...
    order_uuid = request.GET.get("order")
    if not order_uuid:
        # Nếu người dùng gõ URL trực tiếp sai → báo lỗi
        messages.error(request, "Thiếu thông tin đơn hàng để hiển thị đánh giá.")
        return redirect('account:order_list_view')

    # ✅ Truyền order_uuid sang template
    return render(request, 'product/fruitable/feedback.html', {
        "order_uuid": order_uuid
    })


