from django.urls import re_path
from .consumers import DiagnosisLLMConsumer

websocket_urlpatterns = [
    re_path(r'ws/diagnosis/$', DiagnosisLLMConsumer.as_asgi()),
]
