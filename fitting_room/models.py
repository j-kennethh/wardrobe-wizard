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
    image = models.ImageField(upload_to='looks/')
    items = models.ManyToManyField(ClothingItem, through='LookItem')
    
    def __str__(self):
        return f"{self.user.username}'s Look: {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.image:
            # Create a blank image if this is a new look
            if not self.image:
                self.create_blank_canvas()
            
            super().save(*args, **kwargs)
            
            # Composite the image if items exist
            if self.lookitem_set.exists():
                self.composite_look_image()
                
    def create_blank_canvas(self):
        # Blank white canvas for the look
        img = Image.new('RGB', (800, 600), color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        self.image.save(f'blank_look_{uuid.uuid4()}.png', ContentFile(buffer.getvalue()), save=False)
    
    def composite_look_image(self):
        # Composite all ClothingItem onto the look image
        try:
            if self.image:
                with Image.open(self.image) as base_image:
                    base_image = base_image.convert("RGBA")
            else: 
                base_image = Image.new('RGBA', (800,600), (255, 255, 255, 255))

            #Process each item in the look
            for look_item in self.lookitem_set.all().order_by('z_index'):
                try:
                    with Image.open(look_item.clothing_item.image) as item_img:
                        # Convert to RGBA if not already
                        item_img = item_img.convert('RGBA')
                        
                        # Apply transformations
                        item_img = self.apply_transformations(
                            item_img,
                            look_item.scale,
                            look_item.rotation
                        )
                        
                        # Calculate position (centered)
                        x = look_item.position_x
                        y = look_item.position_y
                        
                        # Paste the item onto the base image
                        base_image.paste(item_img, (x, y), item_img)
                
                except Exception as e:
                    print(f"Error processing item {look_item.id}: {str(e)}")
                    continue
            
            # Save the composited image
            buffer = BytesIO()
            base_image.save(buffer, format='PNG', quality=95, optimize=True)
            self.image.save(f'look_{uuid.uuid4()}.png', ContentFile(buffer.getvalue()), save=False)
            self.save(update_fields=['image'])
                    
        except Exception as e:
            print(f"Error compositing look image: {str(e)}")
            # Fall back to blank image if composition fails
            self.create_blank_canvas()
            self.save(update_fields=['image'])
    
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
                fillcolor=(0, 0, 0, 0))
        
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
        ordering = ['z_index']
    
    def __str__(self):
        return f"{self.clothing_item.title} in {self.look.title}"
