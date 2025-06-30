from django.urls import reverse_lazy
from django.urls import path
from . import views
from . import api_views
from django.contrib.auth import views as auth_views

app_name = "order"
urlpatterns = [
    ############### VIEW URLS #################
    path('create-order/', views.create_order_view, name='create_order_view'),

    ############### API URLS #################
    path('api/cart/preview/', views.preview_cart_api_view, name='preview_cart_api_view'),

    path('api/v1/create-order/', api_views.create_order_api_view, name='create_order_api_view'),
    path('api/v1/get-orders/', api_views.get_user_orders_api_view, name='get_user_orders_api_view'),
    path('api/v1/get-orders-detail/<uuid:uuid>/', api_views.get_order_detail_api_view,
         name='get_order_detail_api_view'),
    path('api/v1/cancel/<uuid:order_uuid>/', api_views.cancel_order_api_view, name='cancel_order_api_view'),
    # Admin
    path('api/v1/orders/admin/', api_views.admin_order_list_api_view, name='admin_order_list_api_view'),
    path('api/v1/orders/admin/<uuid>/detail/', api_views.admin_order_detail_api_view, name='admin_order_list_api_view'),
    path('api/v1/orders/admin/<uuid>/update-status/', api_views.admin_order_update_status_api_view, name='admin_order_update_status_api_view'),
    path('api/v1/orders/admin/stats', api_views.admin_order_stats_api_view, name='admin_order_stats_api_view'),
]
