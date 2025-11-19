from django.db import models
from django.contrib.auth.models import User, Group, Permission

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    asset = models.ImageField(upload_to='event_asset', blank=True, null=True, default='event_asset/default_img.jpg')
    user = models.ManyToManyField(User, related_name='user')

    def __str__(self):
        return self.name
    

