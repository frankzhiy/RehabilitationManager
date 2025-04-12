from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('get_patient_data/', views.get_patient_data, name='get_patient_data'),
]