from django import forms
from . import models
from closet.models import ClothingItem


class LookForm(forms.ModelForm):
    class Meta:
        model = models.Look
        fields = ["title", "image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.HiddenInput(),
        }


# Selection of items to place in VFR with checkbox functionality
class ClothingItemSelectionForm(forms.ModelForm):
    items = forms.ModelMultipleChoiceField(
        queryset=ClothingItem.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["items"].queryset = ClothingItem.objects.filter(user=user)
