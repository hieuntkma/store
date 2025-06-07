from django.urls import reverse_lazy
from django.urls import path
from . import views
from . import api_views
from django.contrib.auth import views as auth_views

app_name = "cart"
urlpatterns = [
    ########### VIEW ##############
    path('', views.cart_detail_view, name='cart_detail_view'),

    ########### API VIEW ############
    path('api/cart-items/', api_views.cart_item_list_api_view, name='cart_item_list_api_view'),
    path('api/add-cart-items/', api_views.create_cart_item_api_view, name='create_cart_item_api_view'),
    path('api/update-cart-item/', api_views.update_cart_item_api_view, name='update_cart_item_api_view'),

    path('api/remove-cart-item/', api_views.remove_cart_item_by_product_uuid_api_view,
         name='remove_cart_item_by_product_uuid_api_view'),
]
