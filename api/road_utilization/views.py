import json
from datetime import datetime

from django.http import HttpResponse
from django.views.generic.base import View

from api import scripts
from road_utilization.models import RawData, Device


class ImportRoads(View):
    def get(self, request, *args, **kwargs):
        scripts.import_roads()
        return HttpResponse("OK", status=200)


class PutView(View):

    def post(self, request):
        data = json.loads(request.body)
        device, created = Device.objects.get_or_create(device_id=data["dev_id"])
        if created:
            device.save()

        datetime_string = data["metadata"]["time"]
        datetime_string = datetime_string.split('.')[0]
        time = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
        raw_data = RawData(
            rssi=data["metadata"]["gateways"][0]["rssi"],
            timestamp=time,
            count_car=data["payload_fields"]["count_car"],
            count_truck=data["payload_fields"]["count_truck"],
            battery=data["payload_fields"]["battery"],
            device=device
        )
        raw_data.save()

        return HttpResponse("OK", status=200)
