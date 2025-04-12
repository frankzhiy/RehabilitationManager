from django.urls import path
from .views import upload_adl, upload_cat, upload_mmrc, upload_ccq, get_adl_by_doctor, get_cat_by_doctor, get_mmrc_by_doctor, get_ccq_by_doctor, get_scores_by_patient

urlpatterns = [
    path('upload_adl/', upload_adl, name='upload_adl'),
    path('upload_cat/', upload_cat, name='upload_cat'),
    path('upload_mmrc/', upload_mmrc, name='upload_mmrc'),
    path('upload_ccq/', upload_ccq, name='upload_ccq'),
    path('get_adl_by_doctor/', get_adl_by_doctor, name='get_adl_by_doctor'),
    path('get_cat_by_doctor/', get_cat_by_doctor, name='get_cat_by_doctor'),
    path('get_mmrc_by_doctor/', get_mmrc_by_doctor, name='get_mmrc_by_doctor'),
    path('get_ccq_by_doctor/', get_ccq_by_doctor, name='get_ccq_by_doctor'),
    path('get_scores_by_patient/', get_scores_by_patient, name='get_scores_by_patient'),
]