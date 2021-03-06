# Generated by Django 3.1.3 on 2020-11-25 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('road_utilization', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='road',
            name='coordinates',
        ),
        migrations.RemoveField(
            model_name='road',
            name='osm_id',
        ),
        migrations.RemoveField(
            model_name='road',
            name='road_type',
        ),
        migrations.CreateModel(
            name='RoadStretch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('osm_id', models.CharField(default='', max_length=255)),
                ('coordinates', models.ManyToManyField(to='road_utilization.Coordinate')),
                ('road_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='road_utilization.roadtype')),
            ],
        ),
        migrations.AddField(
            model_name='road',
            name='road_stretches',
            field=models.ManyToManyField(to='road_utilization.RoadStretch'),
        ),
    ]
