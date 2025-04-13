from collections import defaultdict

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from discomfort.models import PatientDiscomfortRecordWarn
from questionnaire.models import PatientADLWarn, PatientCATWarn, PatientmMRCWarn, PatientCCQWarn
import json
from django.forms.models import model_to_dict

@csrf_exempt
def patient_warn_view(request):
    if request.method == 'GET':
        doctor = request.GET.get('doctor')

        if not doctor:
            return JsonResponse({'status': 'error', 'message': '缺少医生信息'})

        try:
            patient_set = set()
            warn_models = [PatientDiscomfortRecordWarn, PatientADLWarn, PatientCATWarn, PatientmMRCWarn, PatientCCQWarn]

            for model in warn_models:
                patients = model.objects.filter(doctor=doctor, is_active=True).values('id_card', 'phone', 'name')
                for patient in patients:
                    patient_tuple = (patient['id_card'], patient['phone'], patient['name'])
                    patient_set.add(patient_tuple)

            data = []

            for id_card, phone, name in patient_set:
                patient_filter = Q(doctor=doctor) & Q(id_card=id_card) & Q(phone=phone) & Q(name=name) & Q(is_active=True)

                # Group records by date
                records_by_date = defaultdict(lambda: defaultdict(list))
                for model in warn_models:
                    records = model.objects.filter(patient_filter).order_by('-uploadTime' if model != PatientDiscomfortRecordWarn else '-datetime')
                    for record in records:
                        record_date = record.uploadTime.date() if model != PatientDiscomfortRecordWarn else record.datetime.date()
                        records_by_date[record_date][model.__name__].append(record)

                # Select the latest records for each type on the same date
                for record_date, records in records_by_date.items():
                    discomfort_record = records[PatientDiscomfortRecordWarn.__name__][0] if records[PatientDiscomfortRecordWarn.__name__] else None
                    adl_record = records[PatientADLWarn.__name__][0] if records[PatientADLWarn.__name__] else None
                    cat_record = records[PatientCATWarn.__name__][0] if records[PatientCATWarn.__name__] else None
                    mmrc_record = records[PatientmMRCWarn.__name__][0] if records[PatientmMRCWarn.__name__] else None
                    ccq_record = records[PatientCCQWarn.__name__][0] if records[PatientCCQWarn.__name__] else None

                    patient_data = {
                        'id_card': id_card,
                        'phone': phone,
                        'name': name,
                        'PatientDiscomfortRecordWarn': {
                            'alert_type': discomfort_record.alert_type,
                            'datetime': discomfort_record.datetime,
                            'is_active': discomfort_record.is_active,
                            'finishedFollowup': discomfort_record.finishedFollowup,
                        } if discomfort_record else None,
                        'PatientADLWarn': {
                            'barthel_index': adl_record.barthel_index,
                            'uploadTime': adl_record.uploadTime,
                            'is_active': adl_record.is_active,
                            'finishedFollowup': adl_record.finishedFollowup,
                        } if adl_record else None,
                        'PatientCATWarn': {
                            'cat_index': cat_record.cat_index,
                            'uploadTime': cat_record.uploadTime,
                            'is_active': cat_record.is_active,
                            'finishedFollowup': cat_record.finishedFollowup,
                        } if cat_record else None,
                        'PatientmMRCWarn': {
                            'mmrc_index': mmrc_record.mmrc_index,
                            'uploadTime': mmrc_record.uploadTime,
                            'is_active': mmrc_record.is_active,
                            'finishedFollowup': mmrc_record.finishedFollowup,
                        } if mmrc_record else None,
                        'PatientCCQWarn': {
                            'ccq_index': ccq_record.ccq_index,
                            'uploadTime': ccq_record.uploadTime,
                            'is_active': ccq_record.is_active,
                            'finishedFollowup': ccq_record.finishedFollowup,
                        } if ccq_record else None,
                    }

                    data.append(patient_data)

            return JsonResponse({'status': 'success', 'data': data})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    else:
        return JsonResponse({'status': 'error', 'message': '请求方法错误'})

