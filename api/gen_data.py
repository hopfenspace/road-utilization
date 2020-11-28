#!/usr/bin/env python3

import random
import datetime
import urllib.parse


# Static data
base_url = "https://lora.omikron.dev/api/"
device_id = "random_data_generator"


def generate_vehicle_data() -> dict:
    """Generate random vehicle data"""

    return {str(k): random.randint(0, 5) for k in range(1, random.randint(0, 10))}


def generate_payload() -> dict:
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

