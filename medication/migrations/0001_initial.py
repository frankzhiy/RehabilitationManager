# Generated by Django 4.1 on 2024-11-27 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PatientMedicationRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_card', models.CharField(max_length=20)),
                ('phone', models.CharField(max_length=15)),
                ('doctor', models.CharField(max_length=100)),
                ('name', models.CharField(default='无', max_length=255)),
                ('medicinesName', models.CharField(max_length=255)),
                ('medicinesProfessionalName', models.CharField(blank=True, max_length=255, null=True)),
                ('medicinesFullDateTime', models.DateTimeField()),
            ],
        ),
    ]
