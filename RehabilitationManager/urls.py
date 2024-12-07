"""RehabilitationManager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
import logging
from logsystem.models import LogEntry
urlpatterns = [
    path("admin/", admin.site.urls),
    path("COPD/", include("COPD.urls")),
    path("login/", include("login.urls")),
    path('registration/', include('registration.urls')),
    path('medication/', include('medication.urls')),
    path('discomfort/', include('discomfort.urls')),
    path('pef_records/', include('pef_records.urls')),
    path('patient_query/', include('patient_query.urls')),
    path('questionnaire/', include('questionnaire.urls')),
    path('assessment/', include('assessment.urls')),
    path('prescription/', include('prescription.urls')),
    path('patientWarn/', include('patientWarn.urls')),
    path('followUp/', include('followUp.urls')),
    path('statisticsAndFeedback/', include('statisticsAndFeedback.urls')),
]


# Get custom logger
logger = logging.getLogger('custom_logger')

def log_info(message):
    logger.info(message)

def log_warning(message):
    logger.warning(message)

def log_error(message):
    logger.error(message)

def log_debug(message):
    logger.debug(message)

def log_to_db(level, message):
    LogEntry.objects.create(level=level, message=message)
