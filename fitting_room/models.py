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

    # creates and saves a blank white canvas is screenshot or setting of Look.image fails
    def create_blank_canvas(self):
        # Blank white canvas for the look
        img = Image.new("RGB", (800, 600), color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        self.image.save(
            f"blank_look_{uuid.uuid4()}.png", ContentFile(buffer.getvalue()), save=False
        )
