# Generated by Django 5.2 on 2025-04-21 18:18

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PatientDiscomfortRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("id_card", models.CharField(max_length=18)),
                ("phone", models.CharField(max_length=15)),
                ("doctor", models.CharField(max_length=255)),
                ("name", models.CharField(default="无", max_length=255)),
                ("comfort", models.BooleanField(default=False)),
                ("appetiteLoss", models.BooleanField(default=False)),
                ("breathing", models.BooleanField(default=False)),
                ("breathingWorsened", models.BooleanField(default=False)),
                ("cough", models.BooleanField(default=False)),
                ("coughWorsened", models.BooleanField(default=False)),
                ("fastHeartbeat", models.BooleanField(default=False)),
                ("fatigue", models.BooleanField(default=False)),
                ("fever", models.BooleanField(default=False)),
                ("sleepPatternChange", models.BooleanField(default=False)),
                ("sputum", models.BooleanField(default=False)),
                ("sputumIncreased", models.BooleanField(default=False)),
                ("swollenLegs", models.BooleanField(default=False)),
                ("weightLoss", models.BooleanField(default=False)),
                ("datetime", models.DateTimeField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="PatientDiscomfortRecordWarn",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("id_card", models.CharField(max_length=18)),
                ("phone", models.CharField(max_length=15)),
                ("doctor", models.CharField(max_length=255)),
                ("name", models.CharField(default="无", max_length=255)),
                ("comfort", models.BooleanField(default=False)),
                ("appetiteLoss", models.BooleanField(default=False)),
                ("breathing", models.BooleanField(default=False)),
                ("breathingWorsened", models.BooleanField(default=False)),
                ("cough", models.BooleanField(default=False)),
                ("coughWorsened", models.BooleanField(default=False)),
                ("fastHeartbeat", models.BooleanField(default=False)),
                ("fatigue", models.BooleanField(default=False)),
                ("fever", models.BooleanField(default=False)),
                ("sleepPatternChange", models.BooleanField(default=False)),
                ("sputum", models.BooleanField(default=False)),
                ("sputumIncreased", models.BooleanField(default=False)),
                ("swollenLegs", models.BooleanField(default=False)),
                ("weightLoss", models.BooleanField(default=False)),
                ("datetime", models.DateTimeField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("finishedFollowup", models.BooleanField(default=False)),
                (
                    "alert_type",
                    models.CharField(default="", max_length=255, verbose_name="预警类型"),
                ),
            ],
        ),
    ]
