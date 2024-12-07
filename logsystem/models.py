from django.db import models

class LogEntry(models.Model):
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO')
    message = models.TextField()  # 日志内容
    module = models.CharField(max_length=255, null=True, blank=True)  # 触发日志的模块或视图
    method = models.CharField(max_length=10, null=True, blank=True)  # HTTP 方法
    path = models.CharField(max_length=255, null=True, blank=True)  # 请求路径
    user = models.CharField(max_length=255, null=True, blank=True)  # 用户标识
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # IP 地址
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return f"[{self.level}] {self.message[:50]}"

