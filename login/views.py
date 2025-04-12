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

@csrf_exempt
def get_patient_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            phone = data.get('phone')
            id_card = data.get('id_card')
            doctor = data.get('doctor')

            if not all([name, phone, id_card, doctor]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            # 查询 PatientDiscomfortRecord 和 PatientDiscomfortRecordWarn
            discomfort_record = PatientDiscomfortRecord.objects.filter(
                name=name, phone=phone, id_card=id_card, doctor=doctor
            ).order_by('-datetime').first()
            discomfort_warn = PatientDiscomfortRecordWarn.objects.filter(
                name=name, phone=phone, id_card=id_card, doctor=doctor
            ).order_by('-datetime').first()

            discomfort_time = None
            alert_type = None
            if discomfort_record and discomfort_warn:
                if discomfort_record.datetime > discomfort_warn.datetime:
                    discomfort_time = discomfort_record.datetime
                    alert_type = None  # discomfort_record 没有 alert_type 字段
                else:
                    discomfort_time = discomfort_warn.datetime
                    alert_type = discomfort_warn.alert_type
            elif discomfort_record:
                discomfort_time = discomfort_record.datetime
                alert_type = None  # discomfort_record 没有 alert_type 字段
            elif discomfort_warn:
                discomfort_time = discomfort_warn.datetime
                alert_type = discomfort_warn.alert_type

            # 查询 PEFAssessment
            pef_assessment = PEFAssessment.objects.filter(
                name=name, phone=phone, id_card=id_card, doctor=doctor
            ).order_by('-PEFUploadTime').first()
            pef = pef_assessment.PEF if pef_assessment else None
            pef_upload_time = pef_assessment.PEFUploadTime if pef_assessment else None

            # 查询 PatientMedicationRecord
            medication_record = PatientMedicationRecord.objects.filter(
                name=name, phone=phone, id_card=id_card, doctor=doctor
            ).order_by('-medicinesFullDateTime').first()
            medicines_name = medication_record.medicinesName if medication_record else None
            medicines_full_date_time = medication_record.medicinesFullDateTime if medication_record else None

            # 查询问卷记录
            questionnaire_count = 0
            if PatientADL.objects.filter(name=name, phone=phone, id_card=id_card, doctor=doctor).exists():
                questionnaire_count += 1
            if PatientCAT.objects.filter(name=name, phone=phone, id_card=id_card, doctor=doctor).exists():
                questionnaire_count += 1
            if PatientmMRC.objects.filter(name=name, phone=phone, id_card=id_card, doctor=doctor).exists():
                questionnaire_count += 1
            if PatientCCQ.objects.filter(name=name, phone=phone, id_card=id_card, doctor=doctor).exists():
                questionnaire_count += 1

            # 返回数据
            response_data = {
                'discomfort_time': discomfort_time,
                'alert_type': alert_type,
                'pef': pef,
                'pef_upload_time': pef_upload_time,
                'medicines_name': medicines_name,
                'medicines_full_date_time': medicines_full_date_time,
                'questionnaire_count': questionnaire_count,
            }
            return JsonResponse({'status': 'success', 'data': response_data})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)