@csrf_exempt
def deactivate_warn_records(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if not data:
            return JsonResponse({'status': 'error', 'message': 'No data provided'}, status=400)

        try:
            id_card = data.get('id_card')
            phone = data.get('phone')
            name = data.get('name')

            if not id_card or not phone or not name:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            patient_filter = Q(id_card=id_card) & Q(phone=phone) & Q(name=name)

            if 'PatientDiscomfortRecordWarn' in data and data['PatientDiscomfortRecordWarn']:
                datetime = data['PatientDiscomfortRecordWarn'].get('datetime')
                if datetime:
                    discomfort_record = PatientDiscomfortRecordWarn.objects.filter(patient_filter, datetime=datetime).first()
                    if discomfort_record:
                        discomfort_record.is_active = False
                        discomfort_record.save()

            if 'PatientADLWarn' in data and data['PatientADLWarn']:
                uploadTime = data['PatientADLWarn'].get('uploadTime')
                if uploadTime:
                    adl_record = PatientADLWarn.objects.filter(patient_filter, uploadTime=uploadTime).first()
                    if adl_record:
                        adl_record.is_active = False
                        adl_record.save()

            if 'PatientCATWarn' in data and data['PatientCATWarn']:
                uploadTime = data['PatientCATWarn'].get('uploadTime')
                if uploadTime:
                    cat_record = PatientCATWarn.objects.filter(patient_filter, uploadTime=uploadTime).first()
                    if cat_record:
                        cat_record.is_active = False
                        cat_record.save()

            if 'PatientmMRCWarn' in data and data['PatientmMRCWarn']:
                uploadTime = data['PatientmMRCWarn'].get('uploadTime')
                if uploadTime:
                    mmrc_record = PatientmMRCWarn.objects.filter(patient_filter, uploadTime=uploadTime).first()
                    if mmrc_record:
                        mmrc_record.is_active = False
                        mmrc_record.save()

            if 'PatientCCQWarn' in data and data['PatientCCQWarn']:
                uploadTime = data['PatientCCQWarn'].get('uploadTime')
                if uploadTime:
                    ccq_record = PatientCCQWarn.objects.filter(patient_filter, uploadTime=uploadTime).first()
                    if ccq_record:
                        ccq_record.is_active = False
                        ccq_record.save()

            return JsonResponse({'status': 'success', 'message': 'Records deactivated successfully'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_patient_warn_records(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        name = data.get('name')
        id_card = data.get('id_card')
        phone = data.get('phone')
        page_number = data.get('page', 1)
        page_size = data.get('page_size', 10)

        if not name or not id_card or not phone:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        try:
            patient_filter = Q(name=name) & Q(id_card=id_card) & Q(phone=phone)

            discomfort_records = PatientDiscomfortRecordWarn.objects.filter(patient_filter)
            adl_records = PatientADLWarn.objects.filter(patient_filter)
            cat_records = PatientCATWarn.objects.filter(patient_filter)
            mmrc_records = PatientmMRCWarn.objects.filter(patient_filter)
            ccq_records = PatientCCQWarn.objects.filter(patient_filter)

            records_by_date = defaultdict(lambda: {
                'PatientDiscomfortRecordWarn': None,
                'PatientADLWarn': None,
                'PatientCATWarn': None,
                'PatientmMRCWarn': None,
                'PatientCCQWarn': None,
            })

            for record in discomfort_records:
                record_date = record.datetime.date()
                records_by_date[record_date]['PatientDiscomfortRecordWarn'] = record

            for record in adl_records:
                record_date = record.uploadTime.date()
                records_by_date[record_date]['PatientADLWarn'] = record

            for record in cat_records:
                record_date = record.uploadTime.date()
                records_by_date[record_date]['PatientCATWarn'] = record

            for record in mmrc_records:
                record_date = record.uploadTime.date()
                records_by_date[record_date]['PatientmMRCWarn'] = record

            for record in ccq_records:
                record_date = record.uploadTime.date()
                records_by_date[record_date]['PatientCCQWarn'] = record

            all_records = []
            for date, records in records_by_date.items():
                record_data = {
                    'date': date,
                    'records': {
                        'PatientDiscomfortRecordWarn': records['PatientDiscomfortRecordWarn'] and model_to_dict(records['PatientDiscomfortRecordWarn']),
                        'PatientADLWarn': records['PatientADLWarn'] and model_to_dict(records['PatientADLWarn']),
                        'PatientCATWarn': records['PatientCATWarn'] and model_to_dict(records['PatientCATWarn']),
                        'PatientmMRCWarn': records['PatientmMRCWarn'] and model_to_dict(records['PatientmMRCWarn']),
                        'PatientCCQWarn': records['PatientCCQWarn'] and model_to_dict(records['PatientCCQWarn']),
                    }
                }
                all_records.append(record_data)

            paginator = Paginator(all_records, page_size)
            page = paginator.get_page(page_number)
            paginated_records = list(page)

            return JsonResponse({'status': 'success', 'data': paginated_records}, safe=False)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
# def get_patient_warn_records(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#
#         name = data.get('name')
#         id_card = data.get('id_card')
#         phone = data.get('phone')
#         page_number = data.get('page', 1)
#         page_size = data.get('page_size', 10)
#
#         if not name or not id_card or not phone:
#             return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
#
#         try:
#             patient_filter = Q(name=name) & Q(id_card=id_card) & Q(phone=phone)
#
#             discomfort_records = PatientDiscomfortRecordWarn.objects.filter(patient_filter)
#             adl_records = PatientADLWarn.objects.filter(patient_filter)
#             cat_records = PatientCATWarn.objects.filter(patient_filter)
#             mmrc_records = PatientmMRCWarn.objects.filter(patient_filter)
#             ccq_records = PatientCCQWarn.objects.filter(patient_filter)
#
#             all_records = {
#                 'PatientDiscomfortRecordWarn': list(discomfort_records.values()),
#                 'PatientADLWarn': list(adl_records.values()),
#                 'PatientCATWarn': list(cat_records.values()),
#                 'PatientmMRCWarn': list(mmrc_records.values()),
#                 'PatientCCQWarn': list(ccq_records.values()),
#             }
#
#             paginated_records = {}
#             for key, records in all_records.items():
#                 paginator = Paginator(records, page_size)
#                 page = paginator.get_page(page_number)
#                 paginated_records[key] = list(page)
#                 # print(
#                 #     f"{key} - Total records: {len(records)}, Page: {page_number}, Page size: {page_size}, Records on this page: {len(page)}")
#
#             return JsonResponse({'status': 'success', 'data': paginated_records}, safe=False)
#
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
#
#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)