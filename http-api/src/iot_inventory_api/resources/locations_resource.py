from json import JSONDecodeError
from typing import Any

from flask import request, Response
from flask_restful import Resource

from iot_inventory_api.persistence.data_manager import DataManager
from iot_inventory_api.model.location_model import LocationModel
from iot_inventory_api.dto.location_creation_request import LocationCreationRequest
from iot_inventory_api.dto.location_entity_response import LocationEntityResponse


class LocationsResource(Resource):
    """ Collection of Locations: list all the Locations (GET) and create a new one (POST) """

    def __init__(self, **kwargs: Any) -> None:
        self.data_manager: DataManager = kwargs['data_manager']

    def post(self) -> Any:
        """Create a new location"""
        try:
            # The boolean flag force the parsing of POST data as JSON irrespective of the mimetype
            json_data = request.get_json(force=True)
            location_creation_request = LocationCreationRequest(**json_data)

            if self.data_manager.is_location_registered(location_creation_request.uuid):
                return {'error': "Location UUID already exists"}, 409

            new_location_model = LocationModel(location_creation_request.uuid,
                                               location_creation_request.name,
                                               location_creation_request.latitude,
                                               location_creation_request.longitude)
            self.data_manager.add_location(new_location_model)

            # 201 Created with the URI of the new resource in the Location header
            return Response(status=201, headers={"Location": request.url + "/" + new_location_model.uuid})
        except (JSONDecodeError, TypeError):
            return {'error': "Invalid JSON ! Check the request"}, 400
        except Exception as e:
            return {'error': "Generic Internal Server Error ! Reason: " + str(e)}, 500

    def get(self) -> Any:
        """Retrieve the list of all the locations"""

        result_location_list = []

        for location in self.data_manager.get_all_locations():

            # Build a serializable list with the ids of the devices of the location
            device_id_list = [device.uuid for device in location.device_dictionary.values()]

            location_entity_response = LocationEntityResponse(location.uuid,
                                                              location.name,
                                                              location.latitude,
                                                              location.longitude,
                                                              device_id_list)

            result_location_list.append(location_entity_response.__dict__)

        return result_location_list, 200
