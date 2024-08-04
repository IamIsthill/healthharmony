from django.urls import path
from healthharmony.doctor import views

urlpatterns = [
    path("", views.overview_view, name="doctor-overview"),
    path(
        "get-diagnosis/", views.get_predicted_diagnosis, name="doctor-predict-diagnosis"
    ),
]
