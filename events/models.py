from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # frontend icon mapping

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')

    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')

    description = models.TextField()

    date = models.DateField()
    time = models.TimeField()

    location = models.CharField(max_length=255)
    is_virtual = models.BooleanField(default=False)

    image = models.ImageField(upload_to='event_asset', default='event_asset/default_img.jpg')

    capacity = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class EventParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')

    status = models.CharField(
        max_length=20,
        choices=[
            ('going', 'Going'),
            ('interested', 'Interested'),
        ],
        default='going'
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
    