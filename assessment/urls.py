from django.urls import path
from setuptools.extern import names

from .views import (upload_respiratory_assessment,
                    upload_tce_assessment,
                    upload_step_assessment,
                    upload_swallow_assessment,
                    upload_limb_assessment,
                    upload_pef_assessment,
                    get_latest_swallow_status,
                    get_latest_respiratory_assessment,
                    get_latest_tce_assessment,
                    get_latest_step_assessment,
                    get_latest_limb_assessment,
                    get_latest_pef_assessment)

urlpatterns = [
    path('upload_respiratory_assessment/', upload_respiratory_assessment, name='upload_respiratory_assessment'),
    path('upload_tce_assessment/', upload_tce_assessment, name='upload_tce_assessment'),
    path('upload_step_assessment/', upload_step_assessment, name='upload_step_assessment'),
    path('upload_swallow_assessment/', upload_swallow_assessment, name='upload_swallow_assessment'),
    path('upload_limb_assessment/', upload_limb_assessment, name='upload_limb_assessment'),
    path('upload_pef_assessment/', upload_pef_assessment, name='upload_pef_assessment'),

    path('get_latest_swallow_status/', get_latest_swallow_status, name='get_latest_swallow_status'),
    path('get_latest_respiratory_status/', get_latest_respiratory_assessment, name='get_latest_respiratory_assessment'),
    path('get_latest_tce_status/', get_latest_tce_assessment, name='get_latest_tce_assessment'),
    path('get_latest_step_status/', get_latest_step_assessment, name='get_latest_step_assessment'),
    path('get_latest_limb_status/',get_latest_limb_assessment, name='get_latest_limb_assessment'),
    path('get_latest_pef_status/',get_latest_pef_assessment, name='get_latest_pef_assessment')


]
