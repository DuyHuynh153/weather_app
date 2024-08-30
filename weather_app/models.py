from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True ,null = True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email
    
    
class WeatherHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    temperature = models.FloatField( null=True)
    wind_speed = models.FloatField( null=True)
    humidity = models.IntegerField( null=True)
    icon = models.CharField( null=True)
    condition = models.CharField( null=True)
    weather_time = models.DateTimeField(null=True)  # Use this for the weather time
    
    def __str__(self):
        return str(self.city)
    

class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}, {self.country}"
    
class Subscription(models.Model):
    email = models.EmailField(unique=True, null=True)
    token = models.CharField(max_length=100, unique=True)
    confirmed = models.BooleanField(default=False)
    city = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.email



