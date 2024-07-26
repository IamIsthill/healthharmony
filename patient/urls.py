from django.urls import path
from patient import views

urlpatterns = [
    path('', views.overview_view, name='patient-overview'),
    path('records/', views.records_view, name='patient-records'),
    path('patient-profile/<int:pk>/', views.patient_view, name='patient-profile'),
]
