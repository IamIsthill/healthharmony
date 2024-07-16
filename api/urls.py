from django.urls import path, include
from . import views

urlpatterns = [
    path("data/", views.api_data, name="api-data"),
    path("staff/records/request-data/", views.certificate_sorter, name="staff-certificate-sorter"),
    path("staff/records/certificate-data/", views.certificate_data, name="staff-certificate-data"),
]