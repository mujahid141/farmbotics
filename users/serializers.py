from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'address', 'location', 'bio', 'account_type']
        read_only_fields = ['user']  # Ensure the user is set automatically
