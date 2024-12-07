from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from registration.models import PatientPrescription
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

from .models import MotionPrescription
from .services import get_recommendations
from django.views import View

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
                'doctor', 'id_card', 'name', 'phone', 'swallowStatusPrescription',
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



@csrf_exempt
def save_prescription(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        id_card = data.get('id_card')
        phone = data.get('phone')
        doctor = data.get('doctor')
        is_confirmed = data.get('is_confirmed', False)

        existing_prescription = MotionPrescription.objects.filter(
            name=name, id_card=id_card, phone=phone, doctor=doctor
        ).first()

        if existing_prescription and not is_confirmed:
            return JsonResponse({
                'message': '该患者已经存在运动处方，'
            })

        is_active = data.get('is_active', True) if is_confirmed else False

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
            is_active=is_active
        )
        prescription.save()

        return JsonResponse({'message': 'Prescription saved successfully.'})

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


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