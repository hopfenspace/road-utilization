import json

from django.http import HttpResponse
from django.views.generic.base import View

from api import scripts
from road_utilization.models import RawData


class ImportRoads(View):
    def get(self, request, *args, **kwargs):
        scripts.import_roads()
        return HttpResponse("OK", status=200)


class PutView(View):

    def post(self, request):
        data = json.loads(request.body)
        obj = RawData()
        obj.device_id = data["dev_id"]
        obj.rssi = data["metadata"]["rssi"]
        obj.timestamp = data["metadata"]["timestamp"]
        obj.count_car = data["payload_fields"]["count_car"]
        obj.count_truck = data["payload_fields"]["count_truck"]
        obj.battery = data["payload_fields"]["battery"]
        obj.save()
        return HttpResponse("OK", status=200)
