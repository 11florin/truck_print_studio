from django.shortcuts import render


# Create your views here.
# def _cart(request):
#     """ Returns the session cart, initializing it if it is missing. """
#     pass


def home(request):
    """ Displays the homepage with active and featured products. """
    return render(request, "shop/base.html")


def product_list(request):
    """ Display the catalog and apply the filters from the query string. """
    return render(request, "shop/list.html")


def cart(request):
    """ Convert the identifiers from the session into displayable products and totals."""
    return render(request, "shop/cart.html")