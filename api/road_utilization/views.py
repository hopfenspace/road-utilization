import json
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.views.generic.base import View

from api import scripts
from road_utilization.models import RawData, Device, RoadStretch, RoadUtilization


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


class GetRoadUtilization(View):
    def get(self, request, *args, **kwargs):
        data = {
            "success": True,
            "result": {}
        }
        road_stretch_object = None
        limit = None
        if "road_stretch" in request.GET:
            osm_id = request.GET["road_stretch"]
            try:
                road_stretch_object = RoadStretch.objects.get(osm_id=osm_id)
            except RoadStretch.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "result": f"RoadStretch was not found with osm_id {osm_id}"
                }, status=400)
        if "limit" in request.GET:
            try:
                limit = int(request.GET["limit"])
                if limit <= 0:
                    raise ValueError
            except ValueError:
                return JsonResponse({"success": False, "result": "Limit is no positive int"}, status=400)

        road_stretches = [x.osm_id for x in RoadStretch.objects.all()] if not road_stretch_object else [road_stretch_object]
        for road_stretch in road_stretches:
            try:
                raw_data_list = RoadUtilization.objects.get(road_stretch__osm_id=road_stretch).raw_data.all() if not limit \
            else RoadUtilization.objects.get(road_stretch__osm_id=road_stretch).raw_data.all().order_by("-id")[:limit]
                data["result"][road_stretch.osm_id] = {
                   "count_car": sum([x.count_car for x in raw_data_list]),
                   "count_truck": sum([x.count_truck for x in raw_data_list])
                }
            except RoadUtilization.DoesNotExist:
                data["result"][road_stretch.osm_id] = {
                    "count_car": 0,
                    "count_truck": 0
                }
        return JsonResponse(data, safe=False)


class GetRoads(View):
    def get(self, request, *args, **kwargs):
        data = {
            "success": True,
            "result": {}
        }
        road_stretch_objects = RoadStretch.objects.all()
        for road_stretch in road_stretch_objects:
            data["result"][road_stretch.osm_id] = {
                "coordinates": [{"lat": x.lat, "long": x.lon} for x in road_stretch.coordinates.all()]
            }
        return JsonResponse(data, safe=False)
