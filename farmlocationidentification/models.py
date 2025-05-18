from django.db import models

# Create your models here.

from users.models import CustomUser as User 
from django.db import models

class FarmReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_at = models.DateTimeField()
    coordinates = models.JSONField()  # Store array of coordinates (e.g., polygon)
    estimated_area = models.CharField(max_length=20)  # or use FloatField if numerical
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return f"Farm Report of {self.user.username} at {self.selected_at.strftime('%Y-%m-%d %H:%M')}"
