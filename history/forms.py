from django import forms
from .models import OutfitHistory


class OutfitHistoryForm(forms.ModelForm):
    class Meta:
        model = OutfitHistory
        fields = ["look", "date", "notes"]
        widgets = {
            "look": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }
