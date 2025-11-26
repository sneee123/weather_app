# api/urls.py
from django.urls import path
from .views import current_weather_view

urlpatterns = [
    path("weather", current_weather_view, name="api-weather"),
]
