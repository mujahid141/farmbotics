from rest_framework import serializers
from .models import Profile,CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'address', 'bio', 'phone_number']
