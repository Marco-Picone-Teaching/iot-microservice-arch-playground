import json


class DeviceModel:
    """ Domain model of an IoT Device registered in a Location """

    DEVICE_TYPE_DEFAULT = "device.default"
    DEVICE_TYPE_MOBILE = "device.mobile"
    DEVICE_TYPE_SENSOR = "device.sensor"
    DEVICE_TYPE_ACTUATOR = "device.actuator"

    def __init__(self, uuid: str, name: str, location_id: str, device_type: str, manufacturer: str,
                 software_version: str, latitude: float, longitude: float) -> None:
        self.uuid = uuid
        self.name = name
        self.locationId = location_id
        self.type = device_type
        self.manufacturer = manufacturer
        self.software_version = software_version
        self.latitude = latitude
        self.longitude = longitude

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)
