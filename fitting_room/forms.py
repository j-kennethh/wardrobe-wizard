from django import forms
from .models import Look
from closet.models import ClothingItem

class LookForm(forms.ModelForm):
    class Meta:
        model = Look
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ClothingItemSelectionForm(forms.Form):
    items = forms.ModelMultipleChoiceField(
        queryset=ClothingItem.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['items'].queryset = ClothingItem.objects.filter(user=user)
