# discomfort/urls.py

from django.urls import path
from .views import upload_discomfort_record, get_discomfort_records, get_discomfort_records_by_doctor

urlpatterns = [
    path('upload/', upload_discomfort_record, name='upload_discomfort_record'),
    path('get/', get_discomfort_records, name='get_discomfort_records'),
    path('get_by_doctor/', get_discomfort_records_by_doctor, name='get_discomfort_records_by_doctor'),
]
