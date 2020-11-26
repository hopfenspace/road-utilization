import json
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.views.generic.base import View

from api import scripts
from road_utilization.models import RawData, Device, RoadStretch


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


class RoadUtilization(View):
    def get(self, request, *args, **kwargs):
        data = {
            "success": True,
            "result": {}
        }
        if "road_stretch" not in request.GET:
            return JsonResponse({"success": False, "result": "Please specify the parameter road_stretch"}, status=400)
        osm_id = request.GET["road_stretch"]
        try:
            road_stretch_object = RoadStretch.objects.get(osm_id=osm_id)
            data["result"]["osm_id"] = road_stretch_object.osm_id
            data["result"]["coordinates"] = []
            for coordinate in road_stretch_object.coordinates.all():
                data["result"]["coordinates"].append({
                    "lat": coordinate.lat,
                    "long": coordinate.lon
                })
            data["result"]["road_type"] = road_stretch_object.road_type.highway_type
        except RoadStretch.DoesNotExist:
            return JsonResponse({"success": False, "result": f"RoadStretch was not found with osm_id {osm_id}"},
                                status=400)
        return JsonResponse(data, safe=False)
