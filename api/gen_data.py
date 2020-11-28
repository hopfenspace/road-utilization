#!/usr/bin/env python3

import sys
import json
import random
import datetime

import requests


def generate_vehicle_data() -> dict:
    """Generate random vehicle data"""

    return {
        str(k): random.randint(0, 5)
        for k in range(1, random.randint(0, 10))
    }


def generate_payload(device_id: str) -> dict:
    """Generate random payload data for /put"""

    return {
        "dev_id": device_id,
        "payload_fields": {
            "battery": round(random.random() * 100, 3),
            "vehicles": generate_vehicle_data()
        },
        "metadata": {
            "time": datetime.datetime.now().isoformat(),
            "gateways": [
                {
                    "rssi": -random.randint(0, 100)
                }
            ]
        }
    }


class RandomTrafficGenerator:
    """Generator for random traffic data"""

    allowed_roads = ["primary", "secondary", "tertiary"]
    base_url = "https://lora.omikron.dev/api/"
    cached_roads = None
    cached_road_keys = None

    def __init__(self, device_id: str, coordinate: dict, road_stretch: str):
        self.device_id = device_id
        self.coordinate = coordinate
        self.road_stretch = road_stretch

        self.set_position()

    def set_position(self):
        """Tell the sensor's position to the backend"""

        r = requests.post(
            self.base_url + "setSensorPosition",
            json={
                "device": self.device_id,
                "coordinate": self.coordinate,
                "linked_road_stretch": self.road_stretch
            },
            headers={"User-Agent": "curl/7.52.1"}
        )
        print("set_position", r)
        print(r.text)

    def send_data(self):
        """Send randomly generated payload data to the backend"""

        self.response = requests.post(
            self.base_url + "put",
            json=generate_payload(self.device_id),
            headers={"User-Agent": "curl/7.52.1"}
        )
        print("send_data", self.response)

    @classmethod
    def get_all_roads(cls) -> dict:
        """Get a list of all roads from the backend"""

        response = requests.get(
            cls.base_url + "getRoads",
            headers={"User-Agent": "curl/7.52.1"}
        )
        content = json.loads(response.content)
        if not content["success"]:
            raise RuntimeError("Error fetching data from /getRoads")
        return content["result"]

    @classmethod
    def get_roads(cls) -> dict:
        """Get a list of all allowed roads from the backend"""

        roads = cls.get_all_roads()
        return {
            k: roads[k] for k in roads
            if roads[k]["road_type"] in cls.allowed_roads
        }

    @classmethod
    def find_random_position(cls) -> tuple:
        """Find a random position for a sensor"""

        if cls.cached_roads is None or cls.cached_road_keys is None:
            cls.cached_roads = cls.get_roads()
            cls.cached_road_keys = list(cls.cached_roads.keys())


if __name__ == "__main__":
    count = 10
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    [
        RandomTrafficGenerator(
            f"random_data_generator_{k}_{random.randint(1000, 100000)}"
        )
        for k in range(count)
    ]

