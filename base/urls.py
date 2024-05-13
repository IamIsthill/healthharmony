from django.urls import path, include
from . import views

urlpatterns = [
    # path("", include('base.urls'))
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("weather/", views.weather, name="weather"),
    path("api/",include('api.urls')),
]