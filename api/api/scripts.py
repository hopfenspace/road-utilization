import json

from road_utilization.models import RoadType, Coordinate, Road, RoadStretch


def import_roads():
    with open("roads.json") as fh:
        road_data = json.load(fh)["features"]

        for road in road_data:
            road_type, created = RoadType.objects.get_or_create(highway_type=road["properties"]["highway"])
            if created:
                road_type.save()

            coordinate_list = []
            for coordinate_data in road["geometry"]["coordinates"]:
                coordinate = Coordinate.objects.create(lat=coordinate_data[1], lon=coordinate_data[0])
                coordinate.save()
                coordinate_list.append(coordinate)

            name = road["properties"]["loc_name"] if "loc_name" in road["properties"] else road["properties"]["name"] if "name" in road["properties"] else road["properties"]["@id"]
            road_stretch, created = RoadStretch.objects.get_or_create(
                osm_id=road["properties"]["@id"],
                road_type=road_type
            )
            road_stretch.coordinates.clear()
            for coordinate in coordinate_list:
                road_stretch.coordinates.add(coordinate)
            road_stretch.save()

            road_obj, created = Road.objects.get_or_create(
                name=name
            )
            road_obj.road_stretches.add(road_stretch)
            road_obj.save()
