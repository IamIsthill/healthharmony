from django.urls import path
from . import views

urlpatterns = [
    path("add-patient/", views.add_patient, name="add-patient"),
    path("post_add_patient/", views.post_add_patient, name="post_add_patient"),
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
    path(
        "bed/post_delete_bed/<int:pk>/", views.post_delete_bed, name="post_delete_bed"
    ),
    path("records/", views.records, name="staff-records"),
    path("patient-and-accounts/", views.patients_and_accounts, name="staff-accounts"),
    path(
        "patient-and-accounts/add-department/",
        views.add_department,
        name="staff-accounts-add-department",
    ),
    path(
        "patient-and-accounts/delete-department/<int:pk>/",
        views.delete_department,
        name="staff-accounts-delete-department",
    ),
    path(
        "patient-and-accounts/edit-department/<int:pk>/",
        views.edit_department,
        name="staff-accounts-edit-department",
    ),
]
