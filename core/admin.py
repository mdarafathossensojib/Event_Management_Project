from django.contrib import admin
from core.models import Newsletter, Testimonial, SiteStats

# Register your models here.

admin.site.register(Newsletter)
admin.site.register(Testimonial)
admin.site.register(SiteStats)