from django.db import models

class User(models.Model):
    username = models.CharField(max_length=200, blank=False, null=False)
    password = models.CharField(max_length=200, blank=False, null=False)
    authorities = models.CharField(max_length=200, blank=True, null=True, verbose_name='权限', help_text='权限')
    tel = models.CharField(max_length=200, blank=True, null=True, verbose_name='电话号码', help_text='电话号码')
    email = models.CharField(max_length=200, blank=True, null=True, verbose_name='邮箱', help_text='邮箱')
    desc = models.CharField(max_length=200, blank=True, null=True, verbose_name='描述', help_text='描述')

    def __str__(self):
        return self.username