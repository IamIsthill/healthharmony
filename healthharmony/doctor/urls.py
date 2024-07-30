from django.urls import path
from healthharmony.doctor import views

urlpatterns = [
    path('', views.overview_view, name='doctor-overview'),
]
