# Generated by Django 3.1.3 on 2020-11-26 00:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('road_utilization', '0003_auto_20201125_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensorposition',
            name='road_stretch',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='road_utilization.roadstretch'),
            preserve_default=False,
        ),
    ]