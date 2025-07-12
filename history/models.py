from django.db import models
from django.conf import settings

# Create your models here.
class OutfitHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    look = models.ForeignKey('fitting_room.Look', on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True) # optional remarks

    class Meta:
        unique_together = ('user', 'date') # prevent duplicate logs in one day
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} wore '{self.look.title}' on {self.date}"
