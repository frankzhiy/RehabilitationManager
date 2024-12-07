from django.db import models

class PatientPEFRecord(models.Model):
    id_card = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    doctor = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    pefValue = models.FloatField()
    dateText = models.CharField(max_length=100)
    currentTime = models.DateTimeField()

    def __str__(self):
        return f'{self.name} - PEF: {self.pefValue}'

class PatientBestPEFRecord(models.Model):
    id_card = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    doctor = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    bestpefInput = models.FloatField()
    currentTime = models.DateTimeField()

    def __str__(self):
        return f'{self.name} - Best PEF: {self.bestpefInput}'