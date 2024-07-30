from django.urls import path, include
from healthharmony.base import views

urlpatterns = [
    path("", views.home, name="home"),
    path("", include('healthharmony.users.urls')),
    path("staff/", include('healthharmony.staff.urls')),
    path("doctor/", include('healthharmony.doctor.urls')),
    path("patient/", include('healthharmony.patient.urls')),
    path("api/",include('healthharmony.api.urls')),
    path("administrator/", include('healthharmony.administrator.urls')),
]