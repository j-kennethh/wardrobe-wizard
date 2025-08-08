import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Look
from .forms import LookForm, ClothingItemSelectionForm
from closet.models import ClothingItem
from django.core.files.base import ContentFile
import json
from PIL import Image, ImageDraw
import uuid
import os
from io import BytesIO
from taggit.models import Tag


@login_required
def fitting_room(request):
    if request.method == "POST":
        form = LookForm(request.POST, request.FILES)
        if form.is_valid():
            look = form.save(commit=False)
            look.user = request.user

            # Handle screenshot
            screenshot_data = request.POST.get("screenshot_data", "")
            if screenshot_data:
                look.save(screenshot_data=screenshot_data)
            else:
                look.save()
            return redirect("fitting_room:lookbook")
    else:
        form = LookForm()

    # Renders all clothing items in the selection modal

    tag = request.GET.get("tag")
    tags = Tag.objects.all()
    if tag:
        clothing_items = ClothingItem.objects.filter(
            user=request.user, tags__name=tag
        ).order_by("-date")
    else:
        clothing_items = ClothingItem.objects.filter(user=request.user).order_by(
            "-date"
        )

    return render(
        request,
        "fitting_room/fitting_room.html",
        {
            "form": form,
            "clothing_items": clothing_items,
            "user": request.user,
            "selected_tag": tag,
            "tags": tags,
        },
    )


@login_required
def lookbook(request):
    looks = Look.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "fitting_room/lookbook.html", {"looks": looks})


@login_required
def delete_look(request, look_id):
    look = get_object_or_404(Look, id=look_id, user=request.user)
    if request.method == "POST":
        look.image.delete()
        look.delete()
        return redirect("fitting_room:lookbook")
    return redirect("fitting_room:lookbook")
