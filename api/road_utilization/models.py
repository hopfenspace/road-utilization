from django.db.models import Model, CharField, IntegerField, FloatField, DateTimeField, ForeignKey, CASCADE, \
    ManyToManyField


class Device(Model):
    device_id = CharField(default="", max_length=255)

    def __str__(self):
        return self.device_id


class Coordinate(Model):
    lat = FloatField(default=0)
    lon = FloatField(default=0)


class KeyValuePair(Model):
    key = IntegerField(default=0)
    value = IntegerField(default=0)


class RawData(Model):
    device = ForeignKey(Device, on_delete=CASCADE)
    data = ManyToManyField(KeyValuePair)
    battery = FloatField(default=0)
    timestamp = DateTimeField()
    rssi = IntegerField(default=0)


class RoadType(Model):
    highway_type = CharField(default="", max_length=255)

    def __str__(self):
        return self.highway_type


class RoadStretch(Model):
    osm_id = CharField(default="", max_length=255, unique=True)
    road_type = ForeignKey(RoadType, on_delete=CASCADE)
    coordinates = ManyToManyField(Coordinate)

    def __str__(self):
        return self.osm_id


class SensorPosition(Model):
    device = ForeignKey(Device, on_delete=CASCADE)
    coordinate = ForeignKey(Coordinate, on_delete=CASCADE, null=True)
    road_stretch = ForeignKey(RoadStretch, on_delete=CASCADE, null=True)


class Road(Model):
    name = CharField(default="", max_length=255)
    road_stretches = ManyToManyField(RoadStretch)

    def __str__(self):
        return self.name


class RoadUtilization(Model):
    road_stretch = ForeignKey(RoadStretch, on_delete=CASCADE)
    raw_data = ManyToManyField(RawData)
    count_cars = IntegerField(default=0)
    count_trucks = IntegerField(default=0)


class CycleMapping(Model):
    cycle_time = IntegerField(default=0, unique=True)
    mapping = CharField(default="other", choices=[("car", "car"), ("truck", "truck"), ("other", "other")], max_length=255)
