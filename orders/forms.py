from django import forms


class CheckoutForm(forms.Form):
    """Verify your contact and delivery details before placing the order."""

    email = forms.EmailField(max_length=254)
    full_name = forms.CharField(max_length=160)
    address = forms.CharField(widget=forms.Textarea)
    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)

    def clean_full_name(self):
        return self.cleaned_data["full_name"].strip()

    def clean_address(self):
        return self.cleaned_data["address"].strip()

    def clean_city(self):
        return self.cleaned_data["city"].strip()

    def clean_postal_code(self):
        return self.cleaned_data["postal_code"].strip()