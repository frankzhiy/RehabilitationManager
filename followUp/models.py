from django.db import models

class FollowUp(models.Model):
    name = models.CharField(max_length=255)
    id_card = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    doctor = models.CharField(max_length=255, default='无')
    followUpEffectiveness = models.CharField(max_length=255)
    ineffectivenessReason = models.CharField(max_length=255)
    qualityOfLife = models.CharField(max_length=255)
    physicalCondition = models.CharField(max_length=255)
    psychologicalCondition = models.CharField(max_length=255)
    medicationAdherence = models.CharField(max_length=255)
    exacerbations = models.CharField(max_length=255)
    acuteExacerbations = models.CharField(max_length=255)
    newDiscomfort = models.CharField(max_length=255)
    newSymptoms = models.CharField(max_length=255)
    followUpReason = models.CharField(max_length=255)
    reasonDetail = models.TextField()
    followUpTime = models.DateTimeField()

    def __str__(self):
        return self.name