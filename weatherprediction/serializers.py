from .models import WeatherData
from rest_framework import serializers


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'
        read_only_fields = ['user', 'date']  # Assuming 'timestamp' is auto-generated