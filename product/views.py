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


# Create your views here.


def shop_detail_view(request, uuid):
    context = {}
    product = get_object_or_404(Product, uuid=uuid, active=True)

    # related_products = Product.objects.filter(
    #     categories_uuid=product.categories_uuid,
    #     active=True
    # ).exclude(uuid=product.uuid).order_by('-created_at')[:8]

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
        # 'related_products': related_products,
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

        if not (product_uuid and order_uuid and rating):
            messages.error(request, "Vui lòng nhập đầy đủ thông tin bắt buộc.")
            return redirect('feedback_view')

        # (tùy chọn) kiểm tra đơn hàng có thuộc user không
        if not Order.objects.filter(uuid=order_uuid, account_uuid=request.user.uuid).exists():
            messages.error(request, "Không tìm thấy đơn hàng tương ứng.")
            return redirect('feedback_view')

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
        return redirect('feedback_view')

    return render(request, 'product/fruitable/feedback.html')


