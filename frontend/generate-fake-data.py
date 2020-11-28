import math
import json
import random

roadTypes = {
		"primary": (3, 10),
		"secondary": (1, 8),
		"tertiary": (0, 6),
	}

with open("./streets.json", "r") as fd:
	data = json.load(fd)


streets = data["result"]
result = {}
for name in streets:
	street = streets[name]
	if street["road_type"] not in roadTypes:
		continue
	minCars, maxCars = roadTypes[street["road_type"]]
	result[name] = {
			"count_car": random.randint(minCars, maxCars),
			"count_truck": 0,
		}

with open("./data.json", "w") as fd:
	json.dump({"success": True, "result": result}, fd)
