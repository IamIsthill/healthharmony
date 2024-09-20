from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin-overview"),
    path("log-and-records/", views.log_and_records, name="admin-logs"),
    path("accounts/", views.account_view, name="admin-accounts"),
    path(
        "accounts/post_update_user_access/",
        views.post_update_user_access,
        name="post_update_user_access",
    ),
    path("accounts/post_delete_user/", views.post_delete_user, name="post_delete_user"),
]
