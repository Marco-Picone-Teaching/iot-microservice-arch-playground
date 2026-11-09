from json import JSONDecodeError
from typing import Any

from flask import request, Response
from flask_restful import Resource, reqparse

from iot_inventory_api.persistence.data_manager import DataManager
from iot_inventory_api.model.device_model import DeviceModel
from iot_inventory_api.dto.device_creation_request import DeviceCreationRequest


class DevicesResource(Resource):
    """ Collection of the Devices of a Location: list the Devices (GET, optional ?type= filter) and create one (POST) """

    def __init__(self, **kwargs: Any) -> None:
        self.data_manager: DataManager = kwargs['data_manager']

    def post(self, location_id: str) -> Any:
        """Create a new Device in the specified Location"""
        try:
            # Retrieve the target Location through its location_id
            target_location = self.data_manager.get_location_by_id(location_id)
            if target_location is None:
                return {'error': "Location Not Found !"}, 404

            # The boolean flag force the parsing of POST data as JSON irrespective of the mimetype
            json_data = request.get_json(force=True)
            device_creation_request = DeviceCreationRequest(**json_data)

            # Check if the device is new or if it already exists
            if device_creation_request.uuid in target_location.device_dictionary:
                return {'error': "Device UUID already exists"}, 409

            # Create a new DeviceModel from the data available in the request
            new_device_model = DeviceModel(device_creation_request.uuid,
                                           device_creation_request.name,
                                           location_id,
                                           device_creation_request.type,
                                           device_creation_request.manufacturer,
                                           device_creation_request.software_version,
                                           device_creation_request.latitude,
                                           device_creation_request.longitude)

            self.data_manager.add_device(location_id, new_device_model)

            # 201 Created with the URI of the new resource in the Location header
            return Response(status=201, headers={"Location": request.url + "/" + new_device_model.uuid})
        except (JSONDecodeError, TypeError):
            return {'error': "Invalid JSON ! Check the request"}, 400
        except Exception as e:
            return {'error': "Generic Internal Server Error ! Reason: " + str(e)}, 500

    def get(self, location_id: str) -> Any:
        """Retrieve the list of Devices associated to a specific Location, optionally filtered by type"""

        target_location = self.data_manager.get_location_by_id(location_id)
        if target_location is None:
            return {'error': "Location Not Found !"}, 404

        # Optional query argument to filter the devices by type (e.g., ?type=device.sensor)
        parser = reqparse.RequestParser()
        parser.add_argument('type', location='args')
        args = parser.parse_args()
        type_filter = args.get("type")

        # Build a serializable device list applying the optional filter
        device_list = [device.__dict__ for device in target_location.device_dictionary.values()
                       if type_filter is None or device.type == type_filter]

        return device_list, 200
