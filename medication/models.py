from django.db import models

class PatientMedicationRecord(models.Model):
    id_card = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    doctor = models.CharField(max_length=100)
    name = models.CharField(max_length=255, default='无')
    medicinesName = models.CharField(max_length=255)
    medicinesProfessionalName = models.CharField(max_length=255, blank=True, null=True)
    medicinesFullDateTime = models.DateTimeField()

    def __str__(self):
        return f'{self.medicinesName} - {self.id_card}'
