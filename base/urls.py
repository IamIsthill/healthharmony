from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("", include('users.urls')),
    path("staff/", include('staff.urls')),
    path("weather/", views.weather, name="weather"),
    path("api/",include('api.urls')),
    path("administrator/", include('administrator.urls')),
    path("accounts/", include("allauth.urls")),
]