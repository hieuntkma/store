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

    # template = loader.get_template(str('workspace/mazer/workspace.html'))
    template = loader.get_template(str('workspace/mazer/workspace.html'))
    return HttpResponse(template.render(context, request))

@login_required(login_url='account:signin_view')
def products_management_view(request):
    context = {}
    context["breadscrumb"] = "Sản phẩm"
    context["breadscrumb_url"] = reverse('workspace:products_management_view')
    template = loader.get_template(str('workspace/mazer/categories_mgmt.html'))
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

    template = loader.get_template(str('workspace/mazer/categories_mgmt.html'))
    return HttpResponse(template.render(context, request))

@login_required(login_url='account:signin_view')
def users_management_view(request):
    context = {}
    context["breadscrumb"] = "Người dùng"
    context["breadscrumb_url"] = reverse('workspace:users_management_view')

    template = loader.get_template(str('workspace/mazer/categories_mgmt.html'))
    return HttpResponse(template.render(context, request))
