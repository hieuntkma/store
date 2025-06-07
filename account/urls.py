from django.urls import reverse_lazy
from django.urls import path
from . import views
from . import api_views
from django.contrib.auth import views as auth_views

app_name = "account"
urlpatterns = [
    # path('', views.index, name='index'),
    path('signin/', views.signin_view, name='signin_view'),
    path('sign-out/', views.sign_out_view, name='sign_out_view'),
    path('signup/', views.sign_up_view, name='signup_view'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password_view'),
    path('change-password/', views.change_password_view, name='change_password_view'),
    path('my-profile/', views.my_profile_view, name='my_profile_view'),
    path('profile-setting/', views.profile_setting_view, name='profile_setting_view'),
    path('my-order/', views.order_list_view, name='order_list_view'),

    ### Api View ###
    path('api/v1/signin/', api_views.signin_api_view, name='signin_api_view'),
    path('api/v1/signup/', api_views.signup_api_view, name='signup_api_view'),
]
