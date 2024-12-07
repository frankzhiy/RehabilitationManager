# tasks.py

from celery import shared_task
from django.utils import timezone
import datetime
from registration.models import PatientFollowUp

@shared_task
def reset_patient_followup_status():
    now = timezone.now()
    fourteen_days_ago = now - datetime.timedelta(days=14)
    thirty_days_ago = now - datetime.timedelta(days=30)

    # 处理 followUpTime 超过14天的记录
    followups = PatientFollowUp.objects.filter(followUpTime__isnull=False, followUpTime__lte=fourteen_days_ago)
    for followup in followups:
        # followup.followUpTime = None
        followup.isFinished = False
        followup.save()

    # 处理 deactivateTime 超过14天的记录
    deactivates = PatientFollowUp.objects.filter(deactivateTime__isnull=False, deactivateTime__lte=fourteen_days_ago)
    for deactivate in deactivates:
        deactivate.deactivateTime = None
        deactivate.isActive = True
        deactivate.save()

    # 处理 endedTime 超过30天的记录
    endeds = PatientFollowUp.objects.filter(endedTime__isnull=False, endedTime__lte=thirty_days_ago)
    for ended in endeds:
        ended.endedTime = None
        ended.isEnded = False  # 应设置为 True
        ended.save()