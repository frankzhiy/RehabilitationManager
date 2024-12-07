from django.urls import path
from . import views

urlpatterns = [
    path('create_followup/', views.create_followup, name='create_followup'),
    path('get_active_followups/', views.get_active_followups, name='get_active_followups'),
    path('deactivate_followup/', views.deactivate_followup, name='deactivate_followup'),
    path('ended_followup/', views.ended_followup, name='ended_followup'),
]