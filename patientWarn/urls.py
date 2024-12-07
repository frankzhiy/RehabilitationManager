from django.urls import path
from .views import patient_warn_view, deactivate_warn_records, get_patient_warn_records

urlpatterns = [
    path('patient_warn/', patient_warn_view, name='patient_warn'),
    path('deactivate_warn/', deactivate_warn_records, name='deactivate_warn'),
    path('get_patient_warn_records/', get_patient_warn_records, name='get_patient_warn_records')
]
