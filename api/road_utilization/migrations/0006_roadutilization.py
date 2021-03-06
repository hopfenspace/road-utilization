# Generated by Django 3.1.3 on 2020-11-26 01:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('road_utilization', '0005_auto_20201126_0136'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoadUtilization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_data', models.ManyToManyField(to='road_utilization.RawData')),
                ('road_stretch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='road_utilization.roadstretch')),
            ],
        ),
    ]
