import json


class LocationEntityResponse:
    """ Response body describing a Location and the list of the ids of its Devices """

    def __init__(self, uuid: str, name: str, latitude: float, longitude: float, device_list: list[str]) -> None:
        self.uuid = uuid
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.device_list = device_list

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)
