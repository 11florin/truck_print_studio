""" Views for the store's checkout flow. """

from django.shortcuts import render

# Create your views here.


def checkout(request):
    """ Build the order from the session cart and display the checkout. """
    return render(request, "orders/checkout.html", {
        "message": "Checkout-ul este în lucru."
    })