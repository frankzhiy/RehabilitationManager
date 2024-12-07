from django.urls import path
from . import views

urlpatterns = [
    path('get_unverified_patients/', views.get_unverified_patients, name='get_unverified_patients'),
]