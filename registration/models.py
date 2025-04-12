import datetime

from django.db import models

class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    id_card = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10)
    birth = models.DateField()
    phone = models.CharField(max_length=15)
    education = models.CharField(max_length=50)
    marital_status = models.CharField(max_length=20)
    nation = models.CharField(max_length=50)
    occupation = models.CharField(max_length=50)
    height = models.FloatField()
    weight = models.FloatField()
    waistline = models.FloatField()
    diseases = models.CharField(max_length=255 , default='none')
    doctor = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    is_verified = models.BooleanField(default=False)  # 审核状态
    has_prescription = models.BooleanField(default=False)  # 是否有处方
    openid = models.CharField(max_length=50, unique=True, null=True, blank=True, default=None)
    unionid = models.CharField(max_length=50, unique=True, null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DoctorProfile(models.Model):
    IDcard = models.CharField(max_length=18, unique=True)
    hospital = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=15)
    sex = models.CharField(max_length=10 , default='男')

    def __str__(self):
        return self.name



class PatientPrescription(models.Model):
    swallowStatusPrescription = models.JSONField(default=list, blank=True, null=True)
    MepAndMipPrescription = models.JSONField(default=list, blank=True, null=True)
    limbStatusPrescription = models.JSONField(default=list, blank=True, null=True)
    PEFPrescription = models.JSONField(default=list, blank=True, null=True)
    TCEPrescription = models.JSONField(default=list, blank=True, null=True)
    MwtAndStepPrescription = models.JSONField(default=list, blank=True, null=True)
    doctor = models.CharField(max_length=255)
    id_card = models.CharField(max_length=18)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    uploadtime = models.DateTimeField(auto_now_add=True)
    isActive = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # 审核状态
    sex = models.CharField(max_length=10,default=None)
    birth = models.DateField(default=datetime.date(1960, 1, 1))
    height = models.FloatField(default=None)
    weight = models.FloatField(default=None)
    waistline = models.FloatField(default=None)
    diseases = models.CharField(max_length=255, default='none')
    def __str__(self):
        return f"{self.name} - {self.id_card} Prescription"

class PatientFollowUp(models.Model):
    doctor = models.CharField(max_length=255)
    id_card = models.CharField(max_length=18)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    sex = models.CharField(max_length=10,default=None)
    birth = models.DateField(default=datetime.date(1960, 1, 1))
    height = models.FloatField(default=None)
    weight = models.FloatField(default=None)
    waistline = models.FloatField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    followUpTime = models.DateTimeField(default=None , null=True)
    isActive = models.BooleanField(default=True)
    isFinished = models.BooleanField(default=False)
    deactivateTime = models.DateTimeField(default=None, null=True)
    isEnded = models.BooleanField(default=False)
    endedTime = models.DateTimeField(default=None, null=True)
    is_verified = models.BooleanField(default=False)
    diseases = models.CharField(max_length=255, default='none')
    followTimes = models.IntegerField(default=0)
    followUpType = models.CharField(max_length=255, default='普通随访')
    def __str__(self):
        return f"{self.name} - {self.id_card} Follow-Up"