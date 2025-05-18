
# Create your models here.
from django.db import models
from users.models import CustomUser as User


class LeafDiseasePrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaf_predictions')
    image = models.ImageField(upload_to='leaf_disease_images/')
    predicted_class = models.CharField(max_length=255)
    confidence = models.FloatField()
    description = models.TextField()
    care = models.TextField()
    treatment = models.TextField()
    recommended_pesticides_or_fungicides = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.predicted_class} ({self.created_at})"
