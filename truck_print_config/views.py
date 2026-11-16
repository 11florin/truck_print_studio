from django.contrib import messages
from django.shortcuts import redirect, render


def page_not_found(request, exception):
    """Return visitors to the catalogue when a requested page is missing."""
    if request.resolver_match is not None:
        return render(request, "404.html", status=404)

    messages.info(
        request,
        "That page is not available. You have been returned to the shop.",
    )
    return redirect("shop:home")
