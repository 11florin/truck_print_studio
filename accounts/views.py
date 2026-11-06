""" Views for account creation and authentication. """

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def register(request):
    """ Display the account form and authenticate the user upon success. """
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            login(request, form.save())
            return redirect("shop:home")
        else:
            form = UserCreationForm()

        return render(request, "accounts/register.html", {
            "form": form
            })
