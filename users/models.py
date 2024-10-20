from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    
    
