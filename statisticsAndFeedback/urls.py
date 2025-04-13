# statisticsAndFeedback/urls.py
from django.urls import path
from .views import get_statistics, get_warn_statistics

urlpatterns = [
    path('get_statistics/', get_statistics, name='get_statistics'),
    path('get_warn_statistics/', get_warn_statistics, name='get_warn_statistics'),
]