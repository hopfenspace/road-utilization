import json
from datetime import datetime, tzinfo, timezone

from django.http import HttpResponse, JsonResponse
from django.views.generic.base import View

from api import scripts
from road_utilization.models import RawData, Device, RoadStretch, RoadUtilization, SensorPosition, KeyValuePair, \
    CycleMapping


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
            battery=data["payload_fields"]["battery"],
            device=device
        )
        for measurement in data["payload_fields"]["vehicles"]:
            kvp = KeyValuePair(
                key=int(measurement),
                value=int(data["payload_fields"]["vehicles"][measurement])
            )
            kvp.save()
            raw_data.data.add(kvp)
        raw_data.save()

        try:
            sensor_position = SensorPosition.objects.get(device__device_id=data["dev_id"])
            road_utilization, _ = RoadUtilization.objects.get_or_create(
                road_stretch=sensor_position.road_stretch,
            )
            road_utilization.raw_data.add(raw_data)
            road_utilization.save()
        except SensorPosition.DoesNotExist or RoadUtilization.DoesNotExist:
            pass

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

        road_stretches = [x.osm_id for x in RoadStretch.objects.all()] if not road_stretch_object else [road_stretch_object.osm_id]
        for road_stretch in road_stretches:
            try:
                raw_data_list = RoadUtilization.objects.get(road_stretch__osm_id=road_stretch).raw_data.all() if not limit \
            else RoadUtilization.objects.get(road_stretch__osm_id=road_stretch).raw_data.all().order_by("-id")[:limit]
                count_car = 0
                count_truck = 0
                for raw_data in raw_data_list:
                    count_car += sum([y.value for y in raw_data.data.all() if y.key in [x.cycle_time for x in CycleMapping.objects.filter(mapping="car")]])
                    count_truck += sum([y.value for y in raw_data.data.all() if y.key in [x.cycle_time for x in CycleMapping.objects.filter(mapping="truck")]])
                data["result"][road_stretch] = {
                   "count_car": count_car,
                   "count_truck": count_truck,
                }
            except RoadUtilization.DoesNotExist:
                data["result"][road_stretch] = {
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


class GetSensorPositions(View):
    def get(self, request, *args, **kwargs):
        data = {
            "success": True,
            "result": {}
        }
        sensor_positions = SensorPosition.objects.all()
        for sensor_position in sensor_positions:
            data["result"][sensor_position.device.device_id] = {
                "coordinates": {
                    "lat": sensor_position.coordinate.lat,
                    "long": sensor_position.coordinate.lon
                },
                "linked_road_stretch": sensor_position.road_stretch.osm_id
            }
        return JsonResponse(data, safe=False)


class GetRoadUtilizationHistory(View):
    def get(self, request, *args, **kwargs):
        data = {
            "success": True,
            "result": {}
        }
        to_timestamp = None
        from_timestamp = None
        if "road_stretch" not in request.GET:
            return JsonResponse({"success": False, "result": "Missing parameter: road_stretch"}, status=400)
        else:
            try:
                print(request.GET["road_stretch"])
                road_utilization = RoadUtilization.objects.get(road_stretch__osm_id=request.GET["road_stretch"])
                raw_data = road_utilization.raw_data.all()
                if "to" in request.GET:
                    try:
                        to_timestamp = datetime.fromtimestamp(int(request.GET["to"]), timezone.utc)
                    except ValueError:
                        return JsonResponse({"success": False, "result": "To is no valid unix epoch"}, status=400)
                if "from" in request.GET:
                    try:
                        from_timestamp = datetime.fromtimestamp(int(request.GET["from"]), timezone.utc)
                    except ValueError:
                        return JsonResponse({"success": False, "result": "From is no valid unix epoch"}, status=400)
                if from_timestamp:
                    raw_data = [x for x in raw_data if x.timestamp > from_timestamp]
                if to_timestamp:
                    raw_data = [x for x in raw_data if x.timestamp < to_timestamp]
                data["result"][request.GET["road_stretch"]] = [{"count_car": x.count_car,
                                                                "count_truck": x.count_truck,
                                                                "timestamp": int(x.timestamp.timestamp()),
                                                                "battery": x.battery,
                                                                "device": x.device.device_id} for x in raw_data]
                return JsonResponse(data, safe=False, status=200)
            except RoadUtilization.DoesNotExist:
                return JsonResponse({"success": False, "result": "road_stretch not found"})

