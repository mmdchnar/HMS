# Generated by Django 4.1.7 on 2023-05-08 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0007_alter_bed_floor_alter_patient_bed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='bed',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.bed'),
        ),
    ]
