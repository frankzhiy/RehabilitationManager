# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置 Django 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RehabilitationManager.settings')

app = Celery('RehabilitationManager')

# 从 Django 的 settings.py 中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()