""" Views for account creation and authentication. """

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def register(request):
    """Display the account form and authenticate the user upon success."""
    if request.user.is_authenticated:
        return redirect("shop:home")
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop:home')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
    })


@login_required
def profile(request):
    """Display the authenticated user's account page."""
    return render(request, 'accounts/profile.html')
