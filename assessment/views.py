from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import RespiratoryAssessment, TCEAssessment, StepAssessment, SwallowAssessment, LimbAssessment, PEFAssessment

@csrf_exempt
def upload_respiratory_assessment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = RespiratoryAssessment(
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                isUploadByDoctor = data.get('isUploadByDoctor', True),
                MEP=data.get('MEP'),
                MIP=data.get('MIP'),
                RespiratoryUploadTime=data.get('RespiratoryUploadTime')
            )
            record.save()
            return JsonResponse({'status': 'success', 'message': 'Respiratory Assessment data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_tce_assessment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = TCEAssessment(
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                isUploadByDoctor = data.get('isUploadByDoctor', True),
                TCE=data.get('TCE'),
                TCEUploadTime=data.get('TCEUploadTime')
            )
            record.save()
            return JsonResponse({'status': 'success', 'message': 'TCE Assessment data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_step_assessment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = StepAssessment(
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                isUploadByDoctor = data.get('isUploadByDoctor', True),
                MWT=data.get('MWT'),
                STEP=data.get('STEP'),
                STEPUploadTime=data.get('STEPUploadTime')
            )
            record.save()
            return JsonResponse({'status': 'success', 'message': 'Step Assessment data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_swallow_assessment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = SwallowAssessment(
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                isUploadByDoctor = data.get('isUploadByDoctor', True),
                swallowStatus=data.get('swallowStatus'),
                swallowStatusUploadTime=data.get('swallowStatusUploadTime')
            )
            record.save()
            return JsonResponse({'status': 'success', 'message': 'Swallow Assessment data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_limb_assessment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = LimbAssessment(
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                isUploadByDoctor = data.get('isUploadByDoctor', True),
                limbStatus=data.get('limbStatus'),
                limbStatusUploadTime=data.get('limbStatusUploadTime')
            )
            record.save()
            return JsonResponse({'status': 'success', 'message': 'Limb Assessment data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_pef_assessment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = PEFAssessment(
                doctor=data.get('doctor'),
                id_card=data.get('id_card'),
                name=data.get('name'),
                phone=data.get('phone'),
                isUploadByDoctor = data.get('isUploadByDoctor', True),
                PEF=data.get('PEF'),
                PEFUploadTime=data.get('PEFUploadTime')
            )
            record.save()
            return JsonResponse({'status': 'success', 'message': 'PEF Assessment data saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SwallowAssessment

@csrf_exempt
def get_latest_swallow_status(request):
    if request.method == 'GET':
        try:
            doctor = request.GET.get('doctor')
            id_card = request.GET.get('id_card')
            name = request.GET.get('name')
            phone = request.GET.get('phone')

            # Query the database for the matching record and order by swallowStatusUploadTime descending
            record = SwallowAssessment.objects.filter(
                doctor=doctor,
                id_card=id_card,
                name=name,
                phone=phone
            ).order_by('-swallowStatusUploadTime').first()

            if record:
                return JsonResponse({
                    'status': 'success',
                    'swallowStatus': record.swallowStatus,
                    'swallowStatusUploadTime': record.swallowStatusUploadTime
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'No matching record found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def get_latest_respiratory_assessment(request):
    if request.method == 'GET':
        try:
            doctor = request.GET.get('doctor')
            id_card = request.GET.get('id_card')
            name = request.GET.get('name')
            phone = request.GET.get('phone')

            # Query the database for the matching record and order by RespiratoryUploadTime descending
            record = RespiratoryAssessment.objects.filter(
                doctor=doctor,
                id_card=id_card,
                name=name,
                phone=phone
            ).order_by('-RespiratoryUploadTime').first()

            if record:
                return JsonResponse({
                    'status': 'success',
                    'MEP': record.MEP,
                    'MIP': record.MIP,
                    'RespiratoryUploadTime': record.RespiratoryUploadTime
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'No matching record found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TCEAssessment, StepAssessment, LimbAssessment, PEFAssessment

@csrf_exempt
def get_latest_tce_assessment(request):
    if request.method == 'GET':
        try:
            doctor = request.GET.get('doctor')
            id_card = request.GET.get('id_card')
            name = request.GET.get('name')
            phone = request.GET.get('phone')

            record = TCEAssessment.objects.filter(
                doctor=doctor,
                id_card=id_card,
                name=name,
                phone=phone
            ).order_by('-TCEUploadTime').first()

            if record:
                return JsonResponse({
                    'status': 'success',
                    'TCE': record.TCE,
                    'TCEUploadTime': record.TCEUploadTime
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'No matching record found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def get_latest_step_assessment(request):
    if request.method == 'GET':
        try:
            doctor = request.GET.get('doctor')
            id_card = request.GET.get('id_card')
            name = request.GET.get('name')
            phone = request.GET.get('phone')

            record = StepAssessment.objects.filter(
                doctor=doctor,
                id_card=id_card,
                name=name,
                phone=phone
            ).order_by('-STEPUploadTime').first()

            if record:
                return JsonResponse({
                    'status': 'success',
                    'MWT': record.MWT,
                    'STEP': record.STEP,
                    'STEPUploadTime': record.STEPUploadTime
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'No matching record found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def get_latest_limb_assessment(request):
    if request.method == 'GET':
        try:
            doctor = request.GET.get('doctor')
            id_card = request.GET.get('id_card')
            name = request.GET.get('name')
            phone = request.GET.get('phone')

            record = LimbAssessment.objects.filter(
                doctor=doctor,
                id_card=id_card,
                name=name,
                phone=phone
            ).order_by('-limbStatusUploadTime').first()

            if record:
                return JsonResponse({
                    'status': 'success',
                    'limbStatus': record.limbStatus,
                    'limbStatusUploadTime': record.limbStatusUploadTime
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'No matching record found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def get_latest_pef_assessment(request):
    if request.method == 'GET':
        try:
            doctor = request.GET.get('doctor')
            id_card = request.GET.get('id_card')
            name = request.GET.get('name')
            phone = request.GET.get('phone')

            record = PEFAssessment.objects.filter(
                doctor=doctor,
                id_card=id_card,
                name=name,
                phone=phone
            ).order_by('-PEFUploadTime').first()

            if record:
                return JsonResponse({
                    'status': 'success',
                    'PEF': record.PEF,
                    'PEFUploadTime': record.PEFUploadTime
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'No matching record found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

