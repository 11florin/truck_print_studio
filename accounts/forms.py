from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    """Create an account with an email address for notifications."""

    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            if field_name == "username":
                field.widget.attrs["autocomplete"] = "username"
            elif field_name in ("password1", "password2"):
                field.widget.attrs["autocomplete"] = "new-password"

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
