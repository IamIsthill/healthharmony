from django.urls import path
from . import views

urlpatterns = [
    path('add-patient/', views.add_patient, name='add-patient'),
    path('issue/add/', views.add_issue, name='add-issue'),
    path('', views.overview, name='staff-overview')
]
