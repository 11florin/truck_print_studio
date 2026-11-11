""" Routes for checkout and order confirmation. """
from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("history/", views.order_history, name="history"),
    path("detail/<int:order_id>/", views.order_detail, name="detail"),
    path("success/<int:order_id>/", views.success, name="success"),
]