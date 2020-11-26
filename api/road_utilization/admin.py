from django.contrib import admin

from road_utilization.models import *

admin.site.register(Device)
admin.site.register(SensorPosition)
admin.site.register(RawData)
admin.site.register(RoadType)
admin.site.register(Coordinate)
admin.site.register(RoadStretch)
admin.site.register(Road)
admin.site.register(RoadUtilization)
