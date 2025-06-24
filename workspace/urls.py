from django.urls import reverse_lazy
from django.urls import path
from . import views
from . import api_views
from django.contrib.auth import views as auth_views

app_name = "workspace"
urlpatterns = [
    #### Index management ####
    path('mgmt/dashboard/', views.admin_index_view, name='admin_index_view'),

    #### Category management ####
    path('mgmt/categories/', views.categories_management_view, name='categories_management_view'),

    #### Product management ####
    path('mgmt/products/', views.products_management_view, name='products_management_view'),
    path('mgmt/products/create/', views.create_products_management_view, name='create_products_management_view'),
    path('mgmt/products/<product_uuid>/edit/', views.edit_products_management_view, name='edit_products_management_view'),
    path('mgmt/inventory/', views.inventory_management_view, name='inventory_management_view'),

    #### Order management ####
    path('mgmt/orders/', views.orders_management_view, name='orders_management_view'),

    #### User management ####
    path('mgmt/users/', views.users_management_view, name='users_management_view'),
]
