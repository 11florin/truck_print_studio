from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Validate and present a product review."""

    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.Select(
                choices=[(rating, f"{rating} / 5") for rating in range(1, 6)],
                attrs={"class": "form-select"},
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Share your experience with this product.",
                },
            ),
        }
