"""
ASGI config for RehabilitationManager project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import diagnosisLLM.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RehabilitationManager.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        diagnosisLLM.routing.websocket_urlpatterns
    ),
})  # 确保字典闭合

# 提示：请使用 daphne 或 uvicorn 启动 ASGI 服务器，
# 例如： daphne -p 8000 RehabilitationManager.asgi:application
