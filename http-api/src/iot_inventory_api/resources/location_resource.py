from json import JSONDecodeError
from typing import Any

from flask import request, Response
from flask_restful import Resource

from iot_inventory_api.persistence.data_manager import DataManager
from iot_inventory_api.model.location_model import LocationModel
from iot_inventory_api.dto.location_entity_response import LocationEntityResponse
from iot_inventory_api.dto.location_update_request import LocationUpdateRequest


class LocationResource(Resource):
    """ Single Location identified by its UUID: read (GET), update (PUT) and delete (DELETE) """

    def __init__(self, **kwargs: Any) -> None:
        self.data_manager: DataManager = kwargs['data_manager']

    def get(self, location_id: str) -> Any:
        """ Get a location by its UUID """

        location = self.data_manager.get_location_by_id(location_id)
        if location is None:
            return {'error': "Location Not Found !"}, 404

        # Build a serializable list with the ids of the devices of the location
        device_id_list = [device.uuid for device in location.device_dictionary.values()]

        location_entity_response = LocationEntityResponse(location.uuid,
                                                          location.name,
                                                          location.latitude,
                                                          location.longitude,
                                                          device_id_list)
        return location_entity_response.__dict__, 200

    def delete(self, location_id: str) -> Any:
        """ Delete a location by its UUID """
        try:
            if self.data_manager.is_location_registered(location_id):
                self.data_manager.remove_location(location_id)
                return Response(status=204)
            else:
                return {'error': "Location UUID not found"}, 404
        except Exception as e:
            return {'error': "Generic Internal Server Error ! Reason: " + str(e)}, 500

    def put(self, location_id: str) -> Any:
        """ Update a location by its UUID """

        try:
            current_location = self.data_manager.get_location_by_id(location_id)
            if current_location is None:
                return {'error': "Location UUID not found"}, 404

            # The boolean flag force the parsing of PUT data as JSON irrespective of the mimetype
            json_data = request.get_json(force=True)
            location_update_request = LocationUpdateRequest(**json_data)

            # The UUID in the body must match the UUID of the resource
            if location_update_request.uuid != location_id:
                return {'error': "UUID mismatch between body and resource"}, 400

            updated_location_model = LocationModel(location_update_request.uuid,
                                                   location_update_request.name,
                                                   location_update_request.latitude,
                                                   location_update_request.longitude)

            # Keep the devices already registered in the location
            updated_location_model.device_dictionary = current_location.device_dictionary

            self.data_manager.update_location(updated_location_model)
            return Response(status=204)
        except (JSONDecodeError, TypeError):
            return {'error': "Invalid JSON ! Check the request"}, 400
        except Exception as e:
            return {'error': "Generic Internal Server Error ! Reason: " + str(e)}, 500
