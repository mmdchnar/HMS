# Generated by Django 4.1.7 on 2023-05-08 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_patient_national_id_patient_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='bed',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='manager.bed'),
        ),
    ]
