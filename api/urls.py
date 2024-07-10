from django.urls import path, include
from . import views

urlpatterns = [
    path("data/", views.api_data, name="api-data")
]