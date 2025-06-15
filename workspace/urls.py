from django.urls import reverse_lazy
from django.urls import path
from . import views
from . import api_views
from django.contrib.auth import views as auth_views

app_name = "workspace"
urlpatterns = [
    path('', views.index, name='index'),
    path('hello/', views.hello, name='hello'),
]
