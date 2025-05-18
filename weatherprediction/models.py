from django.db import models
from users.models import CustomUser as User

class ChatbotInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    question = models.TextField()
    matched_question = models.TextField(blank=True, null=True)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat from {self.user or 'Anonymous'} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class WeatherData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    location_name = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)

    temperature_c = models.FloatField()
    condition_text = models.CharField(max_length=100)
    icon_url = models.URLField()

    cloud = models.IntegerField()
    humidity = models.IntegerField()
    wind_kph = models.FloatField()
    wind_dir = models.CharField(max_length=10)
    pressure_mb = models.FloatField()
    feelslike_c = models.FloatField()

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.location_name} - {self.date}"
