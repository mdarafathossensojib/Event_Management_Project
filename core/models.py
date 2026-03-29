from django.db import models

# Create your models here.

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    company = models.CharField(max_length=100)

    image = models.ImageField(upload_to='testimonials/')
    content = models.TextField()
    rating = models.IntegerField(default=5)

    def __str__(self):
        return self.name

class SiteStats(models.Model):
    events_count = models.IntegerField(default=0)
    users_count = models.IntegerField(default=0)
    cities_count = models.IntegerField(default=0)
    satisfaction_rate = models.IntegerField(default=0)