from django import forms


class CheckoutForm(forms.Form):
    """Verify your contact and delivery details before placing the order."""

    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )
    full_name = forms.CharField(
        max_length=160,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your full name",
            "autocomplete": "name",
        }),
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Street address and house number",
            "rows": 3,
            "autocomplete": "street-address",
        }),
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "City",
            "autocomplete": "address-level2",
        }),
    )
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. SW1A 1AA",
            "autocomplete": "postal-code",
        }),
    )

    def clean_full_name(self):
        return self.cleaned_data["full_name"].strip()

    def clean_address(self):
        return self.cleaned_data["address"].strip()

    def clean_city(self):
        return self.cleaned_data["city"].strip()

    def clean_postal_code(self):
        return self.cleaned_data["postal_code"].strip()
