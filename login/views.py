from django.http import HttpResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = User.objects.filter(username=username, password=password)
    if user:
        return HttpResponse('Success')
    else:
        return HttpResponse('Error')