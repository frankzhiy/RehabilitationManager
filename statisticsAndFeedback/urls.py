# statisticsAndFeedback/urls.py
from django.urls import path
from .views import get_statistics, get_warn_statistics, get_patient_data, get_userprofile_stats

urlpatterns = [
    path('get_statistics/', get_statistics, name='get_statistics'),
    path('get_warn_statistics/', get_warn_statistics, name='get_warn_statistics'),
    path('get_patient_data/', get_patient_data, name='get_patient_data'),
    path('get_userprofile_stats/', get_userprofile_stats, name='get_userprofile_stats'),
]