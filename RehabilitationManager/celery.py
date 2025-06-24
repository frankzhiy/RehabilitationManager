# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置 Django 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RehabilitationManager.settings')

app = Celery('RehabilitationManager')

# 使用字符串命名空间，这样不用担心设置名称与其他模块的设置冲突
app.config_from_object('django.conf:settings', namespace='CELERY')

# 加载所有已注册app中的任务模块
app.autodiscover_tasks()

# 配置结果后端
app.conf.result_backend = 'redis://localhost:6379/0'
# 或使用数据库后端
# app.conf.result_backend = 'db+sqlite:///celery-results.sqlite'

# 任务序列化格式
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# 任务超时设置
app.conf.task_time_limit = 300  # 5分钟超时
app.conf.task_soft_time_limit = 240  # 4分钟软超时

# 设置任务结果过期时间
app.conf.result_expires = 3600  # 1小时

# 确保日志输出
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')
    return 'Debug task completed'