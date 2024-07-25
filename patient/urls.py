from django.urls import path
from patient import views

urlpatterns = [
    path('', views.overview_view, name='patient-home'),
    path('records/', views.records_view, name='patient-records'),
]
