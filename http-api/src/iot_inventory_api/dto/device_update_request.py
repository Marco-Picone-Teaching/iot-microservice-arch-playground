import json


class DeviceUpdateRequest:
    """ Request body to update an existing Device """

    def __init__(self, uuid: str, name: str, device_type: str, manufacturer: str,
                 software_version: str, latitude: float, longitude: float) -> None:
        self.uuid = uuid
        self.name = name
        self.type = device_type
        self.manufacturer = manufacturer
        self.software_version = software_version
        self.latitude = latitude
        self.longitude = longitude

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)
