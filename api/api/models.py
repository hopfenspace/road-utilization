from django.db.models import Model, CharField, IntegerField, FloatField, DateTimeField


class RawData(Model):
    device_id = CharField(default="", max_length=255)
    count_car = IntegerField(default=0)
    count_truck = IntegerField(default=0)
    battery = FloatField(default=0)
    timestamp = DateTimeField()
    rssi = IntegerField(default=0)
