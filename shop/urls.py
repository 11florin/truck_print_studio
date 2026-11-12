""" Storefront routes: home, catalog, categories, product, and cart. """

from django.urls import path
from . import views


app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path('products/', views.product_list, name='list'),
    path('categories/<slug:slug>/', views.category_detail, name='category'),
    path('products/<slug:slug>/', views.product_detail, name='detail'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart, name='cart'),
]