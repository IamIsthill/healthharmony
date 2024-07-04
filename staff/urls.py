from django.urls import path
from . import views

urlpatterns = [
    path('add-patient/', views.add_patient, name='add-patient'),
    path('', views.overview, name='staff-overview')
]
