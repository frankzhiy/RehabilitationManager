from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator

from registration.models import PatientPrescription
from django.views.decorators.csrf import csrf_exempt
import json
import io
import requests
from datetime import datetime, timedelta
from pydub import AudioSegment
from .models import MotionPrescription, MotionList, ExerciseRecord
from .services import get_recommendations,build_audio_url_sequence
from django.views import View
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
@csrf_exempt
def create_or_update_prescription(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # 获取医生和患者的标识信息
        doctor = data.get('doctor')
        id_card = data.get('id_card')
        name = data.get('name')
        phone = data.get('phone')

        if not all([doctor, id_card, name, phone]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        # 获取或创建记录
        prescription, created = PatientPrescription.objects.get_or_create(
            doctor=doctor,
            id_card=id_card,
            name=name,
            phone=phone
        )

        # 更新非空字段
        updated_fields = {}
        for field in ['swallowStatusPrescription', 'MepAndMipPrescription', 'limbStatus', 'PEFPrescription',
                      'TCEPrescription', 'MwtAndStepPrescription']:
            if field in data and data[field]:
                updated_fields[field] = data[field]

        # 更新并保存上传时间
        if updated_fields:
            for field, value in updated_fields.items():
                setattr(prescription, field, value)
            prescription.uploadtime = datetime.now()
            prescription.save()
            return JsonResponse({'message': '处方以添加' if not created else '处方记录创建失败'}, status=200)

        return JsonResponse({'error': '没有更新的字段'}, status=400)

    return JsonResponse({'error': '无效的请求方法'}, status=405)


@csrf_exempt
def get_prescription(request):
    if request.method == 'GET':
        doctor = request.GET.get('doctor')


        if not doctor:
            return JsonResponse({'status': 'error', 'message': '必须提供完整的医生信息才可获取患者列表'})

        try:
            prescription = PatientPrescription.objects.filter(doctor=doctor, is_verified=True)

            if not prescription:
                return JsonResponse({'status': 'success', 'message': '未找到患者处方记录'})

            # 将记录转换为字典
            data = list(prescription.values(
                'doctor', 'id_card', 'name', 'phone', 'swallowStatusPrescription','sex',
                'MepAndMipPrescription', 'limbStatusPrescription', 'PEFPrescription',
                'TCEPrescription', 'MwtAndStepPrescription', 'uploadtime', 'isActive', 'is_verified'
            ))
            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求方法'})


@csrf_exempt
def recommend_assessments(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request
            assessments = json.loads(request.body)
            # Get recommendations based on the assessments
            recommendations = get_recommendations(assessments)
            return JsonResponse({'status': 'success', 'recommendations': recommendations})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



# @csrf_exempt
# def save_prescription(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         name = data.get('name')
#         id_card = data.get('id_card')
#         phone = data.get('phone')
#         doctor = data.get('doctor')
#         is_confirmed = data.get('is_confirmed', False)
#
#         existing_prescription = MotionPrescription.objects.filter(
#             name=name, id_card=id_card, phone=phone, doctor=doctor
#         ).first()
#
#         if existing_prescription and not is_confirmed:
#             return JsonResponse({
#                 'message': '该患者已经存在运动处方，'
#             })
#
#         is_active = data.get('is_active', True) if is_confirmed else False
#
#         prescription = MotionPrescription(
#             name=name,
#             id_card=id_card,
#             phone=phone,
#             doctor=doctor,
#             limbPrescription=data.get('limbPrescription', []),
#             pefPrescription=data.get('pefPrescription', []),
#             respiratoryPrescription=data.get('respiratoryPrescription', []),
#             swallowPrescription=data.get('swallowPrescription', []),
#             tcePrescription=data.get('tcePrescription', []),
#             upload_time=data.get('upload_time'),
#             is_active=is_active
#         )
#         prescription.save()
#
#         return JsonResponse({'message': 'Prescription saved successfully.'})
#
#     return JsonResponse({'error': 'Invalid request method.'}, status=400)


@csrf_exempt
def save_motion_prescription(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            id_card = data.get('id_card')
            phone = data.get('phone')
            doctor = data.get('doctor')

            # Deactivate existing prescriptions with the same name, id_card, phone, doctor
            MotionPrescription.objects.filter(
                name=name, id_card=id_card, phone=phone, doctor=doctor, is_active=True
            ).update(is_active=False)

            # Save new prescription
            prescription = MotionPrescription(
                name=name,
                id_card=id_card,
                phone=phone,
                doctor=doctor,
                limbPrescription=data.get('limbPrescription', []),
                pefPrescription=data.get('pefPrescription', []),
                respiratoryPrescription=data.get('respiratoryPrescription', []),
                swallowPrescription=data.get('swallowPrescription', []),
                tcePrescription=data.get('tcePrescription', []),
                upload_time=data.get('upload_time'),
                is_active=True
            )
            prescription.save()

            # Update corresponding PatientPrescription
            patient_prescription = PatientPrescription.objects.filter(
                name=name, id_card=id_card, phone=phone, doctor=doctor
            ).first()

            if patient_prescription:
                patient_prescription.limbStatusPrescription = data.get('limbPrescription', [])
                patient_prescription.PEFPrescription = data.get('pefPrescription', [])
                patient_prescription.MepAndMipPrescription = data.get('respiratoryPrescription', [])
                patient_prescription.swallowStatusPrescription = data.get('swallowPrescription', [])
                patient_prescription.TCEPrescription = data.get('tcePrescription', [])
                patient_prescription.save()
            else:
                return JsonResponse({'error': 'PatientPrescription not found'}, status=404)

            return JsonResponse({'message': 'Prescription saved and updated successfully.'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def get_motion_prescriptions(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')

        if not all([name, id_card, phone, doctor]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        prescriptions = MotionPrescription.objects.filter(
            name=name, id_card=id_card, phone=phone, doctor=doctor
        ).order_by('-upload_time')

        if not prescriptions.exists():
            return JsonResponse({'error': '未找到符合条件的处方记录'}, status=404)

        latest_prescription = prescriptions.first()
        other_prescriptions = prescriptions[1:]

        latest_data = {
            'name': latest_prescription.name,
            'id_card': latest_prescription.id_card,
            'phone': latest_prescription.phone,
            'doctor': latest_prescription.doctor,
            'limbPrescription': latest_prescription.limbPrescription,
            'pefPrescription': latest_prescription.pefPrescription,
            'respiratoryPrescription': latest_prescription.respiratoryPrescription,
            'swallowPrescription': latest_prescription.swallowPrescription,
            'tcePrescription': latest_prescription.tcePrescription,
            'upload_time': latest_prescription.upload_time,
            'is_active': latest_prescription.is_active,
        }

        other_data = list(other_prescriptions.values(
            'name', 'id_card', 'phone', 'doctor', 'limbPrescription', 'pefPrescription','sex',
            'respiratoryPrescription', 'swallowPrescription', 'tcePrescription', 'upload_time', 'is_active'
        ))

        return JsonResponse({
            'latest_prescription': latest_data,
            'other_prescriptions': other_data
        })

    return JsonResponse({'error': '无效的请求方法'}, status=405)


def get_motion_prescriptions_with_urls(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')

        if not all([name, id_card, phone, doctor]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        prescriptions = MotionPrescription.objects.filter(
            name=name, id_card=id_card, phone=phone, doctor=doctor
        ).order_by('-upload_time')

        if not prescriptions.exists():
            return JsonResponse({'error': '未找到符合条件的处方记录'}, status=404)

        latest_prescription = prescriptions.first()
        other_prescriptions = prescriptions[1:]

        def add_urls_to_prescription(prescription):
            for field in ['tcePrescription', 'swallowPrescription', 'respiratoryPrescription', 'pefPrescription', 'limbPrescription']:
                if field in prescription:
                    for item in prescription[field]:
                        motion = MotionList.objects.filter(name=item['name']).first()
                        if motion:
                            item['url'] = motion.urls
                            item['purpose'] = motion.purpose
                            item['details'] = motion.details

            return prescription

        latest_data = {
            'name': latest_prescription.name,
            'id_card': latest_prescription.id_card,
            'phone': latest_prescription.phone,
            'doctor': latest_prescription.doctor,
            'limbPrescription': latest_prescription.limbPrescription,
            'pefPrescription': latest_prescription.pefPrescription,
            'respiratoryPrescription': latest_prescription.respiratoryPrescription,
            'swallowPrescription': latest_prescription.swallowPrescription,
            'tcePrescription': latest_prescription.tcePrescription,
            'upload_time': latest_prescription.upload_time,
            'is_active': latest_prescription.is_active,
        }

        other_data = list(other_prescriptions.values(
            'name', 'id_card', 'phone', 'doctor', 'limbPrescription', 'pefPrescription',
            'respiratoryPrescription', 'swallowPrescription', 'tcePrescription', 'upload_time', 'is_active'
        ))

        urls_data = add_urls_to_prescription({
            'limbPrescription': latest_prescription.limbPrescription,
            'pefPrescription': latest_prescription.pefPrescription,
            'respiratoryPrescription': latest_prescription.respiratoryPrescription,
            'swallowPrescription': latest_prescription.swallowPrescription,
            'tcePrescription': latest_prescription.tcePrescription,
        })

        # 提取duration为null的元素
        def extract_null_duration_elements(prescription):
            null_duration_elements = []
            for field in ['limbPrescription', 'pefPrescription', 'respiratoryPrescription', 'swallowPrescription', 'tcePrescription']:
                if field in prescription:
                    for item in prescription[field]:
                        if item.get('duration') is None:
                            null_duration_elements.append(item)
            return null_duration_elements

        null_duration_elements = extract_null_duration_elements(latest_data)

        # 组合成一个序列
        sequence = []
        for element in null_duration_elements:
            motion = MotionList.objects.filter(name=element['name']).first()
            if motion:
                sequence.append({
                    'name': motion.name,
                    'weekly_training_count': motion.weekly_training_count,
                    'daily_training_count': motion.daily_training_count,
                    'reps_per_set': motion.reps_per_set,
                    'sets_per_session': motion.sets_per_session
                })

        return JsonResponse({
            'latest_prescription': latest_data,
            'other_prescriptions': other_data,
            'urls_data': urls_data,
            'motion_sequence': sequence
        })

    return JsonResponse({'error': '无效的请求方法'}, status=405)
# @csrf_exempt
# def get_motion_prescriptions_with_urls(request):
#     if request.method == 'GET':
#         name = request.GET.get('name')
#         id_card = request.GET.get('id_card')
#         phone = request.GET.get('phone')
#         doctor = request.GET.get('doctor')
#
#         if not all([name, id_card, phone, doctor]):
#             return JsonResponse({'error': '缺少必填字段'}, status=400)
#
#         prescriptions = MotionPrescription.objects.filter(
#             name=name, id_card=id_card, phone=phone, doctor=doctor
#         ).order_by('-upload_time')
#
#         if not prescriptions.exists():
#             return JsonResponse({'error': '未找到符合条件的处方记录'}, status=404)
#
#         latest_prescription = prescriptions.first()
#         other_prescriptions = prescriptions[1:]
#
#         def add_urls_to_prescription(prescription):
#             for field in ['tcePrescription', 'swallowPrescription', 'respiratoryPrescription', 'pefPrescription', 'limbPrescription']:
#                 if field in prescription:
#                     for item in prescription[field]:
#                         motion = MotionList.objects.filter(name=item['name']).first()
#                         if motion:
#                             item['url'] = motion.urls
#                             item['purpose'] = motion.purpose
#                             item['details'] = motion.details
#
#             return prescription
#
#         latest_data = {
#             'name': latest_prescription.name,
#             'id_card': latest_prescription.id_card,
#             'phone': latest_prescription.phone,
#             'doctor': latest_prescription.doctor,
#             'limbPrescription': latest_prescription.limbPrescription,
#             'pefPrescription': latest_prescription.pefPrescription,
#             'respiratoryPrescription': latest_prescription.respiratoryPrescription,
#             'swallowPrescription': latest_prescription.swallowPrescription,
#             'tcePrescription': latest_prescription.tcePrescription,
#             'upload_time': latest_prescription.upload_time,
#             'is_active': latest_prescription.is_active,
#         }
#
#         other_data = list(other_prescriptions.values(
#             'name', 'id_card', 'phone', 'doctor', 'limbPrescription', 'pefPrescription',
#             'respiratoryPrescription', 'swallowPrescription', 'tcePrescription', 'upload_time', 'is_active'
#         ))
#
#         urls_data = add_urls_to_prescription({
#             'limbPrescription': latest_prescription.limbPrescription,
#             'pefPrescription': latest_prescription.pefPrescription,
#             'respiratoryPrescription': latest_prescription.respiratoryPrescription,
#             'swallowPrescription': latest_prescription.swallowPrescription,
#             'tcePrescription': latest_prescription.tcePrescription,
#         })
#
#         return JsonResponse({
#             'latest_prescription': latest_data,
#             'other_prescriptions': other_data,
#             'urls_data': urls_data
#         })
#
#     return JsonResponse({'error': '无效的请求方法'}, status=405)


# @csrf_exempt
# def get_exercise_record(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             id_card = data.get('id_card')
#             name = data.get('name')
#             phone = data.get('phone')
#             doctor = data.get('doctor')
#             current_time_str = data.get('current_time')
#
#             if not all([id_card, name, phone, doctor, current_time_str]):
#                 return JsonResponse({'error': '缺少必填字段'}, status=400)
#
#             try:
#                 current_time = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M:%S')
#             except ValueError:
#                 return JsonResponse({'error': 'Invalid date format'}, status=400)
#
#             records = ExerciseRecord.objects.filter(id_card=id_card, name=name, phone=phone, doctor=doctor).order_by('-submission_time')
#
#             if not records.exists():
#                 return JsonResponse({'message': '不存在'}, status=404)
#
#             latest_record = records.first()
#             seven_days_ago = timezone.now() - timedelta(days=7)
#             count_within_seven_days = records.filter(submission_time__gte=seven_days_ago).count()
#
#             start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
#             end_of_day = start_of_day + timedelta(days=1)
#             day_records = records.filter(submission_time__range=(start_of_day, end_of_day))
#
#             count_brackets = sum(
#                 len(item) if isinstance(item, list) else len(json.loads(item))
#                 for record in day_records
#                 for item in (record.training_content if isinstance(record.training_content, list) else json.loads(record.training_content))
#             )
#
#             count_lists = sum(
#                 1 if isinstance(item, list) else 1
#                 for record in day_records
#                 for item in (record.training_content if isinstance(record.training_content, list) else json.loads(record.training_content))
#             )
#
#             return JsonResponse({
#                 'latest_training_content': latest_record.training_content,
#                 'count_within_seven_days': count_within_seven_days,
#                 'count_brackets': count_brackets,
#                 'count_lists': count_lists
#             })
#
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'error': 'Invalid request method'}, status=405)
def count_repetitive(rep_item):
    count = 0
    if isinstance(rep_item, list):
        for it in rep_item:
            if isinstance(it, dict):
                count += 1
            elif isinstance(it, list):
                count += len(it)
    return count
@csrf_exempt
def get_exercise_record(request):
    if request.method == 'POST':
        try:
            # 解析请求数据
            data = json.loads(request.body)
            id_card = data.get("id_card")
            name = data.get("name")
            phone = data.get("phone")
            doctor = data.get("doctor")
            current_time_str = data.get("current_time")

            if not all([id_card, name, phone, doctor, current_time_str]):
                return JsonResponse({"error": "缺少必填字段"}, status=400)

            try:
                current_time = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return JsonResponse({"error": "Invalid date format"}, status=400)

            # 获取该id_card、name、phone、doctor的所有记录
            records = ExerciseRecord.objects.filter(
                id_card=id_card, name=name, phone=phone, doctor=doctor
            ).order_by("-submission_time")

            if not records.exists():
                return JsonResponse({"message": "不存在"}, status=404)

            # 七天内运动的天数：记录条数（如果一天多条，也作为多次记录）
            seven_days_ago = timezone.now() - timedelta(days=7)
            count_within_seven_days = records.filter(submission_time__gte=seven_days_ago).count()

            # 统计当天的记录（以请求中的current_time为当天依据）
            start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            day_records = records.filter(submission_time__range=(start_of_day, end_of_day))

            # 初始化当天运动统计数据
            today_motion_count = 0  # 今天运动的次数（组数）
            today_total_duration_minutes = 0  # 今天时长运动的分钟（continuousAction中duration之和）
            today_repetition_count = 0  # 今天次数运动的个数（repetitiveAction中字典个数）

            for record in day_records:
                # training_content为一个列表，每个元素为字符串格式的JSON数据
                if isinstance(record.training_content, list):
                    for group in record.training_content:
                        try:
                            group_data = json.loads(group)
                        except json.JSONDecodeError:
                            continue
                        today_motion_count += 1
                        # 累加continuousAction中duration之和
                        for action in group_data.get("continuousAction", []):
                            duration_str = action.get("duration", "0")
                            try:
                                today_total_duration_minutes += int(duration_str)
                            except ValueError:
                                continue
                        # 累加repetitiveAction中所有字典的个数
                        rep_item = group_data.get("repetitiveAction", [])
                        today_repetition_count += count_repetitive(rep_item)
                else:
                    try:
                        content = json.loads(record.training_content)
                        today_motion_count += 1
                        for action in content.get("continuousAction", []):
                            duration_str = action.get("duration", "0")
                            try:
                                today_total_duration_minutes += int(duration_str)
                            except ValueError:
                                continue
                        rep_item = content.get("repetitiveAction", [])
                        today_repetition_count += count_repetitive(rep_item)
                    except Exception:
                        continue

            return JsonResponse({
                "count_within_seven_days": count_within_seven_days,
                "today_motion_count": today_motion_count,
                "today_total_duration_minutes": today_total_duration_minutes,
                "today_repetition_count": today_repetition_count
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
# @csrf_exempt
# def get_exercise_record(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             id_card = data.get('id_card')
#             name = data.get('name')
#             phone = data.get('phone')
#             doctor = data.get('doctor')
#
#             if not all([id_card, name, phone, doctor]):
#                 return JsonResponse({'error': '缺少必填字段'}, status=400)
#
#             records = ExerciseRecord.objects.filter(id_card=id_card, name=name, phone=phone, doctor=doctor).order_by('-submission_time')
#
#             if not records.exists():
#                 return JsonResponse({'message': '不存在'}, status=404)
#
#             latest_record = records.first()
#             seven_days_ago = timezone.now() - timedelta(days=7)
#             count_within_seven_days = records.filter(submission_time__gte=seven_days_ago).count()
#
#             return JsonResponse({
#                 'latest_training_content': latest_record.training_content,
#                 'count_within_seven_days': count_within_seven_days
#             })
#
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'error': 'Invalid request method'}, status=405)


# @csrf_exempt
# def save_exercise_record(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             id_card = data.get('id_card')
#             name = data.get('name')
#             phone = data.get('phone')
#             doctor = data.get('doctor')
#             training_content = data.get('training_content')
#             submission_time = timezone.now()
#
#             if not all([id_card, name, phone, doctor, training_content]):
#                 return JsonResponse({'error': '缺少必填字段'}, status=400)
#
#             # Check if there is an existing record for the same day
#             start_of_day = submission_time.replace(hour=0, minute=0, second=0, microsecond=0)
#             end_of_day = start_of_day + timedelta(days=1)
#             existing_record = ExerciseRecord.objects.filter(
#                 id_card=id_card, name=name, phone=phone, doctor=doctor,
#                 submission_time__range=(start_of_day, end_of_day)
#             ).first()
#
#             if existing_record:
#                 # Update the existing record
#                 existing_record.training_content += f"\n{training_content}"
#                 existing_record.submission_time = submission_time
#                 existing_record.save()
#             else:
#                 # Create a new record
#                 ExerciseRecord.objects.create(
#                     id_card=id_card,
#                     name=name,
#                     phone=phone,
#                     doctor=doctor,
#                     training_content=training_content,
#                     submission_time=submission_time
#                 )
#
#             return JsonResponse({'message': '记录保存成功'}, status=200)
#
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def save_exercise_record(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_card = data.get('id_card')
            name = data.get('name')
            phone = data.get('phone')
            doctor = data.get('doctor')
            training_content = data.get('training_content')
            submission_time = timezone.now()

            if not all([id_card, name, phone, doctor, training_content]):
                return JsonResponse({'error': '缺少必填字段'}, status=400)

            # Check if there is an existing record for the same day
            start_of_day = submission_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            existing_record = ExerciseRecord.objects.filter(
                id_card=id_card, name=name, phone=phone, doctor=doctor,
                submission_time__range=(start_of_day, end_of_day)
            ).first()

            if existing_record:
                # Update the existing record
                existing_content = existing_record.training_content
                if isinstance(existing_content, list):
                    existing_content.append(training_content)
                else:
                    existing_content = [existing_content, training_content]
                existing_record.training_content = existing_content
                existing_record.submission_time = submission_time
                existing_record.save()
            else:
                # Create a new record
                ExerciseRecord.objects.create(
                    id_card=id_card,
                    name=name,
                    phone=phone,
                    doctor=doctor,
                    training_content=[training_content],  # Store as a list
                    submission_time=submission_time
                )

            return JsonResponse({'message': '记录保存成功'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# @csrf_exempt
# def generate_audio_sequence(request):
#     """
#     接收前端 motion_sequence (POST JSON)，
#     生成按顺序拼好的音频文件并返回。
#     """
#     if request.method == 'POST':
#         try:
#             # 1. 解析 body
#             body = request.body.decode('utf-8')
#             data = json.loads(body)
#             motion_sequence = data.get('motion_sequence', [])
#
#             if not motion_sequence:
#                 return JsonResponse({"error": "No motion_sequence data provided."}, status=400)
#
#             # 2. 获取按顺序的音频URL列表
#             audio_url_sequence = build_audio_url_sequence(motion_sequence)
#
#             # 如果你不想合并音频，而是返回此列表给前端自行顺序播放：
#             # return JsonResponse({"audio_urls": audio_url_sequence}, status=200)
#
#             # 3. 后端用 pydub 来拼接所有音频
#             final_audio = None
#             for url in audio_url_sequence:
#                 if not url:  # 可能有空字符串，表示没找到音频
#                     continue
#                 resp = requests.get(url)
#                 if resp.status_code != 200:
#                     continue
#                 # 假设你的音频文件都是 mp3
#                 segment = AudioSegment.from_file(io.BytesIO(resp.content), format="mp3")
#
#                 if final_audio is None:
#                     final_audio = segment
#                 else:
#                     final_audio += segment  # pydub 用 + 或 += 来拼接音频
#
#             if not final_audio:
#                 return JsonResponse({"error": "No valid audio to merge."}, status=400)
#
#             # 4. 导出结果到内存
#             output_buffer = io.BytesIO()
#             final_audio.export(output_buffer, format="mp3")
#             output_buffer.seek(0)
#
#             # 5. 返回给前端
#             #    content_type = "audio/mpeg" 或 "audio/mp3" 皆可
#             response = HttpResponse(output_buffer, content_type="audio/mpeg")
#             response['Content-Disposition'] = 'attachment; filename="final_audio.mp3"'
#             return response
#
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
#
#     else:
#         # 如果不是 POST，就返回 405 (Method Not Allowed)
#         return JsonResponse({"error": "Only POST method is allowed."}, status=405)

@csrf_exempt
def generate_audio_sequence(request):
    if request.method == 'POST':
        try:
            # 1. 解析body
            body = request.body.decode('utf-8')
            data = json.loads(body)
            motion_sequence = data.get('motion_sequence', [])

            if not motion_sequence:
                return JsonResponse({"error": "No motion_sequence data provided."}, status=400)

            # 2. 通过 services.py 的函数，获取 (type, value) 的列表
            audio_sequence = build_audio_url_sequence(motion_sequence)
            if not audio_sequence:
                return JsonResponse({"error": "build_audio_url_sequence returned empty."}, status=400)

            final_audio = None

            # 3. 逐个处理
            for item_type, item_value in audio_sequence:
                if item_type == "audio":
                    # item_value 是字符串URL
                    resp = requests.get(item_value)
                    if resp.status_code != 200:
                        # 如果下载失败，继续下一个
                        continue

                    # 假设是 mp3
                    segment = AudioSegment.from_file(io.BytesIO(resp.content), format="mp3")

                elif item_type == "silence":
                    # item_value 是毫秒数
                    segment = AudioSegment.silent(duration=item_value)

                else:
                    # 其它类型不做处理
                    continue

                # 拼接
                if final_audio is None:
                    final_audio = segment
                else:
                    final_audio += segment

            if final_audio is None:
                return JsonResponse({"error": "No valid segments to merge."}, status=400)

            # 4. 导出
            output_buffer = io.BytesIO()
            final_audio.export(output_buffer, format="mp3")
            output_buffer.seek(0)

            # 5. 返回给前端
            response = HttpResponse(output_buffer.read(), content_type="audio/mpeg")
            response['Content-Disposition'] = 'attachment; filename="final_audio.mp3"'
            return response

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)


