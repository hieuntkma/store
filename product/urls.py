from django.urls import reverse_lazy
from django.urls import path
from . import views
from . import api_views
from django.contrib.auth import views as auth_views

app_name = "product"
urlpatterns = [
    path('', views.shop_view, name='shop'),
    path('api/products/', api_views.product_list_api, name='product_list_api'),
    path('api/categories/', api_views.category_list_api_view, name='category_list_api_view'),
    path('api/filter-products/', api_views.filter_products_api, name='filter_products_api'),
    path('api/related-products/<uuid:uuid>/', api_views.related_product_list_api_view, name='related-products'),
    path('search/', views.product_search_view, name='product_search_view'),
    path('api/best-seller-products/', api_views.best_seller_products_api_view, name='best_seller_products_api'),
    path('shop-detail/<uuid:uuid>/', views.shop_detail_view, name='shop_detail'),
    path('api/detail/<uuid:uuid>/', api_views.product_detail, name='product_detail'),
    path('feedback/', views.feedback_view, name='feedback_view'),
    path('api/feedback/create/', api_views.create_feedback_api_view, name='create_feedback'),

]
