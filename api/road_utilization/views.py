import json

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

        raw_data = RawData(
            rssi=data["metadata"]["gateways"][0]["rssi"],
            timestamp=data["metadata"]["timestamp"],
            count_car=data["payload_fields"]["count_car"],
            count_truck=data["payload_fields"]["count_truck"],
            battery=data["payload_fields"]["battery"],
            device=device
        )
        raw_data.save()
        
        return HttpResponse("OK", status=200)
