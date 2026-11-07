""" Storefront routes: home, catalog, categories, product, and cart. """

from django.urls import path
from . import views


app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path('products/', views.product_list, name='list'),
    path('categories/<slug:slug>/', views.category_detail, name='category'),
    path('products/<slug:slug>/', views.product_detail, name='detail'),
    path('cart/', views.cart, name='cart'),
]