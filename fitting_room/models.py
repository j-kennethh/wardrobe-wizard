from django.db import models
from django.conf import settings
from closet.models import ClothingItem
from django.core.files.base import ContentFile
import uuid
import os
from PIL import Image
from io import BytesIO

class Look(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='looks/')
    items = models.ManyToManyField(ClothingItem, through='LookItem')
    
    def __str__(self):
        return f"{self.user.username}'s Look: {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.image:
            # Create a blank image if none is provided
            img = Image.new('RGB', (800, 600), color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            self.image.save(f'blank_look_{uuid.uuid4()}.png', ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)

class LookItem(models.Model):
    look = models.ForeignKey(Look, on_delete=models.CASCADE)
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    rotation = models.IntegerField(default=0)
    scale = models.FloatField(default=1.0)
    z_index = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['z_index']
    
    def __str__(self):
        return f"{self.clothing_item.title} in {self.look.title}"
