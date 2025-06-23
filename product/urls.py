from django.urls import reverse_lazy
from django.urls import path
from . import views
from . import api_views
from django.contrib.auth import views as auth_views

app_name = "product"
urlpatterns = [
    path('', views.shop_view, name='shop'),

    ### CATEGORY

    path('api/categories/user/', api_views.category_list_api_view, name='category_list_api_view'),
    path('api/categories/admin/', api_views.admin_category_list_api_view, name='admin_category_list_api_view'),
    path('api/categories/create/', api_views.create_category_api_view, name='create_category_api_view'),
    path('api/categories/<cat_uuid>/edit/', api_views.edit_category_api_view, name='edit_category_api_view'),
    path('api/categories/<cat_uuid>/delete/', api_views.delete_category_api_view, name='delete_category_api_view'),

    #### PRODUCT ####

    path('api/products/', api_views.product_list_api, name='product_list_api'),
    path('api/products/admin/', api_views.admin_product_list_api, name='admin_product_list_api'),
    path('api/filter-products/', api_views.filter_products_api, name='filter_products_api'),
    path('api/related-products/<uuid:uuid>/', api_views.related_product_list_api_view, name='related-products'),
    path('search/', views.product_search_view, name='product_search_view'),
    path('api/best-seller-products/', api_views.best_seller_products_api_view, name='best_seller_products_api'),
    path('shop-detail/<uuid:uuid>/', views.shop_detail_view, name='shop_detail'),
    path('api/detail/<uuid:uuid>/', api_views.product_detail, name='product_detail'),

    #### FEEDBACK ####

    path('feedback/', views.feedback_view, name='feedback_view'),
    path('api/feedback/create/', api_views.create_feedback_api_view, name='create_feedback'),

]

