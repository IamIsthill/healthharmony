from django.urls import path
from healthharmony.doctor import views

urlpatterns = [
    path("", views.overview_view, name="doctor-overview"),
    path("handled-cases/", views.handled_cases, name="doctor-handled-cases"),
    path("schedule/", views.schedule, name="doctor-schedule"),
    path(
        "schedule/post_update_doctor_time/",
        views.post_update_doctor_time,
        name="post_update_doctor_time",
    ),
    path(
        "schedule/post_update_doctor_avail/",
        views.post_update_doctor_avail,
        name="post_update_doctor_avail",
    ),
    path("patient/<int:pk>/", views.view_patient_profile, name="doctor-view-patient"),
    path(
        "get-diagnosis/", views.get_predicted_diagnosis, name="doctor-predict-diagnosis"
    ),
    path("get_illness_categories/", views.get_illness_categories),
    path("get_inventory_list/", views.get_inventory_list),
    path(
        "patient/post_update_user_details/",
        views.post_update_user_details,
        name="post_update_user_details",
    ),
]
