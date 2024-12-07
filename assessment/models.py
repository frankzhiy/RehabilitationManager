# from django.db import models
#
# class AssessmentRecord(models.Model):
#     # 固定字段
#     doctor = models.CharField(max_length=100)
#     id_card = models.CharField(max_length=20)
#     name = models.CharField(max_length=100)
#     phone = models.CharField(max_length=15)
#     isUploadByDoctor = models.BooleanField(default=True)
#
#     # 可选字段及其对应的 upload_time
#     swallowStatus = models.CharField(max_length=100, null=True, blank=True)
#     swallowStatusUploadTime = models.DateTimeField(null=True, blank=True)
#
#     MEP = models.FloatField(null=True, blank=True)
#     MEPUploadTime = models.DateTimeField(null=True, blank=True)
#
#     MIP = models.FloatField(null=True, blank=True)
#     MIPUploadTime = models.DateTimeField(null=True, blank=True)
#
#     limbStatus = models.CharField(max_length=100, null=True, blank=True)
#     limbStatusUploadTime = models.DateTimeField(null=True, blank=True)
#
#     PEF = models.FloatField(null=True, blank=True)
#     PEFUploadTime = models.DateTimeField(null=True, blank=True)
#
#     TCE = models.FloatField(null=True, blank=True)
#     TCEUploadTime = models.DateTimeField(null=True, blank=True)
#
#     MWT = models.FloatField(null=True, blank=True)
#     MWTUploadTime = models.DateTimeField(null=True, blank=True)
#
#     STEP = models.IntegerField(null=True, blank=True)
#     STEPUploadTime = models.DateTimeField(null=True, blank=True)
#
#     def __str__(self):
#         return f'{self.name} ({self.id_card})'
#
#     class Meta:
#         unique_together = ('doctor', 'id_card', 'name', 'phone', 'isUploadByDoctor')


from django.db import models

class RespiratoryAssessment(models.Model):
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    isUploadByDoctor = models.BooleanField(default=True)
    MEP = models.FloatField(null=True, blank=True)
    MIP = models.FloatField(null=True, blank=True)
    RespiratoryUploadTime = models.DateTimeField(null=True, blank=True)

class TCEAssessment(models.Model):
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    isUploadByDoctor = models.BooleanField(default=True)

    TCE = models.FloatField(null=True, blank=True)
    TCEUploadTime = models.DateTimeField(null=True, blank=True)

class StepAssessment(models.Model):
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    isUploadByDoctor = models.BooleanField(default=True)
    MWT = models.FloatField(null=True, blank=True)
    STEP = models.IntegerField(null=True, blank=True)
    STEPUploadTime = models.DateTimeField(null=True, blank=True)

class SwallowAssessment(models.Model):
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    isUploadByDoctor = models.BooleanField(default=True)
    swallowStatus = models.CharField(max_length=100, null=True, blank=True)
    swallowStatusUploadTime = models.DateTimeField(null=True, blank=True)

class LimbAssessment(models.Model):
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    isUploadByDoctor = models.BooleanField(default=True)
    limbStatus = models.CharField(max_length=100, null=True, blank=True)
    limbStatusUploadTime = models.DateTimeField(null=True, blank=True)

class PEFAssessment(models.Model):
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    isUploadByDoctor = models.BooleanField(default=True)

    PEF = models.FloatField(null=True, blank=True)
    PEFUploadTime = models.DateTimeField(null=True, blank=True)
