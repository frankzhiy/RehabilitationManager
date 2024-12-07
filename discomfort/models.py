# discomfort/models.py

from django.db import models

class PatientDiscomfortRecord(models.Model):
    id_card = models.CharField(max_length=18)
    phone = models.CharField(max_length=15)
    doctor = models.CharField(max_length=255)
    name = models.CharField(max_length=255, default='无')
    comfort = models.BooleanField(default=False)
    appetiteLoss = models.BooleanField(default=False)
    breathing = models.BooleanField(default=False)
    breathingWorsened = models.BooleanField(default=False)
    cough = models.BooleanField(default=False)
    coughWorsened = models.BooleanField(default=False)
    fastHeartbeat = models.BooleanField(default=False)
    fatigue = models.BooleanField(default=False)
    fever = models.BooleanField(default=False)
    sleepPatternChange = models.BooleanField(default=False)
    sputum = models.BooleanField(default=False)
    sputumIncreased = models.BooleanField(default=False)
    swollenLegs = models.BooleanField(default=False)
    weightLoss = models.BooleanField(default=False)
    datetime = models.DateTimeField(default=False)
    def __str__(self):
        return f"{self.id_card} - {self.doctor}"

class PatientDiscomfortRecordWarn(models.Model):
    id_card = models.CharField(max_length=18)
    phone = models.CharField(max_length=15)
    doctor = models.CharField(max_length=255)
    name = models.CharField(max_length=255, default='无')
    comfort = models.BooleanField(default=False)
    appetiteLoss = models.BooleanField(default=False)
    breathing = models.BooleanField(default=False)
    breathingWorsened = models.BooleanField(default=False)
    cough = models.BooleanField(default=False)
    coughWorsened = models.BooleanField(default=False)
    fastHeartbeat = models.BooleanField(default=False)
    fatigue = models.BooleanField(default=False)
    fever = models.BooleanField(default=False)
    sleepPatternChange = models.BooleanField(default=False)
    sputum = models.BooleanField(default=False)
    sputumIncreased = models.BooleanField(default=False)
    swollenLegs = models.BooleanField(default=False)
    weightLoss = models.BooleanField(default=False)
    datetime = models.DateTimeField(default=False)
    is_active = models.BooleanField(default=True)
    finishedFollowup = models.BooleanField(default=False)
    alert_type = models.CharField(max_length=255, verbose_name="预警类型", default='')  # 新增字段

    def __str__(self):
        return f"{self.id_card} - {self.doctor}"
