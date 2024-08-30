

import datetime
import logging
import os
import uuid
from django.contrib import messages
from time import timezone
from django.http import JsonResponse
from django.shortcuts import redirect, render
import requests
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .token import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth import  login, logout, authenticate
from django.urls import reverse

from .models import Subscription, WeatherHistory, User
from .forms import RegistrationForm, SubscriptionForm



def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        
        user = None
        # Check if user exists in database
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User does not exist!")
            
        # Authenticate using the username and password if user exists
        if user:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Email or password is incorrect Or account not activate yes. Please activate your account in email we sent youuu")

    context = {'page': page}
    return render(request, "registration/login.html", context)


def logoutUser(request):
    #  remove session ID from cookie to logout
    logout(request)
    return redirect("home")



def home(request):
    # API_KEY = open("API_KEY" , "r").read()
    API_KEY = settings.WEATHER_API_KEY

    # api key : b757b355213a46ca88e162857242708
    current_weather_url = "https://api.weatherapi.com/v1/current.json?key={}&q={}&aqi={}"
    forecast_url = "https://api.weatherapi.com/v1/forecast.json?key={}&q={}&days={}&aqi={}&alerts={}"
    
    messages_to_display = messages.get_messages(request)
    try:
        
        context = {}
        
        if request.method == "POST":
            if "city" in request.POST and request.POST["city"]:
                # Search by city name
                city = request.POST["city"]
                weather_data, daily_forecast = fetch_weather_and_forecast_data(city, API_KEY, current_weather_url, forecast_url)
            elif "lat" in request.POST and "lon" in request.POST:
                # Search by latitude and longitude (current location)
                lat = request.POST["lat"]
                lon = request.POST["lon"]
                location = f"{lat},{lon}"
                weather_data, daily_forecast = fetch_weather_and_forecast_data(location, API_KEY, current_weather_url, forecast_url)
            else:
                context["error"] = "Please enter a city or allow access to your location."
                return render(request, "weather_app/index.html", context)

            if weather_data:
                context = {
                    "weather_data": weather_data,
                    "daily_forecast": daily_forecast,
                    "messages": messages_to_display
                }
         # Fetch the latest saved weather data for the user if the request method is GET and the query parameter is present
        elif request.method == "GET":
            if request.user.is_authenticated and request.GET.get('latest_weather') == 'true':
                saved_weather_data_list = WeatherHistory.objects.filter(user=request.user).order_by('-weather_time')
                if saved_weather_data_list.exists():
                    context["weather_data_list"] = [
                        {
                            "city": weather_data.city,
                            "country": weather_data.country,
                            "temperature": weather_data.temperature,
                            "wind_kph": weather_data.wind_speed,
                            "humidity": weather_data.humidity,
                            "Date": weather_data.weather_time,
                            "icon": weather_data.icon,  # Add appropriate icon if available
                            "condition": weather_data.condition  # Add appropriate condition if available
                        }
                        for weather_data in saved_weather_data_list
                    ]
            elif request.GET.get('city'):
                city = request.GET.get('city')
                weather_data, daily_forecast = fetch_weather_and_forecast_data(city, API_KEY, current_weather_url, forecast_url)
                if weather_data:
                    context = {
                        "weather_data": weather_data,
                        "daily_forecast": daily_forecast,
                        "messages": messages_to_display
                    }
                
            
        return render(request, "weather_app/index.html", context)
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        context["error"] = "An error occurred while fetching weather data."
        return render(request, "weather_app/index.html", context)
    
    
    
def fetch_weather_and_forecast_data(city, api_key, current_weather_url, forecast_url):
    
    try:
        # Fetch current weather data
        response = requests.get(current_weather_url.format(api_key, city, "no"))
        response.raise_for_status()
        response_data = response.json()
        
        # Fetch forecast data
        forecast_response = requests.get(forecast_url.format(api_key, city, 5, "no", "no"))
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        weather_data = {
            "city": response_data["location"]["name"],
            "country": response_data["location"]["country"],
            "temperature": response_data["current"]["temp_c"],
            "condition": response_data["current"]["condition"]["text"],
            "icon": response_data["current"]["condition"]["icon"],
            "wind_kph": response_data["current"]["wind_kph"],
            "humidity": response_data["current"]["humidity"],
            "feels_like": response_data["current"]["feelslike_c"],
            "Date": response_data['current']['last_updated'],
        }
        
       

        
        daily_forecast = []
        first_entry = True  # Flag to track the first entry

        for day in forecast_data["forecast"]["forecastday"]:
            if first_entry:
                first_entry = False
                continue  # Skip the first entry
            
            forecast = {
                "date": day["date"],
                "temperature": day["day"]["avgtemp_c"],
                "wind_kph": day["day"]["maxwind_kph"],
                "condition": day["day"]["condition"]["text"],
                "humidity": day["day"]["avghumidity"],
                "icon": day["day"]["condition"]["icon"],
            }
            daily_forecast.append(forecast)
        
        return weather_data, daily_forecast
    
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        
        return None, None
    
   
