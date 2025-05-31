from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length = 75)
    category = models.TextField() #different from Charfield, relates to a text area form input
    slug = models.SlugField()
    date = models.DateTimeField(auto_now_add = True) #auto adds date and time
    image = models.ImageField(default='fallback.jpeg', blank = True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
# upload_to='media/',

    def __str__(self):
        return self.title


