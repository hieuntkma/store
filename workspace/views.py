from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required(login_url='account:signin_view')
def index(request):
    context = {}

    template = loader.get_template(str('workspace/mantis/workspace.html'))
    return HttpResponse(template.render(context, request))


def hello(request):
    context = {}

    template = loader.get_template(str('workspace/mantis/workspace.html'))
    # return HttpResponse(template.render(context, request))
    return HttpResponse("Hello guy!!!")
