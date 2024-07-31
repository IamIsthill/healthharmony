from django.urls import path, include
from . import views

urlpatterns = [
    path("data/", views.api_data, name="api-data"),
    path(
        "staff/records/request-data/",
        views.certificate_sorter,
        name="staff-certificate-sorter",
    ),
    path(
        "staff/records/certificate-data/",
        views.certificate_data,
        name="staff-certificate-data",
    ),
    path("administrator/user-data/", views.user_data, name="admin-user-data"),
    path(
        "administrator/account-role-data/",
        views.account_roles,
        name="admin-account-role-data",
    ),
    path(
        "administrator/user-demographics-data/",
        views.user_demographics,
        name="admin-user-demographics-data",
    ),
    path(
        "administrator/accounts/account-list-data/",
        views.filtered_account_list,
        name="admin-account-list-data",
    ),
    path("session-email/", views.get_session_email, name="session-email"),
    path("patient/visit-data/", views.get_visit_data, name="patient-visit-data"),
    path(
        "patient/treatment-data/",
        views.get_user_illness_count,
        name="patient-treatment-data",
    ),
]
