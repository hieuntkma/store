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
from product.models import *

# Create your views here.

def index(request):
    context = {}
    # context['categories'] = Categories.objects.all()
    template = loader.get_template(str('portal/fruitable/portal.html'))
    return HttpResponse(template.render(context, request))

def about_us_view(request):
    context = {}
    context['breadcrumb_title'] = 'Giới thiệu'
    template = loader.get_template(str('portal/fruitable/about-us.html'))
    return HttpResponse(template.render(context, request))

def contact_us_view(request):
    context = {}
    context['breadcrumb_title'] = 'Liên hệ'
    template = loader.get_template(str('portal/fruitable/contact-us.html'))
    return HttpResponse(template.render(context, request))
