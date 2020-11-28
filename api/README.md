# API

## API Calls

### put

Use json encoded data to input new measurements.

#### POST /api/put

```
{
    "dev_id": "testdevice1337",
    "payload_fields": {
        "battery": 4.322,
        "vehicles":
        {
            "1": 1,
            "2": 4,
            "3": 0,
            "4": 1,
            "5": 0,
            "6": 0,
            "7": 1,
            "8": 0,
            "9": 0
        }
    },
    "metadata": {
        "time": "2020-11-25T21:45:32.231844583Z",
        "gateways":
        [
             {
                 "rssi": -58
             }
        ]
    }

}
```

### setSensorPosition

#### POST /api/setSensorPosition

```
{
    "device": str,
    "coordinate": {
        "lat": float,
        "lon": float
    },
    "linked_road_stretch": osm_id
}
```

### getRoads

This method is used to get all RoadStretches with their associated coordinates. A RoadStretch is identified by an ID `way/<number`. The IDs correspond to the OSM IDs.

#### GET /api/getRoads

#### Response:
```
{
    "success": "true",
    "result":
    {
        "way/0123456789":
        {
            "road_type": "primary",
            "coordinates":
            [
                {
                    "lat": 50.1234567,
                    "lon": 10.1234567
                },
                [..]
            ]
        },
        [..]
    }
}
```

### getRoadUtilization

Use this method to get the utilization of RoadStretches.

#### GET /api/getUtilizationHistory

Parameter    | Optional           | Description                       | Example
---          | :---:              | ---                               | ---
road_stretch | :white_check_mark: | Specifies the wanted road_stretch | way/0123456789
limit        | :white_check_mark: | Limit data to last x data packets | 20

#### Example

`curl "/api/getRoadUtilization?road_stretch=way/32860057"`

#### Response

```
{
    "success": "true",
    "result": [
        {
            "count_car": 7,
            "count_truck": 2,
            "timestamp": "2020-11-26T17:42:03"
        },
        {
            "count_car": 14,
            "count_truck": 0,
            "timestamp": "2020-11-26T17:57:04"
        },
        [..]
    ]
}
```

### getSensorPositions

Use this method to retrieve the coordinates and the linked RoadStretches of all sensors.

#### GET /api/getSensorPositions

#### Response

```
{
    "success": "true",
    "result":
    {
        "test_sensor":
        {
            "coordinates":
            {
                "lat": 50.1234567,
                "long": 10.1234567
            },
            "linked_road_stretch": "way/123456789"
        }
    }
}
```

### getRoadUtilizationHistory

Use this method to receive the raw data linked to a RoadUtilization.

#### GET /api/getRoadUtilizationHistory

Parameter    | Optional           | Description                                                                    | Example
---          | :---:              | ---                                                                            | ---
road_stretch | :x:                | Specifies the wanted road_stretch                                              | way/0123456789
from         | :white_check_mark: | Unix Epoch Timestamp in UTC from which the data should be displayed, excluding | 1606340000
to           | :white_check_mark: | Unix Epoch Timestamp in UTC to which the data should be displayed, excluding   | 1606349999

#### Response

```
{
    "status": "true",
    "result":
    {
        "way/<id>":
        [
            {
                "count_car": "23",
                "count_truck": "12",
                "timestamp" : "1606340044",
                "battery": "3.9",
                "device": "testdevice"
            },
            [...]
        ]
    }
}
```
