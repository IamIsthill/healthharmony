from django.urls import path
from . import views

urlpatterns = [
    path("add-patient/", views.add_patient, name="add-patient"),
    path("issue/add/", views.create_patient_add_issue, name="create-patient-add-issue"),
    path("", views.overview, name="staff-overview"),
    path("inventory/", views.inventory, name="staff-inventory"),
    path("inventory/add/", views.add_inventory, name="staff-inventory-add"),
    path(
        "inventory/update/<int:pk>/",
        views.update_inventory,
        name="staff-inventory-update",
    ),
    path(
        "inventory/delete/<int:pk>/",
        views.delete_inventory,
        name="staff-inventory-delete",
    ),
    path("bed/", views.bed, name="staff-bed"),
    path("bed/update/<int:pk>/", views.bed_handler, name="staff-bed-handler"),
    path("records/", views.records, name="staff-records"),
    path("patient-and-accounts/", views.patients_and_accounts, name="staff-accounts"),
]
