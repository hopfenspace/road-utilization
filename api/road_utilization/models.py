from django.db.models import Model, CharField, IntegerField, FloatField, DateTimeField, ForeignKey, CASCADE, \
    ManyToManyField


class Device(Model):
    device_id = CharField(default="", max_length=255)

    def __str__(self):
        return self.device_id


class Coordinate(Model):
    lat = FloatField(default=0)
    lon = FloatField(default=0)


class SensorPosition(Model):
    device = ForeignKey(Device, on_delete=CASCADE)
    coordinate = ForeignKey(Coordinate, on_delete=CASCADE)


class RawData(Model):
    device = ForeignKey(Device, on_delete=CASCADE)
    count_car = IntegerField(default=0)
    count_truck = IntegerField(default=0)
    battery = FloatField(default=0)
    timestamp = DateTimeField()
    rssi = IntegerField(default=0)


class RoadType(Model):
    highway_type = CharField(default="", max_length=255)

    def __str__(self):
        return self.highway_type


class RoadStretch(Model):
    osm_id = CharField(default="", max_length=255)
    road_type = ForeignKey(RoadType, on_delete=CASCADE)
    coordinates = ManyToManyField(Coordinate)

    def __str__(self):
        return self.osm_id


class Road(Model):
    name = CharField(default="", max_length=255)
    road_stretches = ManyToManyField(RoadStretch)

    def __str__(self):
        return self.name
