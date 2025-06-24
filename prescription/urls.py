from django.urls import path
from . import views

urlpatterns = [
    path('create_or_update/', views.create_or_update_prescription, name='create_or_update_prescription'),
    path('get_prescription/', views.get_prescription, name='get_prescription'),
    path('recommend_assessments/', views.recommend_assessments, name='recommend_assessments'),
    path('save_motion_prescription/', views.save_motion_prescription, name='save_motion_prescription'),
    path('get_motion_prescriptions/', views.get_motion_prescriptions, name='get_motion_prescription'),
    path('get_motion_prescriptions_with_urls/', views.get_motion_prescriptions_with_urls, name='get_motion_prescriptions_with_urls'),
    path('save_exercise_record/', views.save_exercise_record, name='save_exercise_record'),
    path('get_exercise_record/', views.get_exercise_record, name='get_exercise_record'),
    path('generate_audio_sequence/', views.generate_audio_sequence, name='generate_audio_sequence'),
    path('get_audio_task_status/', views.get_audio_task_status, name='get_audio_task_status'),
    path('download_audio_result/', views.download_audio_result, name='download_audio_result'),
]
