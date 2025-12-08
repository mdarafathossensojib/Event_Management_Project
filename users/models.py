from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images', blank=True, default='profile_images/default.jpg')
    cover_image = models.ImageField(upload_to='cover_images', blank=True, default='cover_images/default.jpg')
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.username} Profile'