from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import ClothingItem
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from . import forms
from taggit.models import Tag
# Create your views here.

@login_required
def clothing_items_list(request):
    tag = request.GET.get('tag')
    tags = Tag.objects.all()
    if tag:
        items = ClothingItem.objects.filter(user=request.user, tags__name=tag)
    else:
        items = ClothingItem.objects.filter(user=request.user)
    
    return render(request, 'closet/clothing_items_list.html', {'items': items, 'user': request.user, 'selected_tag': tag, 'tags': tags})


def clothing_item_page(request, pk):
    item = get_object_or_404(ClothingItem, pk=pk)
    return render(request, 'closet/clothing_item_page.html', {'item': item})

@login_required(login_url= "/users/login/")
def clothing_item_new(request):
    if request.method == "POST":
        form = forms.CreateClothingItem(request.POST, request.FILES)
        if form.is_valid():
            newpost = form.save(commit=False)
            newpost.user = request.user
            newpost.save()
            form.save_m2m() #to save tags as commit=False skips saving related many-to-many fields
            return redirect('closet:list')
            
    else:
        form = forms.CreateClothingItem()
    return render(request, 'closet/new_item.html', {'form': form})
    