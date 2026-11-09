import json

from iot_inventory_api.model.device_model import DeviceModel


class LocationModel:
    """ Domain model of a Location hosting a set of IoT Devices (indexed by their uuid) """

    def __init__(self, uuid: str, name: str, latitude: float, longitude: float) -> None:
        self.uuid = uuid
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.device_dictionary: dict[str, DeviceModel] = {}

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)
