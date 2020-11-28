#!/usr/bin/env python3

import sys
import random
import datetime


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

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.base_url = "https://lora.omikron.dev/api/"
        self.allowed_roads = ["primary", "secondary", "tertiary"]


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

