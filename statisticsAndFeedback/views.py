from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from registration.models import UserProfile
from followUp.models import FollowUp
import json
from questionnaire.models import PatientADLWarn, PatientCATWarn, PatientmMRCWarn, PatientCCQWarn
from discomfort.models import PatientDiscomfortRecordWarn
from discomfort.models import PatientDiscomfortRecord, PatientDiscomfortRecordWarn
from assessment.models import PEFAssessment
from medication.models import PatientMedicationRecord
from questionnaire.models import PatientADL, PatientCAT, PatientmMRC, PatientCCQ
from pef_records.models import PatientPEFRecord, PatientBestPEFRecord  # 新增导入

@csrf_exempt
def get_statistics(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            doctor = data.get('doctor')

            if not doctor:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            # 查询 UserProfile 中同一个 doctor 的条目数
            user_profile_count = UserProfile.objects.filter(doctor=doctor).count()

            # 查询 FollowUp 中 followUpReason 为“常规随访”的数量
            regular_followup_count = FollowUp.objects.filter(doctor=doctor, followUpReason='常规随访').count()

            # 查询 FollowUp 中 followUpReason 为“预警随访”的数量
            warning_followup_count = FollowUp.objects.filter(doctor=doctor, followUpReason='预警随访').count()

            return JsonResponse({
                'status': 'success',
                'user_profile_count': user_profile_count,
                'regular_followup_count': regular_followup_count,
                'warning_followup_count': warning_followup_count
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_warn_statistics(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            doctor = data.get('doctor')
            followUpReason='常规随访'
            if not doctor:
                return JsonResponse({'status': 'error', 'message': 'Missing required field: doctor'}, status=400)

            # 使用 doctor 查询对应预警记录
            total_inactive_count = (
                PatientDiscomfortRecordWarn.objects.filter(doctor=doctor, finishedFollowup=True).count() +
                PatientADLWarn.objects.filter(doctor=doctor, finishedFollowup=True).count() +
                PatientCATWarn.objects.filter(doctor=doctor, finishedFollowup=True).count() +
                PatientmMRCWarn.objects.filter(doctor=doctor, finishedFollowup=True).count() +
                PatientCCQWarn.objects.filter(doctor=doctor, finishedFollowup=True).count()
            )

            followup_count = FollowUp.objects.filter(doctor=doctor, followUpReason=followUpReason).count()
            user_profile_count = UserProfile.objects.filter(doctor=doctor).count()
            return JsonResponse({
                'status': 'success',
                'total_inactive_count': total_inactive_count,
                'followup_count': followup_count,
                'user_profile_count': user_profile_count
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_patient_data(request):
    # 从 login/views.py 移动过来的函数
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            phone = data.get('phone')
            id_card = data.get('id_card')
            doctor = data.get('doctor')

            if not all([name, phone, id_card, doctor]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

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
                    alert_type = None
                else:
                    discomfort_time = discomfort_warn.datetime
                    alert_type = discomfort_warn.alert_type
            elif discomfort_record:
                discomfort_time = discomfort_record.datetime
            elif discomfort_warn:
                discomfort_time = discomfort_warn.datetime
                alert_type = discomfort_warn.alert_type

            # 修改PEF查询，使用PatientPEFRecord和PatientBestPEFRecord
            patient_pef_record = PatientPEFRecord.objects.filter(
                name=name, phone=phone, id_card=id_card, doctor=doctor
            ).order_by('-dateText').first()
            patient_best_pef_record = PatientBestPEFRecord.objects.filter(
                name=name, phone=phone, id_card=id_card, doctor=doctor
            ).order_by('-id').first()  # 修改排序条件，PatientBestPEFRecord没有dateText字段
            pef_value = patient_pef_record.pefValue if patient_pef_record else None
            pef_date = patient_pef_record.dateText if patient_pef_record else None
            best_pef_input = patient_best_pef_record.bestpefInput if patient_best_pef_record else None

            medication_record = PatientMedicationRecord.objects.filter(
                name=name, phone=phone, id_card=id_card, doctor=doctor
            ).order_by('-medicinesFullDateTime').first()
            medicines_name = medication_record.medicinesName if medication_record else None
            medicines_full_date_time = medication_record.medicinesFullDateTime if medication_record else None

            questionnaire_count = 0
            if PatientADL.objects.filter(name=name, phone=phone, id_card=id_card, doctor=doctor).exists():
                questionnaire_count += 1
            if PatientCAT.objects.filter(name=name, phone=phone, id_card=id_card, doctor=doctor).exists():
                questionnaire_count += 1
            if PatientmMRC.objects.filter(name=name, phone=phone, id_card=id_card, doctor=doctor).exists():
                questionnaire_count += 1
            if PatientCCQ.objects.filter(name=name, phone=phone, id_card=id_card, doctor=doctor).exists():
                questionnaire_count += 1

            response_data = {
                'discomfort_time': discomfort_time,
                'alert_type': alert_type,
                'pef_value': pef_value,
                'pef_date': pef_date,
                'best_pef_input': best_pef_input,
                'medicines_name': medicines_name,
                'medicines_full_date_time': medicines_full_date_time,
                'questionnaire_count': questionnaire_count,
            }
            return JsonResponse({'status': 'success', 'data': response_data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_userprofile_stats(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Missing required field: name'}, status=400)
            qs = UserProfile.objects.filter(doctor=name)
            total_count = qs.count()
            not_verified_count = qs.filter(is_verified=False).count()
            return JsonResponse({
                'status': 'success',
                'total_count': total_count,
                'not_verified_count': not_verified_count
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)