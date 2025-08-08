from django import forms
from . import models
from taggit.forms import TagWidget
from django.template.defaultfilters import filesizeformat


# using form manually for more flexibility, instead of using Django Admin
class CreateClothingItem(forms.ModelForm):
    class Meta:
        model = models.ClothingItem
        fields = ["image", "title", "tags"]
        widgets = {
            "image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                    "capture": "environment",  # allows camera capture
                }
            ),
            "tags": TagWidget(
                attrs={"placeholder": "Enter tags, separated by commas"}
            ),  # enables comma-separated tag input
        }  # the widgets allows us to create ClothingItem objects from images captured

    def clean_image(self):
        image = self.cleaned_data.get("image", False)
        if image:
            # Only add file size validation (5MB limit)
            max_size = 5 * 1024 * 1024  # 5MB
            if image.size > max_size:
                raise forms.ValidationError(
                    f"File size too large. Maximum size is {filesizeformat(max_size)}. "
                    f"Your file is {filesizeformat(image.size)}"
                )
        return image
