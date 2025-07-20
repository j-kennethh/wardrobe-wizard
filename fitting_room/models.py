import base64
from django.db import models
from django.conf import settings
from closet.models import ClothingItem
from django.core.files.base import ContentFile
import uuid
import os
from PIL import Image, ImageOps
from io import BytesIO


class Look(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="looks/", blank=True)
    items = models.ManyToManyField(ClothingItem, through="LookItem")

    def __str__(self):
        return f"{self.user.username}'s Look: {self.title}"

    def save(self, *args, **kwargs):
        # If this is a new look
        if not self.pk:
            # Check if there's screenshot data, if not put None
            screenshot_data = kwargs.pop("screenshot_data", None)

            if screenshot_data:
                self.create_from_screenshot(screenshot_data)  # process the image
            else:
                self.create_blank_canvas()  # create a white image

        super().save(*args, **kwargs)

    def create_from_screenshot(self, screenshot_data):
        # Extract the base64 image data
        format, imgstr = screenshot_data.split(";base64,")
        ext = format.split("/")[-1]

        # Create a ContentFile from the base64 data
        decoded_image = base64.b64decode(imgstr)  # decode the image
        self.image.save(
            f"look_{uuid.uuid4()}.png", ContentFile(decoded_image), save=False
        )

    # might be redundant as ill just save the blank grey canvas
    def create_blank_canvas(self):
        # Blank white canvas for the look
        img = Image.new("RGB", (800, 600), color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        self.image.save(
            f"blank_look_{uuid.uuid4()}.png", ContentFile(buffer.getvalue()), save=False
        )

    def apply_transformations(image, scale, rotation):
        """Apply scale and rotation to an image"""
        # Scale the image
        if scale != 1.0:
            new_size = (int(image.width * scale), int(image.height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Rotate the image (with transparent background)
        if rotation != 0:
            image = image.rotate(
                rotation,
                expand=True,
                resample=Image.Resampling.BICUBIC,
                fillcolor=(0, 0, 0, 0),
            )

        return image


class LookItem(models.Model):
    look = models.ForeignKey(Look, on_delete=models.CASCADE)
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    rotation = models.IntegerField(default=0)
    scale = models.FloatField(default=1.0)
    z_index = models.IntegerField(default=0)

    class Meta:
        ordering = ["z_index"]

    def __str__(self):
        return f"{self.clothing_item.title} in {self.look.title}"
