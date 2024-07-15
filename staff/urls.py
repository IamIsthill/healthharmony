from django.urls import path
from . import views

urlpatterns = [
    path('add-patient/', views.add_patient, name='add-patient'),
    path('issue/add/', views.add_issue, name='add-issue'),
    path('', views.overview, name='staff-overview'),
    path('inventory/', views.inventory, name='staff-inventory'),
    path('bed/', views.bed, name="staff-bed" ),
    path('bed/update/<int:pk>/', views.bed_handler, name="staff-bed-handler" ),
    path('records/', views.records, name="staff-records" ),
]
