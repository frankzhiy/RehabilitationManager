# Generated by Django 5.2 on 2025-04-21 18:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SymptomDoctor",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("symptom", models.CharField(max_length=255, verbose_name="症状")),
                ("doctor", models.CharField(max_length=100, verbose_name="医生")),
                ("notes", models.TextField(blank=True, null=True, verbose_name="备注")),
            ],
        ),
    ]
