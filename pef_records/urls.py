from django.urls import path
from . import views

urlpatterns = [
    path('upload_pef_record/', views.upload_pef_record, name='upload_pef_record'),
    path('upload_best_pef_record/', views.upload_best_pef_record, name='upload_best_pef_record'),
    path('get_best_pef_records/', views.get_best_pef_records, name='get_best_pef_records'),
    path('get_pef_records/', views.get_pef_records, name='get_pef_records'),
    path('get_pef_records_by_doctor/', views.get_patient_records, name='get_pef_records_by_doctor'),
]