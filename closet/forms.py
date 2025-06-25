from django import forms
from . import models
from taggit.forms import TagWidget

# using form manually for more flexibility, instead of using Django Admin
class CreateClothingItem(forms.ModelForm):
    class Meta:
        model = models.ClothingItem
        fields = [ 'image', 'title', 'tags']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'capture': 'environment',
            }),
            'tags': TagWidget(attrs={
                'placeholder': 'Enter tags, separated by commas'
            }), #enables comma-separated tag input
        } # the widgets allows us to create ClothingItem objects from images captured
        