from django.db import models
from users.models import CustomUser as User

class SoilPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.TextField(null=True, blank=True)  # Save actual image file
    phosphorus = models.FloatField()
    ph = models.FloatField()
    organic_matter = models.FloatField()
    electrical_conductivity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Soil prediction for {self.user or 'Anonymous'} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
