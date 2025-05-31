from django import forms
from . import models

class CreatePost(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ['title', 'category', 'slug', 'image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'capture': 'environment',
            }),
        }