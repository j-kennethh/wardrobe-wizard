from django import forms
from . import models
from taggit.forms import TagWidget
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe


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
                    "class": "mb-3",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "col-6 mb-3 col-6",
                }
            ),
            "tags": TagWidget(
                attrs={
                    "placeholder": "Enter tags, separated by commas",
                    "class": "tags",
                    "class": "col-6 col-md-4 mb-3",
                }
            ),  # enables comma-separated tag input
        }
        labels = {
            "image": "Take picture (against a solid colour background)",  # change the label of the image field
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        # handle cases where no image is uploaded (empty string or None)
        if not image or image == "":
            return None

        # only proceed with validation if an actual file was uploaded
        elif hasattr(image, "size"):  # Check if it's a file object
            # File size validation (5MB limit)
            max_size = 5 * 1024 * 1024  # 5MB
            if image.size > max_size:
                raise forms.ValidationError(
                    f"File size too large. Maximum size is {filesizeformat(max_size)}. "
                    f"Your file is {filesizeformat(image.size)}"
                )
            return image

        else:
            return image
