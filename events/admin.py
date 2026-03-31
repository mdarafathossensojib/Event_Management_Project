from django.contrib import admin
from events.models import Event, Category, EventParticipant, Schedule, Speaker

# Register your models here.

admin.site.register(Event)
admin.site.register(Category)
admin.site.register(Speaker)
admin.site.register(Schedule)
admin.site.register(EventParticipant)
