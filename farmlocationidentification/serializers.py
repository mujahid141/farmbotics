from rest_framework import serializers
from .models import FarmReport

class FarmReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmReport
        fields = '__all__'
        read_only_fields = ['id','user']
