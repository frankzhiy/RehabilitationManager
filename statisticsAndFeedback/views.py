from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from registration.models import UserProfile
from followUp.models import FollowUp
import json
from questionnaire.models import PatientADLWarn, PatientCATWarn, PatientmMRCWarn, PatientCCQWarn
from discomfort.models import PatientDiscomfortRecordWarn

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