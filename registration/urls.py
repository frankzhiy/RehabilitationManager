from django.urls import path
from .views import register, login, register_doctor, login_doctor, get_unverified_users_by_doctor, verify_user, get_verified_users_by_doctor,get_user_info,get_user_names_by_doctor,get_user_info_by_name_and_doctor

urlpatterns = [
    path('register/', register, name='register'),  # 处理注册请求的 URL
    path('login/', login, name='login'),  # 处理登录请求的 URL
    path('register_doctor/', register_doctor, name='register-doctor'),
    path('login_doctor/', login_doctor, name='login-doctor'),
    path('get_unverified_users_by_doctor/', get_unverified_users_by_doctor, name='get_unverified_users_by_doctor'),
    path('get_verified_users_by_doctor/', get_verified_users_by_doctor, name='get_verified_users_by_doctor'),
    path('verify_user/', verify_user, name='verify_user'),
    path('get_user_info/', get_user_info, name='get_user_info'),
    path('get_user_names_by_doctor/', get_user_names_by_doctor, name='get_user_names_by_doctor'),
    path('get_user_info_by_name_and_doctor/', get_user_info_by_name_and_doctor, name='get_user_info_by_name_and_doctor')
]
