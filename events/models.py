from django.db import models
from django.conf import settings
from django.utils import timezone

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
    about = models.TextField(blank=True, null=True)

    date = models.DateField()
    time = models.TimeField()

    location = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)  # Add address field
    is_virtual = models.BooleanField(default=False)
    tags = models.JSONField(blank=True, null=True)

    image = models.ImageField(upload_to='event_asset', default='event_asset/default_img.jpg')

    capacity = models.PositiveIntegerField(default=0)
    attendees = models.PositiveIntegerField(default=0, blank=True, null=True)
    registered = models.PositiveIntegerField(default=0, blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    @property
    def spots_left(self):
        """Calculate remaining spots"""
        registered_count = self.registered if self.registered else 0
        return max(0, self.capacity - registered_count)
    
    @property
    def percent_filled(self):
        """Calculate percentage filled"""
        if self.capacity == 0:
            return 0
        registered_count = self.registered if self.registered else 0
        return (registered_count / self.capacity) * 100
    
    @property
    def is_upcoming(self):
        """Check if event is upcoming"""
        event_datetime = timezone.datetime.combine(self.date, self.time)
        return event_datetime > timezone.now()


class Speaker(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='speakers',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='avatars', default='event_asset/default_img.jpg')
    bio = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)  # For ordering speakers

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Schedule(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='schedules',
        null=True,
        blank=True
    )
    time = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    day = models.IntegerField()
    location = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['day', 'order', 'time']

    def __str__(self):
        return f"Day {self.day}: {self.time} - {self.title}"


class EventParticipant(models.Model):
    STATUS_CHOICES = [
        ('going', 'Going'),
        ('interested', 'Interested'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_participants')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='going'
    )
    
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"


class SavedEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_events')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='saved_by_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.event.title}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('event_reminder', 'Event Reminder'),
        ('rsvp_confirmation', 'RSVP Confirmation'),
        ('event_update', 'Event Update'),
        ('new_follower', 'New Follower'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"


class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('rsvp', 'RSVP'),
        ('save', 'Save'),
        ('attend', 'Attend'),
        ('cancel', 'Cancel'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "User activities"
    
    def __str__(self):
        return f"{self.user.username} {self.activity_type} {self.event.title}"