from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from product.models import *
from account.models import *
from order.models import *


# Create your views here.

@login_required(login_url='account:signin_view')
def admin_index_view(request):
    context = {}
    context["breadscrumb"] = "Dashboard"
    context["breadscrumb_url"] = reverse('workspace:admin_index_view')
    accounts = Account.objects.all()
    orders = Order.objects.all()
    products = Product.objects.all()
    context["accounts"] = accounts.count()
    context["orders"] = orders.count()
    context["products"] = products.count()
    ordered = Order.objects.filter(status="delivered")
    revenue = 0
    for order in ordered:
        revenue += order.total_price
    context["revenue"] = revenue
    profile = UserProfile.objects.get(account=request.user)
    account = Account.objects.get(uuid=request.user.uuid)
    context["profile_avt"]= "/media/"+ str(profile.avatar)
    print(profile.avatar)
    context["profile_username"]=account.username
    context["profile_fullname"]=profile.get_full_name()
    # template = loader.get_template(str('workspace/mazer/workspace.html'))
    template = loader.get_template(str('workspace/mazer/workspace.html'))
    return HttpResponse(template.render(context, request))


@login_required(login_url='account:signin_view')
def products_management_view(request):
    context = {}
    context["breadscrumb"] = "Sản phẩm"
    context["breadscrumb_url"] = reverse('workspace:products_management_view')
    template = loader.get_template(str('workspace/mazer/products_mgmt.html'))
    return HttpResponse(template.render(context, request))


@login_required(login_url='account:signin_view')
def create_products_management_view(request):
    context = {}
    context["breadscrumb"] = "Sản phẩm"
    context["breadscrumb_url"] = reverse('workspace:create_products_management_view')
    cats = Categories.objects.all()
    context["cats"] = cats
    template = loader.get_template(str('workspace/mazer/create_products_mgmt.html'))
    return HttpResponse(template.render(context, request))


@login_required(login_url='account:signin_view')
def edit_products_management_view(request, product_uuid):
    context = {}
    context["breadscrumb"] = "Sản phẩm"
    context["breadscrumb_url"] = reverse('workspace:create_products_management_view')
    cats = Categories.objects.all()
    context["cats"] = cats
    product = get_object_or_404(Product, uuid=product_uuid)
    context["product"] = product
    template = loader.get_template(str('workspace/mazer/edit_products_mgmt.html'))
    return HttpResponse(template.render(context, request))


@login_required(login_url='account:signin_view')
def categories_management_view(request):
    context = {}
    context["breadscrumb"] = "Danh mục"
    context["breadscrumb_url"] = reverse('workspace:categories_management_view')

    template = loader.get_template(str('workspace/mazer/categories_mgmt.html'))
    return HttpResponse(template.render(context, request))


@login_required(login_url='account:signin_view')
def inventory_management_view(request):
    context = {}
    context["breadscrumb"] = "Kho hàng"
    context["breadscrumb_url"] = reverse('workspace:inventory_management_view')

    template = loader.get_template(str('workspace/mazer/categories_mgmt.html'))
    return HttpResponse(template.render(context, request))


@login_required(login_url='account:signin_view')
def orders_management_view(request):
    context = {}
    context["breadscrumb"] = "Đơn hàng"
    context["breadscrumb_url"] = reverse('workspace:orders_management_view')

    template = loader.get_template(str('workspace/mazer/orders_mgmt.html'))
    return HttpResponse(template.render(context, request))


@login_required(login_url='account:signin_view')
def users_management_view(request):
    context = {}
    context["breadscrumb"] = "Người dùng"
    context["breadscrumb_url"] = reverse('workspace:users_management_view')
    users = Account.objects.all()

    template = loader.get_template(str('workspace/mazer/users_mgmt.html'))
    return HttpResponse(template.render(context, request))

@login_required(login_url='account:signin_view')
def test_scss_view(request):
    context = {}
    context["breadscrumb"] = "Người dùng"
    context["breadscrumb_url"] = reverse('workspace:users_management_view')
    users = Account.objects.all()

    template = loader.get_template(str('workspace/mazer/test_scss.html'))
    return HttpResponse(template.render(context, request))
