from django.urls import path
from . import views

urlpatterns = [
    path('create_or_update/', views.create_or_update_prescription, name='create_or_update_prescription'),
    path('get_prescription/', views.get_prescription, name='get_prescription'),
    path('recommend_assessments/', views.recommend_assessments, name='recommend_assessments'),
    path('save_motion_prescription/', views.save_motion_prescription, name='save_motion_prescription'),
]
