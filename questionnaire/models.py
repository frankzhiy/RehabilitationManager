from django.utils import timezone
from django.db import models

class PatientADL(models.Model):
    hygiene = models.CharField(max_length=255)
    stool = models.CharField(max_length=255)
    urinating = models.CharField(max_length=255)
    bathing = models.CharField(max_length=255)
    dressing = models.CharField(max_length=255)
    feeding = models.CharField(max_length=255)
    stairs = models.CharField(max_length=255)
    toileting = models.CharField(max_length=255)
    transferring = models.CharField(max_length=255)
    walking = models.CharField(max_length=255)
    score = models.IntegerField()
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    uploadTime = models.DateTimeField(default=timezone.now)
    isbydoctor = models.BooleanField(default=False)


class PatientCAT(models.Model):
    chestTightness = models.CharField(max_length=255)
    confidenceLeavingHome = models.CharField(max_length=255)
    cough = models.CharField(max_length=255)
    energyLevels = models.CharField(max_length=255)
    homeActivities = models.CharField(max_length=255)
    phlegm = models.CharField(max_length=255)
    shortnessOfBreath = models.CharField(max_length=255)
    sleepQuality = models.CharField(max_length=255)
    score = models.IntegerField()
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    uploadTime = models.DateTimeField(default=timezone.now)
    isbydoctor = models.BooleanField(default=False)

class PatientmMRC(models.Model):
    degreeOfBreathing = models.CharField(max_length=255)
    score = models.IntegerField()
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    uploadTime = models.DateTimeField(default=timezone.now)
    isbydoctor = models.BooleanField(default=False)

class PatientCCQ(models.Model):
    breathing = models.CharField(max_length=255)
    chestTightness = models.CharField(max_length=255)
    dailyActivities = models.CharField(max_length=255)
    mentalHealth = models.CharField(max_length=255)
    morningSymptoms = models.CharField(max_length=255)
    phlegm = models.CharField(max_length=255)
    score = models.IntegerField()
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    uploadTime = models.DateTimeField(default=timezone.now)
    isbydoctor = models.BooleanField(default=False)

class PatientADLWarn(models.Model):
    hygiene = models.CharField(max_length=255)
    stool = models.CharField(max_length=255)
    urinating = models.CharField(max_length=255)
    bathing = models.CharField(max_length=255)
    dressing = models.CharField(max_length=255)
    feeding = models.CharField(max_length=255)
    stairs = models.CharField(max_length=255)
    toileting = models.CharField(max_length=255)
    transferring = models.CharField(max_length=255)
    walking = models.CharField(max_length=255)
    score = models.IntegerField()
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    uploadTime = models.DateTimeField(default=timezone.now)
    isbydoctor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    finishedFollowup = models.BooleanField(default=False)
    barthel_index = models.CharField(default='完全自理', max_length=100, verbose_name="Barthel指数")


class PatientCATWarn(models.Model):
    chestTightness = models.CharField(max_length=255)
    confidenceLeavingHome = models.CharField(max_length=255)
    cough = models.CharField(max_length=255)
    energyLevels = models.CharField(max_length=255)
    homeActivities = models.CharField(max_length=255)
    phlegm = models.CharField(max_length=255)
    shortnessOfBreath = models.CharField(max_length=255)
    sleepQuality = models.CharField(max_length=255)
    score = models.IntegerField()
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    uploadTime = models.DateTimeField(default=timezone.now)
    isbydoctor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    finishedFollowup = models.BooleanField(default=False)
    cat_index = models.CharField(max_length=100, verbose_name="CAT指数")  #


class PatientmMRCWarn(models.Model):
    degreeOfBreathing = models.CharField(max_length=255)
    score = models.IntegerField()
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    uploadTime = models.DateTimeField(default=timezone.now)
    isbydoctor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    finishedFollowup = models.BooleanField(default=False)
    mmrc_index = models.CharField(max_length=100, verbose_name="mMRC指数")  # 新增字段

    def __str__(self):
        return f"{self.name} - {self.mmrc_index}"

class PatientCCQWarn(models.Model):
    breathing = models.CharField(max_length=255)
    chestTightness = models.CharField(max_length=255)
    dailyActivities = models.CharField(max_length=255)
    mentalHealth = models.CharField(max_length=255)
    morningSymptoms = models.CharField(max_length=255)
    phlegm = models.CharField(max_length=255)
    score = models.IntegerField()
    doctor = models.CharField(max_length=100)
    id_card = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    uploadTime = models.DateTimeField(default=timezone.now)
    isbydoctor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    finishedFollowup = models.BooleanField(default=False)
    ccq_index = models.CharField(max_length=100, verbose_name="CCQ指数")  # 新增字段

    def __str__(self):
        return f"{self.name} - {self.ccq_index}"