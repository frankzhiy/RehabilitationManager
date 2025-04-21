from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),  # 处理注册请求的 URL
    path('login/', views.login, name='login'),  # 处理登录请求的 URL
    path('register_doctor/', views.register_doctor, name='register-doctor'),
    path('login_doctor/', views.login_doctor, name='login-doctor'),
    path('get_unverified_users_by_doctor/', views.get_unverified_users_by_doctor, name='get_unverified_users_by_doctor'),
    path('get_verified_users_by_doctor/', views.get_verified_users_by_doctor, name='get_verified_users_by_doctor'),
    path('verify_user/', views.verify_user, name='verify_user'),
    path('get_user_info/', views.get_user_info, name='get_user_info'),
    path('get_user_names_by_doctor/', views.get_user_names_by_doctor, name='get_user_names_by_doctor'),
    path('get_user_info_by_name_and_doctor/', views.get_user_info_by_name_and_doctor, name='get_user_info_by_name_and_doctor'),
    path('get_wechat_steps/', views.get_wechat_steps, name='get_wechat_steps'),
    path('get_symptom_doctors/', views.get_symptom_doctors, name='get_symptom_doctors')
]
