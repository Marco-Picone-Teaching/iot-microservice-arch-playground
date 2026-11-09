# IoT Inventory RESTful HTTP API microservice. From the service folder run: uv run iot-inventory-api
# In the container the same command is the CMD of the Docker image.

import signal
import sys
from types import FrameType
from typing import Any

from flask import Flask
from flask_restful import Api
from werkzeug.serving import make_server

from iot_inventory_api.config.config_loader import ConfigLoader
from iot_inventory_api.persistence.data_manager import DataManager
from iot_inventory_api.resources.device_resource import DeviceResource
from iot_inventory_api.resources.devices_resource import DevicesResource
from iot_inventory_api.resources.location_resource import LocationResource
from iot_inventory_api.resources.locations_resource import LocationsResource

# Configuration file (searched in the working directory and in the service root)
CONF_FILE_PATH = "conf.yaml"

# Default configuration, used for the parameters not defined in the configuration file
DEFAULT_CONFIGURATION: dict[str, Any] = {
    "rest": {
        "api_prefix": "/api/v1/iot/inventory",
        "host": "0.0.0.0",
        "port": 7070
    }
}


def create_app(data_manager: DataManager, api_prefix: str) -> Flask:
    """ Create the Flask application with the RESTful API resources """

    app = Flask(__name__)
    api = Api(app)
    resource_kwargs = {'data_manager': data_manager}

    api.add_resource(LocationsResource, api_prefix + '/location',
                     resource_class_kwargs=resource_kwargs,
                     endpoint="locations",
                     methods=['GET', 'POST'])

    api.add_resource(LocationResource, api_prefix + '/location/<string:location_id>',
                     resource_class_kwargs=resource_kwargs,
                     endpoint='location',
                     methods=['GET', 'PUT', 'DELETE'])

    api.add_resource(DevicesResource, api_prefix + '/location/<string:location_id>/device',
                     resource_class_kwargs=resource_kwargs,
                     endpoint="devices",
                     methods=['GET', 'POST'])

    api.add_resource(DeviceResource, api_prefix + '/location/<string:location_id>/device/<string:device_id>',
                     resource_class_kwargs=resource_kwargs,
                     endpoint='device',
                     methods=['GET', 'PUT', 'DELETE'])

    return app


def handle_sigterm(signum: int, frame: FrameType | None) -> None:
    """ Stop the service when the container is stopped (docker stop sends SIGTERM to the main process) """
    sys.exit(0)


def main() -> None:

    configuration = ConfigLoader.load(CONF_FILE_PATH, DEFAULT_CONFIGURATION)
    rest_configuration = configuration["rest"]

    # Data Manager with a demo location (l0001) and a demo device (d0001)
    data_manager = DataManager()
    data_manager.init_demo_data()

    app = create_app(data_manager, rest_configuration["api_prefix"])

    # In a container the process has PID 1 and ignores SIGTERM unless a handler is installed
    signal.signal(signal.SIGTERM, handle_sigterm)

    http_server = make_server(rest_configuration["host"], rest_configuration["port"], app, threaded=True)
    print(f"IoT Inventory API running on http://{rest_configuration['host']}:{rest_configuration['port']}"
          f"{rest_configuration['api_prefix']} (CTRL+C to stop)")

    try:
        http_server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("IoT Inventory API stopped")
    finally:
        http_server.server_close()


if __name__ == "__main__":
    main()
