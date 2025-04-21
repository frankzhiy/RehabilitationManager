from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
import json
from .models import UserProfile, DoctorProfile, PatientPrescription, PatientFollowUp, SymptomDoctor
import requests
from django.conf import settings
from Crypto.Cipher import AES
import base64


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try:
            user = UserProfile.objects.get(id_card=username)
        except UserProfile.DoesNotExist:
            try:
                user = UserProfile.objects.get(phone=username)
            except UserProfile.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=400)

        if password == user.password:
            user_info = {
                'id_card': user.id_card,
                'name': user.name,
                'sex': user.sex,
                'birth': user.birth,
                'phone': user.phone,
                'education': user.education,
                'marital_status': user.marital_status,
                'nation': user.nation,
                'occupation': user.occupation,
                'height': user.height,
                'weight': user.weight,
                'waistline': user.waistline,
                'doctor': user.doctor,
                'diseases': user.diseases,
                'is_verified': user.is_verified,
            }
            return JsonResponse({'status': 'success', 'message': '登录成功', 'user_info': user_info})
        else:
            return JsonResponse({'status': 'error', 'message': '密码错误'}, status=400)

    return JsonResponse({'status': 'error', 'message': '无效的请求'}, status=400)
@csrf_exempt  # 如果你使用AJAX，请确保处理CSRF令牌
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_card = data['IDcard']
        phone = data['phone']
        code = data.get('code')  # 获取前端传递的 code

        # Check if a user with the same ID card or phone already exists
        if UserProfile.objects.filter(id_card=id_card).exists() or UserProfile.objects.filter(phone=phone).exists():
            return JsonResponse({'status': 'error', 'message': '用户已经注册'}, status=400)

        # 调用微信接口获取 openid 和 unionid
        appid = settings.WECHAT_APPID
        secret = settings.WECHAT_SECRET

        wx_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code"
        response = requests.get(wx_url)
        wx_data = response.json()
        if 'openid' not in wx_data:
            return JsonResponse({'status': 'error', 'message': '微信认证失败'}, status=400)

        openid = wx_data['openid']
        unionid = wx_data.get('unionid', None)


        user = UserProfile(
            id_card=data['IDcard'],
            name=data['name'],
            sex=data['sex'],
            birth=data['birth'],
            phone=data['phone'],
            education=data['education'],
            marital_status=data['maritalStatus'],
            nation=data['nation'],
            occupation=data['occupation'],
            height=data['high'],
            weight=data['weight'],
            waistline=data['waistline'],
            doctor=data['doctor'],
            diseases=data['diseases'],
            password=data['password'],
            is_verified=False,  # 默认未审核
            openid=openid,
            unionid=unionid
        )
        user.save()

        # 创建处方记录
        PatientPrescription.objects.create(
            doctor=data['doctor'],
            id_card=data['IDcard'],
            name=data['name'],
            phone=data['phone'],
            sex=data['sex'],
            birth=data['birth'],
            height=data['high'],
            weight=data['weight'],
            waistline=data['waistline'],
            diseases=data['diseases'],
            swallowStatusPrescription=None,
            MepAndMipPrescription=None,
            limbStatusPrescription=None,
            PEFPrescription=None,
            TCEPrescription=None,
            MwtAndStepPrescription=None,
            uploadtime=None,
            isActive=False
        )

        # 创建随访记录
        PatientFollowUp.objects.create(
            doctor=data['doctor'],
            id_card=data['IDcard'],
            name=data['name'],
            phone=data['phone'],
            sex=data['sex'],
            birth=data['birth'],
            height=data['high'],
            weight=data['weight'],
            waistline=data['waistline'],
            diseases=data['diseases'],
            isActive=True,
            isFinished=False,
            isEnded=False
        )
        return JsonResponse({'status': 'success', 'message': 'Registration successful!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


@csrf_exempt
def register_doctor(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Create a DoctorProfile object with hashed password
        doctor = DoctorProfile(
            IDcard=data['IDcard'],
            hospital=data['hospital'],
            name=data['name'],
            password=data['password'],  # Hash password before saving
            phone=data['phone']
        )

        doctor.save()

        return JsonResponse({'status': 'success', 'message': '注册成功!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@csrf_exempt
def login_doctor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        try:
            # Try to find the doctor by IDcard first, then by phone if not found
            doctor = DoctorProfile.objects.get(IDcard=username)
        except DoctorProfile.DoesNotExist:
            try:
                doctor = DoctorProfile.objects.get(phone=username)
            except DoctorProfile.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Doctor not found'}, status=400)

        # Check the password
        if password == doctor.password:
            doctor_info = {
                'IDcard': doctor.IDcard,
                'name': doctor.name,
                'hospital': doctor.hospital,
                'phone': doctor.phone,
                'sex': doctor.sex
            }
            return JsonResponse({'status': 'success', 'message': 'Login successful', 'doctor_info': doctor_info})
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect password'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_unverified_users_by_doctor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        doctor_name = data.get('doctor')

        if not doctor_name:
            return JsonResponse({'status': 'error', 'message': 'Doctor name is required'}, status=400)

        unverified_users = UserProfile.objects.filter(doctor=doctor_name, is_verified=False)
        users_info = [
            {
                'id_card': user.id_card,
                'name': user.name,
                'sex': user.sex,
                'birth': user.birth,
                'phone': user.phone,
                'education': user.education,
                'marital_status': user.marital_status,
                'nation': user.nation,
                'occupation': user.occupation,
                'height': user.height,
                'weight': user.weight,
                'waistline': user.waistline,
                'diseases': user.diseases,
                'doctor': user.doctor,
                'is_verified': user.is_verified,
            }
            for user in unverified_users
        ]

        return JsonResponse({'status': 'success', 'users': users_info})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_verified_users_by_doctor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        doctor_name = data.get('doctor')
        page = data.get('page', 1)
        page_size = data.get('page_size', 10)

        if not doctor_name:
            return JsonResponse({'status': 'error', 'message': 'Doctor name is required'}, status=400)

        unverified_users = UserProfile.objects.filter(doctor=doctor_name, is_verified=True)
        paginator = Paginator(unverified_users, page_size)
        try:
            users_page = paginator.page(page)
        except:
            return JsonResponse({'status': 'error', 'message': 'Invalid page number'}, status=400)

        users_info = [
            {
                'id_card': user.id_card,
                'name': user.name,
                'sex': user.sex,
                'birth': user.birth,
                'phone': user.phone,
                'education': user.education,
                'marital_status': user.marital_status,
                'nation': user.nation,
                'occupation': user.occupation,
                'height': user.height,
                'weight': user.weight,
                'waistline': user.waistline,
                'diseases': user.diseases,
                'doctor': user.doctor,
                'is_verified': user.is_verified,
            }
            for user in users_page
        ]

        return JsonResponse({
            'status': 'success',
            'users': users_info,
            'total_pages': paginator.num_pages,
            'current_page': page,
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def verify_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_card = data.get('id_card')
        phone = data.get('phone')
        name = data.get('name')
        doctor = data.get('doctor')

        # Check for missing required fields
        if not id_card or not phone or not name or not doctor:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        try:
            # Get the UserProfile instance
            user = UserProfile.objects.get(id_card=id_card, phone=phone, name=name, doctor=doctor)
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        # Update the is_verified field in UserProfile
        user.is_verified = True
        user.save()

        # Update the is_verified field in PatientPrescription for the same user
        try:
            prescription = PatientPrescription.objects.get(id_card=id_card, phone=phone, name=name, doctor=doctor)
            prescription.is_verified = True
            prescription.save()
        except PatientPrescription.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Prescription record not found'}, status=404)

        # Update the is_verified field in PatientFollowUp for the same user
        try:
            follow_up = PatientFollowUp.objects.get(id_card=id_card, phone=phone, name=name, doctor=doctor)
            follow_up.is_verified = True
            follow_up.save()
        except PatientFollowUp.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Follow-up record not found'}, status=404)

        return JsonResponse({'status': 'success', 'message': 'User, prescription, and follow-ups verified successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_user_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_card = data.get('id_card')
        phone = data.get('phone')

        if not id_card or not phone:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        try:
            user = UserProfile.objects.get(id_card=id_card, phone=phone)
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        user_info = {
            'name': user.name,
            'sex': user.sex,
            'birth': user.birth,
            'phone': user.phone,
            'education': user.education,
            'marital_status': user.marital_status,
            'nation': user.nation,
            'occupation': user.occupation,
            'height': user.height,
            'weight': user.weight,
            'waistline': user.waistline,
        }

        return JsonResponse({'status': 'success', 'user_info': user_info})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_user_names_by_doctor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        doctor_name = data.get('doctor')

        if not doctor_name:
            return JsonResponse({'status': 'error', 'message': 'Doctor name is required'}, status=400)

        users = UserProfile.objects.filter(doctor=doctor_name)
        user_names = [user.name for user in users]

        return JsonResponse({'status': 'success', 'user_names': user_names})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_user_info_by_name_and_doctor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        doctor = data.get('doctor')

        if not name or not doctor:
            return JsonResponse({'status': 'error', 'message': 'Name and doctor are required'}, status=400)

        try:
            user = UserProfile.objects.get(name=name, doctor=doctor)
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        user_info = {
            'name': user.name,
            'id_card': user.id_card,
            'phone': user.phone,
            'doctor': user.doctor,
        }

        return JsonResponse({'status': 'success', 'user_info': user_info})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_wechat_steps(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code')
        encrypted_data = data.get('encryptedData')
        iv = data.get('iv')

        if not code or not encrypted_data or not iv:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        # 获取 session_key
        appid = settings.WECHAT_APPID
        secret = settings.WECHAT_SECRET
        wx_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code"
        response = requests.get(wx_url)
        wx_data = response.json()

        if 'session_key' not in wx_data:
            return JsonResponse({'status': 'error', 'message': 'Failed to get session_key'}, status=400)

        session_key = wx_data['session_key']

        try:
            # 解密微信步数数据
            session_key = base64.b64decode(session_key)
            iv = base64.b64decode(iv)
            encrypted_data = base64.b64decode(encrypted_data)

            cipher = AES.new(session_key, AES.MODE_CBC, iv)
            decrypted_data = cipher.decrypt(encrypted_data)

            # 去除填充字节
            padding_length = decrypted_data[-1]
            decrypted_data = decrypted_data[:-padding_length]

            # 解析 JSON 数据
            decrypted_data = json.loads(decrypted_data.decode('utf-8'))
            step_info_list = decrypted_data.get('stepInfoList', [])

            # 获取当天步数（假设最后一个记录为当天步数）
            if step_info_list:
                today_steps = step_info_list[-1].get('step', 0)
                return JsonResponse({'status': 'success', 'today_steps': today_steps})
            else:
                return JsonResponse({'status': 'error', 'message': 'No step data available'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Decryption failed: {str(e)}'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def get_symptom_doctors(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method, only GET allowed'}, status=400)
    qs = SymptomDoctor.objects.all()
    data = [{"symptom": obj.symptom, "doctor": obj.doctor} for obj in qs]
    return JsonResponse(data, safe=False)