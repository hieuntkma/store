from django.urls import reverse_lazy
from django.urls import path
from . import views
from . import api_views
from django.contrib.auth import views as auth_views

app_name = "portal"
urlpatterns = [
    path('', views.index, name='index'),
    path('about-us/', views.about_us_view, name='about_us_view'),
    path('contact-us/', views.contact_us_view, name='contact_us_view'),

    ### API VIEW ####
    path("api/category-tabs/", api_views.category_tab_with_products_api_view,
         name="category_tab_with_products_api_view"),
    path("api/vegetables/", api_views.vegetable_product_list_api_view, name="vegetable_product_list_api_view"),

]
