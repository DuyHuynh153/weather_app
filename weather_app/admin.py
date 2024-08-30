from django.contrib import admin

from .models import WeatherHistory, User, Subscription

# Register your models here.
admin.site.register(User)
admin.site.register(WeatherHistory)
admin.site.register(Subscription)