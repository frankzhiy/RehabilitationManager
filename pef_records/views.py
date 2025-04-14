from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PatientPEFRecord, PatientBestPEFRecord
import json
import datetime

@csrf_exempt
def upload_pef_record(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            id_card = data.get('id_card')
            phone = data.get('phone')
            doctor = data.get('doctor')
            name = data.get('name')
            date_text = data.get('dateText')
            # Always create and save a new PEF record
            record = PatientPEFRecord(
                id_card=id_card,
                phone=phone,
                doctor=doctor,
                name=name,
                pefValue=data.get('pefValue'),
                dateText=date_text,
                currentTime=data.get('currentTime'),
            )
            record.save()
            message = 'PEF record saved successfully!'
            return JsonResponse({'status': 'success', 'message': message})
        except Exception as e:
            # Return error response
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@csrf_exempt  # 修改后upload_best_pef_record会覆盖已有记录
def upload_best_pef_record(request):
    if request.method == 'POST':
        try:
            # 解析 JSON 数据
            data = json.loads(request.body)
            # 检查是否存在相同条件的最佳PEF记录
            existing_record = PatientBestPEFRecord.objects.filter(
                id_card=data.get('id_card'),
                phone=data.get('phone'),
                doctor=data.get('doctor'),
                name=data.get('name')
            ).first()
            if existing_record:
                # 更新已存在的记录
                existing_record.bestpefInput = data.get('bestpefInput')
                existing_record.currentTime = data.get('currentTime')
                existing_record.save()
                message = '最佳PEF记录 updated successfully!'
            else:
                # 创建并保存新的最佳PEF记录
                best_record = PatientBestPEFRecord(
                    id_card=data.get('id_card'),
                    phone=data.get('phone'),
                    doctor=data.get('doctor'),
                    name=data.get('name'),
                    bestpefInput=data.get('bestpefInput'),
                    currentTime=data.get('currentTime'),
                )
                best_record.save()
                message = '最佳PEF记录 saved successfully!'
            return JsonResponse({'status': 'success', 'message': message})
        except Exception as e:
            # 返回错误响应
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})


@csrf_exempt  # 修改后的 get_pef_records
def get_pef_records(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')
        if not (name and id_card and phone and doctor):
            return JsonResponse({'status': 'error', 'message': '必须提供name, id_card, phone和doctor'})
        try:
            # 查询PatientPEFRecord最新记录（按currentTime降序排序）
            record = PatientPEFRecord.objects.filter(
                name=name,
                id_card=id_card,
                phone=phone,
                doctor=doctor
            ).order_by('-currentTime').first()
            if record:
                data = {
                    'pefValue': record.pefValue,
                    'dateText': record.dateText
                }
                return JsonResponse({'status': 'success', 'data': data})
            else:
                return JsonResponse({'status': 'error', 'message': '未找到PEF记录'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})

@csrf_exempt  # 修改后的 get_best_pef_records
def get_best_pef_records(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')
        if not (name and id_card and phone and doctor):
            return JsonResponse({'status': 'error', 'message': '必须提供name, id_card, phone和doctor'})
        try:
            # 查询PatientBestPEFRecord最新记录（按currentTime降序排序）
            record = PatientBestPEFRecord.objects.filter(
                name=name,
                id_card=id_card,
                phone=phone,
                doctor=doctor
            ).order_by('-currentTime').first()
            if record:
                data = {'bestpefInput': record.bestpefInput}
                return JsonResponse({'status': 'success', 'data': data})
            else:
                return JsonResponse({'status': 'error', 'message': '未找到最佳PEF记录'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})

@csrf_exempt
def get_patient_records(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')

        if not (name and id_card and phone and doctor):
            return JsonResponse({'status': 'error', 'message': '必须提供name, id_card, phone和doctor'})

        try:
            # 查询PatientPEFRecord中所有符合条件的条目
            pef_records = PatientPEFRecord.objects.filter(
                name=name,
                id_card=id_card,
                phone=phone,
                doctor=doctor
            )

            # 查询PatientBestPEFRecord中符合条件的且bestpefInput列中值最大的条目
            best_pef_record = PatientBestPEFRecord.objects.filter(
                name=name,
                id_card=id_card,
                phone=phone,
                doctor=doctor
            ).order_by('-bestpefInput').first()

            pef_records_list = list(pef_records.values())
            best_pef_record_data = best_pef_record.__dict__ if best_pef_record else None
            if best_pef_record_data:
                best_pef_record_data.pop('_state', None)  # Remove the internal state attribute

            return JsonResponse({
                'status': 'success',
                'pef_records': pef_records_list,
                'best_pef_record': best_pef_record_data
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})