from django.contrib import admin

from .models import WeatherHistory, User

# Register your models here.
admin.site.register(User)
admin.site.register(WeatherHistory)
