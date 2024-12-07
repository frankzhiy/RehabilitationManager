from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

from registration.models import PatientFollowUp
from .models import FollowUp
from discomfort.models import PatientDiscomfortRecordWarn
from questionnaire.models import PatientADLWarn, PatientCATWarn, PatientmMRCWarn, PatientCCQWarn
import json

@csrf_exempt
def create_followup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            from_value = data.get('from')

            if from_value == 'warnlist':
                # Ensure fields are dictionaries
                patient_adl_warn = json.loads(data.get('PatientADLWarn', '{}'))
                patient_cat_warn = json.loads(data.get('PatientCATWarn', '{}'))
                patient_ccq_warn = json.loads(data.get('PatientCCQWarn', '{}'))
                patient_discomfort_record_warn = json.loads(data.get('PatientDiscomfortRecordWarn', '{}'))
                patient_mmrc_warn = json.loads(data.get('PatientmMRCWarn', '{}'))

                # Combine reasonDetail
                reason_detail = {}
                if patient_adl_warn:
                    reason_detail['barthel_index'] = patient_adl_warn.get('barthel_index')
                if patient_cat_warn:
                    reason_detail['cat_index'] = patient_cat_warn.get('cat_index')
                if patient_ccq_warn:
                    reason_detail['ccq_index'] = patient_ccq_warn.get('ccq_index')
                if patient_discomfort_record_warn:
                    reason_detail['alert_type'] = patient_discomfort_record_warn.get('alert_type')
                if patient_mmrc_warn:
                    reason_detail['mmrc_index'] = patient_mmrc_warn.get('mmrc_index')

                # Convert reasonDetail to JSON string, ensuring non-ASCII characters are not escaped
                reason_detail_str = json.dumps(reason_detail, ensure_ascii=False)

                # Create FollowUp record
                followup = FollowUp(
                    name=data.get('name'),
                    id_card=data.get('id_card'),
                    phone=data.get('phone'),
                    doctor=data.get('doctor'),
                    followUpEffectiveness=data.get('followUpEffectiveness'),
                    ineffectivenessReason=data.get('ineffectivenessReason'),
                    qualityOfLife=data.get('qualityOfLife'),
                    physicalCondition=data.get('physicalCondition'),
                    psychologicalCondition=data.get('psychologicalCondition'),
                    medicationAdherence=data.get('medicationAdherence'),
                    exacerbations=data.get('exacerbations'),
                    acuteExacerbations=data.get('acuteExacerbations'),
                    newDiscomfort=data.get('newDiscomfort'),
                    newSymptoms=data.get('newSymptoms'),
                    followUpReason='预警随访',
                    followUpTime=parse_datetime(data.get('followUpTime')),
                    reasonDetail=reason_detail_str
                )
                followup.save()

                # Update related warning records' finishedFollowup field
                patient_filter = {
                    'name': data.get('name'),
                    'phone': data.get('phone'),
                    'id_card': data.get('id_card'),
                    'doctor': data.get('doctor')
                }

                if patient_adl_warn:
                    upload_time = parse_datetime(patient_adl_warn.get('uploadTime'))
                    PatientADLWarn.objects.filter(uploadTime=upload_time, **patient_filter).update(finishedFollowup=True)

                if patient_cat_warn:
                    upload_time = parse_datetime(patient_cat_warn.get('uploadTime'))
                    PatientCATWarn.objects.filter(uploadTime=upload_time, **patient_filter).update(finishedFollowup=True)

                if patient_ccq_warn:
                    upload_time = parse_datetime(patient_ccq_warn.get('uploadTime'))
                    PatientCCQWarn.objects.filter(uploadTime=upload_time, **patient_filter).update(finishedFollowup=True)

                if patient_discomfort_record_warn:
                    datetime = parse_datetime(patient_discomfort_record_warn.get('datetime'))
                    PatientDiscomfortRecordWarn.objects.filter(datetime=datetime, **patient_filter).update(finishedFollowup=True)

                if patient_mmrc_warn:
                    upload_time = parse_datetime(patient_mmrc_warn.get('uploadTime'))
                    PatientmMRCWarn.objects.filter(uploadTime=upload_time, **patient_filter).update(finishedFollowup=True)

                return JsonResponse({'status': 'success', 'message': 'Follow-up created and warnings updated successfully'})

            elif from_value == 'follow':
                # Create FollowUp record with specific reasonDetail
                followup = FollowUp(
                    name=data.get('name'),
                    id_card=data.get('id_card'),
                    phone=data.get('phone'),
                    doctor=data.get('doctor'),
                    followUpEffectiveness=data.get('followUpEffectiveness'),
                    ineffectivenessReason=data.get('ineffectivenessReason'),
                    qualityOfLife=data.get('qualityOfLife'),
                    physicalCondition=data.get('physicalCondition'),
                    psychologicalCondition=data.get('psychologicalCondition'),
                    medicationAdherence=data.get('medicationAdherence'),
                    exacerbations=data.get('exacerbations'),
                    acuteExacerbations=data.get('acuteExacerbations'),
                    newDiscomfort=data.get('newDiscomfort'),
                    newSymptoms=data.get('newSymptoms'),
                    followUpReason='常规随访',
                    followUpTime=parse_datetime(data.get('followUpTime')),
                    reasonDetail='常规每两周进行的周期随访'
                )
                followup.save()

                # Count the number of '常规随访' entries
                followup_count = FollowUp.objects.filter(
                    name=data.get('name'),
                    phone=data.get('phone'),
                    id_card=data.get('id_card'),
                    doctor=data.get('doctor'),
                    followUpReason='常规随访'
                ).count()

                # Update the count in PatientFollowUp
                PatientFollowUp.objects.filter(
                    name=data.get('name'),
                    phone=data.get('phone'),
                    id_card=data.get('id_card'),
                    doctor=data.get('doctor')
                ).update(
                    followTimes=followup_count,
                    followUpType='常规随访',
                    followUpTime=timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                    isFinished=True
                )

                return JsonResponse({'status': 'success', 'message': 'Follow-up created successfully'})

            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid from value'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
