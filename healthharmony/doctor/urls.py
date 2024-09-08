from django.urls import path
from healthharmony.doctor import views

urlpatterns = [
    path("", views.overview_view, name="doctor-overview"),
    path("patient/<int:pk>/", views.view_patient_profile, name="doctor-view-patient"),
    path(
        "get-diagnosis/", views.get_predicted_diagnosis, name="doctor-predict-diagnosis"
    ),
    path("get_illness_categories/", views.get_illness_categories),
    path("get_inventory_list/", views.get_inventory_list),
]
