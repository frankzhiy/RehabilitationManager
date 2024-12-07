# statisticsAndFeedback/urls.py
from django.urls import path
from .views import get_statistics

urlpatterns = [
    path('get_statistics/', get_statistics, name='get_statistics'),
]