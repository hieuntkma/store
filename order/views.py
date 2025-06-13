from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now as djnow

from cart.models import CartItem, Cart


# Create your views here.
@login_required(login_url='account:signin_view')
def create_order_view(request):
    context = {}
    # my_cart = Cart.objects.filter(account_uuid=request.user.uuid)
    # cart_item_checker = CartItem.objects.filter(cart_uuid=my_cart.uuid, active=True)
    # if cart_item_checker:
    #     return
    template = loader.get_template(str('order/fruitable/order_view.html'))
    return HttpResponse(template.render(context, request))

#draft
from django.http import JsonResponse
from django.views.decorators.http import require_GET
@require_GET
def preview_cart_api_view(request):
    # Fake data
    cart_data = {
        "items": [
            {
                "name": "Chuối",
                "price": 31000,
                "quantity": 1,
                "image": "//product.hstatic.net/200000281397/product/upload_74679edb847d46d4ab017f5c1ddc3368_large.jpg"
            },
            {
                "name": "Táo",
                "price": 20000,
                "quantity": 1,
                "image": "//product.hstatic.net/200000281397/product/upload_74679edb847d46d4ab017f5c1ddc3368_large.jpg"
            },
            {
                "name": "Nho",
                "price": 100000,
                "quantity": 1,
                "image": "//product.hstatic.net/200000281397/product/upload_74679edb847d46d4ab017f5c1ddc3368_large.jpg"
            }
        ],
        "total": 31000
    }
    return JsonResponse(cart_data)
