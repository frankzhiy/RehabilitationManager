from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from registration.models import UserProfile


@csrf_exempt
def get_unverified_patients(request):
    if request.method == 'GET':
        doctor = request.GET.get('doctor')
        if not doctor:
            return JsonResponse({'status': 'error', 'message': '必须提供医生信息'})

        try:
            unverified_patients = UserProfile.objects.filter(doctor=doctor, is_verified=False)
            if not unverified_patients.exists():
                return JsonResponse({'status': 'success', 'message': '目前没有待审核患者'})

            patients_list = list(unverified_patients.values())
            return JsonResponse({'status': 'success', 'data': patients_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': '无效请求'})