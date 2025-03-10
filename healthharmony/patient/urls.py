from django.urls import path
from healthharmony.patient import views

urlpatterns = [
    path("", views.overview_view, name="patient-overview"),
    path("records/<int:pk>/", views.records_view, name="patient-records"),
    path("patient-profile/<int:pk>/", views.patient_view, name="patient-profile"),
    path(
        "records/post_create_certificate_request/",
        views.post_create_certificate_request,
        name="post_create_certificate_request",
    ),
]
