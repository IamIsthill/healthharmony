from django.urls import path
from doctor import views

urlpatterns = [
    path('', views.overview_view, name='doctor-overview'),
]
