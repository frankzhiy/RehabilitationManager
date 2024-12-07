from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_medication_record, name='upload_medication_record'),
    path('get/', views.get_medication_records, name='get_medication_records'),
    path('patientDetails/', views.get_medication_details, name='get_medication_details'),
]
