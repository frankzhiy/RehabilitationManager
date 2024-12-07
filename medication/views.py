from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PatientMedicationRecord
import json


@csrf_exempt  # 如果启用了CSRF保护，在开发阶段可以暂时禁用它
def upload_medication_record(request):
    if request.method == 'POST':
        try:
            # 解析 JSON 数据
            data = json.loads(request.body)

            # 创建并保存新的用药记录
            record = PatientMedicationRecord(
                id_card=data.get('id_card'),
                phone=data.get('phone'),
                doctor=data.get('doctor'),
                name=data.get('name'),
                medicinesName=data.get('medicinesName'),
                medicinesProfessionalName=data.get('medicinesProfessionalName'),
                medicinesFullDateTime=data.get('medicinesFullDateTime'),
            )
            print(record)
            record.save()

            # 返回成功响应
            return JsonResponse({'status': 'success', 'message': '数据保存成功!'})
        except Exception as e:
            # 返回错误响应
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})

@csrf_exempt
def get_medication_records(request):
    if request.method == 'GET':
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')

        if not id_card and not phone:
            return JsonResponse({'status': 'error', 'message': '必须提供id_card或phone'})

        try:
            if id_card:
                records = PatientMedicationRecord.objects.filter(id_card=id_card)
            elif phone:
                records = PatientMedicationRecord.objects.filter(phone=phone)

            records_list = list(records.values())
            return JsonResponse({'status': 'success', 'data': records_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})


@csrf_exempt
def get_medication_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_card = data.get('id_card')
            doctor = data.get('doctor')
            name = data.get('name')
            phone = data.get('phone')

            if not id_card or not doctor or not name or not phone:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            records = PatientMedicationRecord.objects.filter(
                id_card=id_card,
                doctor=doctor,
                name=name,
                phone=phone
            )

            records_info = [
                {
                    'medicinesName': record.medicinesName,
                    'medicinesProfessionalName': record.medicinesProfessionalName,
                    'medicinesFullDateTime': record.medicinesFullDateTime,
                }
                for record in records
            ]

            return JsonResponse({'status': 'success', 'data': records_info})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)