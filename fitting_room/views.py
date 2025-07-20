import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Look, LookItem
from .forms import LookForm, ClothingItemSelectionForm
from closet.models import ClothingItem
from django.core.files.base import ContentFile
import json
from PIL import Image, ImageDraw
import uuid
import os
from io import BytesIO

"""
@login_required
def fitting_room(request):
    if request.method == "POST":
        form = LookForm(request.POST, request.FILES)
        if form.is_valid():
            look = form.save(commit=False)
            look.user = request.user

            # Get the canvas data from the request
            canvas_data = json.loads(request.POST.get("canvas_data", "{}"))

            # first save the blank image
            look.save()

            # Create a blank image for the look
            img = Image.new("RGB", (800, 600), color="white")
            draw = ImageDraw.Draw(img)

            # For now just save the blank image, we'll implement compositing later
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            look.image.save(f"look_{uuid.uuid4()}.png", ContentFile(buffer.getvalue()))
            look.save()

            # Save the items to the look
            for item_data in canvas_data.get("items", []):
                try:
                    clothing_item = ClothingItem.objects.get(
                        id=item_data["id"], user=request.user
                    )
                    LookItem.objects.create(
                        look=look,
                        clothing_item=clothing_item,
                        position_x=item_data["x"],
                        position_y=item_data["y"],
                        rotation=item_data["rotation"],
                        scale=item_data["scale"],
                        z_index=item_data["zIndex"],
                    )
                except ClothingItem.DoesNotExist:
                    continue

            # # the look.save() method will handle the image composition automatically
            return redirect("fitting_room:lookbook")
    else:
        form = LookForm()

    # Get all user's clothing items for the selection modal
    clothing_items = ClothingItem.objects.filter(user=request.user)
    selection_form = ClothingItemSelectionForm(user=request.user)

    return render(
        request,
        "fitting_room/fitting_room.html",
        {
            "form": form,
            "clothing_items": clothing_items,
            "selection_form": selection_form,
        },
    )
"""


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
    clothing_items = ClothingItem.objects.filter(user=request.user)

    return render(
        request,
        "fitting_room/fitting_room.html",
        {
            "form": form,
            "clothing_items": clothing_items,
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
        look.delete()
        return redirect("fitting_room:lookbook")
    return redirect("fitting_room:lookbook")


def test(request):
    return render(request, "fitting_room/test.html")
