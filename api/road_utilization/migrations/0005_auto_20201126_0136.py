# Generated by Django 3.1.3 on 2020-11-26 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('road_utilization', '0004_sensorposition_road_stretch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roadstretch',
            name='osm_id',
            field=models.CharField(default='', max_length=255, unique=True),
        ),
    ]
