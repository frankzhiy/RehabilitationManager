import json
from django.http import JsonResponse
from .models import PatientDiscomfortRecord
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from .service import process_discomfort_record
@csrf_exempt
def upload_discomfort_record(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)

            # Parse boolean fields
            comfort = data.get('comfort')
            appetiteLoss = data.get('appetiteLoss')
            breathing = data.get('breathing')
            breathingWorsened = data.get('breathingWorsened')
            cough = data.get('cough')
            coughWorsened = data.get('coughWorsened')
            fastHeartbeat = data.get('fastHeartbeat')
            fatigue = data.get('fatigue')
            fever = data.get('fever')
            sleepPatternChange = data.get('sleepPatternChange')
            sputum = data.get('sputum')
            sputumIncreased = data.get('sputumIncreased')
            swollenLegs = data.get('swollenLegs')
            weightLoss = data.get('weightLoss')
            datetime = parse_datetime(data.get('datetime'))
            # Create and save the new discomfort record
            record = PatientDiscomfortRecord(
                id_card=data.get('id_card'),
                phone=data.get('phone'),
                doctor=data.get('doctor'),
                name=data.get('name'),
                comfort=comfort,
                appetiteLoss=appetiteLoss,
                breathing=breathing,
                breathingWorsened=breathingWorsened,
                cough=cough,
                coughWorsened=coughWorsened,
                fastHeartbeat=fastHeartbeat,
                fatigue=fatigue,
                fever=fever,
                sleepPatternChange=sleepPatternChange,
                sputum=sputum,
                sputumIncreased=sputumIncreased,
                swollenLegs=swollenLegs,
                weightLoss=weightLoss,
                datetime=datetime
            )
            record.save()
            process_discomfort_record(record)
            # Return a success response
            return JsonResponse({'status': 'success', 'message': '数据保存成功!'})
        except Exception as e:
            # Return an error response
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})

@csrf_exempt
def get_discomfort_records(request):
    if request.method == 'GET':
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')

        # Ensure either id_card or phone is provided
        if not id_card and not phone:
            return JsonResponse({'status': 'error', 'message': '必须提供id_card或phone'})

        try:
            # Fetch records based on id_card or phone
            if id_card:
                records = PatientDiscomfortRecord.objects.filter(id_card=id_card)
            elif phone:
                records = PatientDiscomfortRecord.objects.filter(phone=phone)

            # Convert queryset to list of dictionaries
            records_list = list(records.values())

            # Return the records in a JSON response
            return JsonResponse({'status': 'success', 'data': records_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})


@csrf_exempt
def get_discomfort_records_by_doctor(request):
    if request.method == 'GET':
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')
        name = request.GET.get('name')

        # Ensure all fields are provided
        if not id_card or not phone or not doctor or not name:
            return JsonResponse({'status': 'error', 'message': '必须提供id_card, phone, doctor 和 name'})

        try:
            # Fetch records based on all four fields
            records = PatientDiscomfortRecord.objects.filter(
                id_card=id_card,
                phone=phone,
                doctor=doctor,
                name=name
            )

            # Convert queryset to list of dictionaries
            records_list = list(records.values())

            # Return the records in a JSON response
            return JsonResponse({'status': 'success', 'data': records_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})