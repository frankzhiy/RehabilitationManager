from django.http import HttpResponse, JsonResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
from discomfort.models import PatientDiscomfortRecord, PatientDiscomfortRecordWarn
from assessment.models import PEFAssessment
from medication.models import PatientMedicationRecord
from questionnaire.models import PatientADL, PatientCAT, PatientmMRC, PatientCCQ
import json

@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = User.objects.filter(username=username, password=password)
    if user:
        return HttpResponse('Success')
    else:
        return HttpResponse('Error')