def save_weather_data(request):
    if request.method == "POST":
        city = request.POST.get("city")
        country = request.POST.get("country")
        temperature = request.POST.get("temperature")
        wind_kph = request.POST.get("wind_kph")
        humidity = request.POST.get("humidity")
        weather_time = request.POST.get("weather_time")
        icon_file_name = request.POST.get("icon")
        condition = request.POST.get("condition")


        # Ensure that required data is present
        # Ensure that required data is present
        if city and country and temperature and request.user.is_authenticated:
            try:
                WeatherHistory.objects.create(
                    user = request.user,
                    city=city,
                    country=country,
                    temperature=float(temperature),
                    wind_speed=float(wind_kph),
                    humidity=int(humidity) ,
                    condition = condition,
                    icon = icon_file_name,
                    weather_time = weather_time
                )
                messages.success(request, "Weather data saved successfully!")
            except Exception as e:
                messages.error(request, f"Error saving weather data: {e}")
        else:
            messages.error(request, "Please Login to saving weather")
    return redirect("home")




def register_user(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = False
            user.save()
            
            current_site = get_current_site(request)
            mail_subject = "Activate your account"
            
            context = {
                "user":user,
                "domain":current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
                "protocol": "https" if settings.DEBUG else "http" 
            }
            message = render_to_string("registration/account_activation_email.html", context)
            to_email = form.cleaned_data["email"]
            email = EmailMessage(
                mail_subject, message,from_email=settings.DEFAULT_FROM_EMAIL, to =[to_email]
            )
            email.send()
            messages.success(request, "Please check you email to complete your registration")
            
            return redirect("home")
        
    return render(request,"registration/register.html", {"form":form})

               
def activate(request, uidb64, token):
    try:
        
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk = uid)
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and account_activation_token.check_token(user,  token):
        user.is_active = True
        user.save()
        
        # Automatically subscribe the user to daily weather information
        email = user.email
        token = str(uuid.uuid4())
        subscription, created = Subscription.objects.get_or_create(email=email)
        subscription.token = token
        subscription.confirmed = False
        subscription.save()
        
        messages.success(request,"you account successfully activated ! Now you can login")
        return  redirect ("home")
    else:
        messages.error(request,"Activation link not found")
        return redirect ("home")
        
    
def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            email = request.user.email
            
            try:
                subscription = Subscription.objects.get(email=email)
                subscription.confirmed = True
                subscription.city = city
                subscription.save()

                messages.success(request, "You have successfully subscribed to daily weather updates!")

            except Subscription.DoesNotExist:
                messages.error(request, "Subscription not found. Please activate your account first.")

            # return redirect("home")  # Redirect to the user's profile or dashboard
            return redirect(f"{reverse('home')}?city={city}")

    else:
        form = SubscriptionForm()
    return render(request, 'weather_app/subscribe.html', {'form': form})





# def register_user(request):
#     form = RegistrationForm()
#     if request.method == "POST":
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.username = user.username.lower()
#             user.is_active = True
#             user.save()
            
#             current_site = get_current_site(request)
#             mail_subject = "Activate your account"
            
#             context = {
#                 "user":user,
#                 "domain":current_site.domain,
#                 "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#                 "token": account_activation_token.make_token(user),
#                 "protocol": "https" if settings.DEBUG else "http" 
#             }
#             message = render_to_string("registration/account_activation_email.html", context)
#             to_email = form.cleaned_data["email"]
#             email = EmailMessage(
#                 mail_subject, message,from_email=settings.DEFAULT_FROM_EMAIL, to =[to_email]
#             )
#             email.send()
#             messages.success(request, "Please check you email to complete your registration")
            
#             return redirect("home")
        
#     return render(request,"registration/register.html", {"form":form})

               
# def activate(request, uidb64, token):
#     try:
        
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk = uid)
        
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None
        
#     if user is not None and account_activation_token.check_token(user,  token):
#         user.is_active = True
#         user.save()
        
#         messages.success(request,"you account successfully activated ! Now you can login")
#         return  redirect ("home")
#     else:
#         messages.error(request,"Activation link not found")
#         return redirect ("home")