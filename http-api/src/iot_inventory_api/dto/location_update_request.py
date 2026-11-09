import json


class LocationUpdateRequest:
    """ Request body to update an existing Location """

    def __init__(self, uuid: str, name: str, latitude: float, longitude: float) -> None:
        self.uuid = uuid
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)
