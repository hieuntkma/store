from django.shortcuts import render
from .models import *

# Create your views here.

def cart_detail_view(request):
    context = {}
    context['breadscrumb_title'] = "Giỏ hàng của tôi"
    # cart = Cart.objects.filter(account_uuid=request.user.uuid, active=True).first()
    # cart_items = CartItem.objects.filter(cart_uuid=cart.uuid, active=True)
    #
    # context['cart_items'] = cart_items
    # context['total_all_item_price'] = cart.get_total_all_item_price

    return render(request, 'cart/fruitable/cart_detail.html', context)
