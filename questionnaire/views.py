from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PatientADL, PatientCAT, PatientmMRC, PatientCCQ, PatientADLWarn
import json
from .service import process_adl_data, process_cat_data, process_mmrc_data, process_ccq_data


@csrf_exempt
def upload_adl(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = PatientADL(
                hygiene=data.get('hygiene'),
                stool=data.get('stool'),
                urinating=data.get('urinating'),
                bathing=data.get('bathing'),
                dressing=data.get('dressing'),
                feeding=data.get('feeding'),
                stairs=data.get('stairs'),
                toileting=data.get('toileting'),
                transferring=data.get('transferring'),
                walking=data.get('walking'),
                score=data.get('score'),
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                uploadTime=data.get('uploadTime'),
                isbydoctor=data.get('isbydoctor')
            )
            record.save()

            # 调用 service.py 中的函数
            process_adl_data(record)

            return JsonResponse({'status': 'success', 'message': 'ADL data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
# @csrf_exempt
# def upload_adl(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             record = PatientADL(
#                 hygiene=data.get('hygiene'),
#                 stool=data.get('stool'),
#                 urinating=data.get('urinating'),
#                 bathing=data.get('bathing'),
#                 dressing=data.get('dressing'),
#                 feeding=data.get('feeding'),
#                 stairs=data.get('stairs'),
#                 toileting=data.get('toileting'),
#                 transferring=data.get('transferring'),
#                 walking=data.get('walking'),
#                 score=data.get('score'),
#                 doctor=data.get('doctor'),
#                 id_card=data.get('id_card'),
#                 name=data.get('name'),
#                 phone=data.get('phone'),
#                 uploadTime=data.get('uploadTime'),
#                 isbydoctor = data.get('isbydoctor')
#             )
#             record.save()
#             return JsonResponse({'status': 'success', 'message': 'ADL data saved successfully'})
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_cat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = PatientCAT(
                chestTightness=data.get('chestTightness'),
                confidenceLeavingHome=data.get('confidenceLeavingHome'),
                cough=data.get('cough'),
                energyLevels=data.get('energyLevels'),
                homeActivities=data.get('homeActivities'),
                phlegm=data.get('phlegm'),
                shortnessOfBreath=data.get('shortnessOfBreath'),
                sleepQuality=data.get('sleepQuality'),
                score=data.get('score'),
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                uploadTime = data.get('uploadTime'),
                isbydoctor=data.get('isbydoctor')
            )
            record.save()
            process_cat_data(record)
            return JsonResponse({'status': 'success', 'message': 'CAT data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_mmrc(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = PatientmMRC(
                degreeOfBreathing=data.get('degreeOfBreathing'),
                score=data.get('score'),
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                uploadTime=data.get('uploadTime'),
                isbydoctor=data.get('isbydoctor')
            )
            record.save()
            process_mmrc_data(record)
            return JsonResponse({'status': 'success', 'message': 'mMRC data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_ccq(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = PatientCCQ(
                breathing=data.get('breathing'),
                chestTightness=data.get('chestTightness'),
                dailyActivities=data.get('dailyActivities'),
                mentalHealth=data.get('mentalHealth'),
                morningSymptoms=data.get('morningSymptoms'),
                phlegm=data.get('phlegm'),
                score=data.get('score'),
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                uploadTime=data.get('uploadTime'),
                isbydoctor=data.get('isbydoctor')
            )
            record.save()
            process_ccq_data(record)
            return JsonResponse({'status': 'success', 'message': 'CCQ data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def get_adl_by_doctor(request):
    if request.method == 'GET':
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')
        name = request.GET.get('name')

        if not id_card and not phone and not doctor and not name:
            return JsonResponse({'status': 'error', 'message': '无法找到对应患者'})

        try :
            records = list(PatientADL.objects.filter(id_card=id_card).values())

            return JsonResponse({'status': 'success', 'data': records})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '请求错误'})
@csrf_exempt
def get_cat_by_doctor(request):
    if request.method == 'GET':
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')
        name = request.GET.get('name')

        if not id_card and not phone and not doctor and not name:
            return JsonResponse({'status': 'error', 'message': '无法找到对应患者'})

        try :
            records = list(PatientCAT.objects.filter(id_card=id_card).values())

            return JsonResponse({'status': 'success', 'data': records})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '请求错误'})

@csrf_exempt
def get_mmrc_by_doctor(request):
    if request.method == 'GET':
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')
        name = request.GET.get('name')

        if not id_card and not phone and not doctor and not name:
            return JsonResponse({'status': 'error', 'message': '无法找到对应患者'})

        try :
            records = list(PatientmMRC.objects.filter(id_card=id_card).values())

            return JsonResponse({'status': 'success', 'data': records})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '请求错误'})


@csrf_exempt
def get_ccq_by_doctor(request):
    if request.method == 'GET':
        id_card = request.GET.get('id_card')
        phone = request.GET.get('phone')
        doctor = request.GET.get('doctor')
        name = request.GET.get('name')

        if not id_card and not phone and not doctor and not name:
            return JsonResponse({'status': 'error', 'message': '无法找到对应患者'})

        try :
            records = list(PatientCCQ.objects.filter(id_card=id_card).values())

            return JsonResponse({'status': 'success', 'data': records})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '请求错误'})
