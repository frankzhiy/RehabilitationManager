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

            # Check if a record with the same id_card, phone, doctor, name, and dateText exists
            existing_record = PatientPEFRecord.objects.filter(
                id_card=id_card,
                phone=phone,
                doctor=doctor,
                name=name,
                dateText=date_text
            ).first()

            if existing_record:
                # Update the existing record's pefValue
                existing_record.pefValue = data.get('pefValue')
                existing_record.save()
                message = 'PEF record updated successfully!'
            else:
                # Create and save a new PEF record
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

            # Return success response
            return JsonResponse({'status': 'success', 'message': message})
        except Exception as e:
            # Return error response
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@csrf_exempt  # 如果启用了CSRF保护，在开发阶段可以暂时禁用它
def upload_best_pef_record(request):
    if request.method == 'POST':
        try:
            # 解析 JSON 数据
            data = json.loads(request.body)

            # 创建并保存最佳PEF记录
            best_record = PatientBestPEFRecord(
                id_card=data.get('id_card'),
                phone=data.get('phone'),
                doctor=data.get('doctor'),
                name=data.get('name'),
                bestpefInput=data.get('bestpefInput'),
                currentTime=data.get('currentTime'),
            )
            best_record.save()

            # 返回成功响应
            return JsonResponse({'status': 'success', 'message': '最佳PEF记录保存成功!'})
        except Exception as e:
            # 返回错误响应
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})


@csrf_exempt  # 获取PEF记录
def get_pef_records(request):
    if request.method == 'GET':
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')

        if not id_card and not phone:
            return JsonResponse({'status': 'error', 'message': '必须提供id_card或phone'})

        try:
            if id_card:
                records = PatientPEFRecord.objects.filter(id_card=id_card)
            elif phone:
                records = PatientPEFRecord.objects.filter(phone=phone)

            records_list = list(records.values())
            return JsonResponse({'status': 'success', 'data': records_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})


@csrf_exempt  # 获取最佳PEF记录
def get_best_pef_records(request):
    if request.method == 'GET':
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')

        if not id_card and not phone:
            return JsonResponse({'status': 'error', 'message': '必须提供id_card或phone'})

        try:
            if id_card:
                record = PatientBestPEFRecord.objects.filter(id_card=id_card).order_by('-currentTime').first()
            elif phone:
                record = PatientBestPEFRecord.objects.filter(phone=phone).order_by('-currentTime').first()

            if record:
                record_data = record.__dict__
                record_data.pop('_state', None)  # Remove the internal state attribute
                return JsonResponse({'status': 'success', 'data': record_data})
            else:
                return JsonResponse({'status': 'error', 'message': '未找到记录'})
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