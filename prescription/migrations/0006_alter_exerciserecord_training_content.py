# Generated by Django 4.1 on 2025-02-12 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prescription', '0005_exerciserecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exerciserecord',
            name='training_content',
            field=models.JSONField(verbose_name='训练内容'),
        ),
    ]
