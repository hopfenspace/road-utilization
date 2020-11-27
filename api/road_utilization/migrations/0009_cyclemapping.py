# Generated by Django 3.1.3 on 2020-11-27 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('road_utilization', '0008_auto_20201127_2159'),
    ]

    operations = [
        migrations.CreateModel(
            name='CycleMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cycle_time', models.IntegerField(default=0)),
                ('mapping', models.CharField(choices=[('car', 'car'), ('truck', 'truck'), ('other', 'other')], default='other', max_length=255)),
            ],
        ),
    ]
