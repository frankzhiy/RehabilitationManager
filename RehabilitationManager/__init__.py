# __init__.py

# 这确保 app 在 Django 启动时被加载
from .celery import app as celery_app

__all__ = ('celery_app',)