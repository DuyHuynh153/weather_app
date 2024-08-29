from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('save-weather/', views.save_weather_data, name='save_weather'),
    path('register_weather_info/', views.register_user, name='register_weather_info'),
    path("activate/<str:uidb64>/<str:token>/", views.activate, name="activate"),
    
    
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser , name = "logout"),
    
]