# def create_followup(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#
#             # 确保字段是字典
#             patient_adl_warn = json.loads(data.get('PatientADLWarn', '{}'))
#             patient_cat_warn = json.loads(data.get('PatientCATWarn', '{}'))
#             patient_ccq_warn = json.loads(data.get('PatientCCQWarn', '{}'))
#             patient_discomfort_record_warn = json.loads(data.get('PatientDiscomfortRecordWarn', '{}'))
#             patient_mmrc_warn = json.loads(data.get('PatientmMRCWarn', '{}'))
#
#             # 组合 reasonDetail
#             reason_detail = {}
#             if patient_adl_warn:
#                 reason_detail['barthel_index'] = patient_adl_warn.get('barthel_index')
#             if patient_cat_warn:
#                 reason_detail['cat_index'] = patient_cat_warn.get('cat_index')
#             if patient_ccq_warn:
#                 reason_detail['ccq_index'] = patient_ccq_warn.get('ccq_index')
#             if patient_discomfort_record_warn:
#                 reason_detail['alert_type'] = patient_discomfort_record_warn.get('alert_type')
#             if patient_mmrc_warn:
#                 reason_detail['mmrc_index'] = patient_mmrc_warn.get('mmrc_index')
#
#             # 将 reasonDetail 转换为 JSON 字符串，确保不转义非 ASCII 字符
#             reason_detail_str = json.dumps(reason_detail, ensure_ascii=False)
#
#             # 创建 FollowUp 记录
#             followup = FollowUp(
#                 name=data.get('name'),
#                 id_card=data.get('id_card'),
#                 phone=data.get('phone'),
#                 doctor=data.get('doctor'),
#                 followUpEffectiveness=data.get('followUpEffectiveness'),
#                 ineffectivenessReason=data.get('ineffectivenessReason'),
#                 qualityOfLife=data.get('qualityOfLife'),
#                 physicalCondition=data.get('physicalCondition'),
#                 psychologicalCondition=data.get('psychologicalCondition'),
#                 medicationAdherence=data.get('medicationAdherence'),
#                 exacerbations=data.get('exacerbations'),
#                 acuteExacerbations=data.get('acuteExacerbations'),
#                 newDiscomfort=data.get('newDiscomfort'),
#                 newSymptoms=data.get('newSymptoms'),
#                 followUpReason=data.get('followUpReason'),
#                 followUpTime=parse_datetime(data.get('followUpTime')),
#                 reasonDetail=reason_detail_str
#             )
#             followup.save()
#
#             # 更新相关预警记录的 finishedFollowup 字段
#             patient_filter = {
#                 'name': data.get('name'),
#                 'phone': data.get('phone'),
#                 'id_card': data.get('id_card'),
#                 'doctor': data.get('doctor')
#             }
#
#             if patient_adl_warn:
#                 upload_time = parse_datetime(patient_adl_warn.get('uploadTime'))
#                 PatientADLWarn.objects.filter(uploadTime=upload_time, **patient_filter).update(finishedFollowup=True)
#
#             if patient_cat_warn:
#                 upload_time = parse_datetime(patient_cat_warn.get('uploadTime'))
#                 PatientCATWarn.objects.filter(uploadTime=upload_time, **patient_filter).update(finishedFollowup=True)
#
#             if patient_ccq_warn:
#                 upload_time = parse_datetime(patient_ccq_warn.get('uploadTime'))
#                 PatientCCQWarn.objects.filter(uploadTime=upload_time, **patient_filter).update(finishedFollowup=True)
#
#             if patient_discomfort_record_warn:
#                 datetime = parse_datetime(patient_discomfort_record_warn.get('datetime'))
#                 PatientDiscomfortRecordWarn.objects.filter(datetime=datetime, **patient_filter).update(finishedFollowup=True)
#
#             if patient_mmrc_warn:
#                 upload_time = parse_datetime(patient_mmrc_warn.get('uploadTime'))
#                 PatientmMRCWarn.objects.filter(uploadTime=upload_time, **patient_filter).update(finishedFollowup=True)
#
#             return JsonResponse({'status': 'success', 'message': 'Follow-up created and warnings updated successfully'})
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def get_active_followups(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            doctor = data.get('doctor')
            page = data.get('page', 1)
            page_size = data.get('page_size', 10)

            if not doctor:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            followups = PatientFollowUp.objects.filter(
                doctor=doctor,
                is_verified=True,
                isActive=True,
                isEnded=False,
                isFinished=False
            ).order_by('created_at')

            paginator = Paginator(followups, page_size)
            try:
                followups_page = paginator.page(page)
            except:
                return JsonResponse({'status': 'error', 'message': 'Invalid page number'}, status=400)

            followup_list = []
            for followup in followups_page:
                followup_list.append({
                    'name': followup.name,
                    'id_card': followup.id_card,
                    'phone': followup.phone,
                    'doctor': followup.doctor,
                    'sex': followup.sex,
                    'birth': followup.birth,
                    'height': followup.height,
                    'weight': followup.weight,
                    'waistline': followup.waistline,
                    'diseases': followup.diseases,
                    'created_at': followup.created_at,
                    'followUpTime': followup.followUpTime,
                    'followUpType': followup.followUpType,
                    'followTimes' : followup.followTimes

                })

            return JsonResponse({
                'status': 'success',
                'followups': followup_list,
                'total_pages': paginator.num_pages,
                'current_page': page,
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def deactivate_followup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            id_card = data.get('id_card')
            phone = data.get('phone')
            doctor = data.get('doctor')

            followup = PatientFollowUp.objects.filter(name=name, id_card=id_card, phone=phone, doctor=doctor).first()
            if followup:
                followup.isActive = False
                followup.deactivateTime = timezone.now()
                followup.save()
                return JsonResponse({'status': 'success', 'message': 'Follow-up deactivated successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Follow-up not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def ended_followup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            id_card = data.get('id_card')
            phone = data.get('phone')
            doctor = data.get('doctor')

            followup = PatientFollowUp.objects.filter(name=name, id_card=id_card, phone=phone, doctor=doctor).first()
            if followup:
                followup.isEnded = True
                followup.endedTime = timezone.now()
                followup.save()
                return JsonResponse({'status': 'success', 'message': 'Follow-up reactivated successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Follow-up not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)