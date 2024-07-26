from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name="admin-overview"),
    path('log-and-records/', views.log_and_records, name="admin-logs"),
    path('accounts/', views.account_view, name="admin-accounts"),
]
