# IoT Inventory Web UI microservice. From the service folder run: uv run iot-inventory-web-ui
# In the container the same command is the CMD of the Docker image.
#
# The Web UI does not store any data: each page retrieves the data from the IoT Inventory API over HTTP
# and renders it with the Jinja2 templates of the templates/ folder.

import signal
import sys
from pathlib import Path
from types import FrameType
from typing import Any

import requests
from flask import Flask, render_template
from werkzeug.serving import make_server

from iot_inventory_web_ui.config.config_loader import ConfigLoader

# Configuration file (searched in the working directory and in the service root)
CONF_FILE_PATH = "web_conf.yaml"

# Folder of the HTML templates: src/iot_inventory_web_ui/templates
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

# Timeout (seconds) of the HTTP requests to the Inventory API
HTTP_TIMEOUT_S = 5

# Default configuration, used for the parameters not defined in the configuration file
DEFAULT_CONFIGURATION: dict[str, Any] = {
    "web": {
        "host": "0.0.0.0",
        "port": 7071,
        "api_base_url": "http://127.0.0.1:7070/api/v1/iot/inventory"
    }
}


class WebServer:
    """ Flask Web Server rendering the Locations and Devices retrieved from the IoT Inventory API """

    def __init__(self, configuration: dict[str, Any]) -> None:

        self.host: str = configuration["web"]["host"]
        self.port: int = configuration["web"]["port"]
        self.api_base_url: str = configuration["web"]["api_base_url"]

        # Create the Flask app using the templates folder of the package
        self.app = Flask(__name__, template_folder=str(TEMPLATE_DIR))

        # Add URL rules to the Flask app mapping the URL to the function
        self.app.add_url_rule('/locations', 'locations', self.locations)
        self.app.add_url_rule('/location/<string:location_id>/devices', 'devices', self.devices)

    def http_get(self, path: str) -> Any:
        """ Send a GET request to the Inventory API and return the parsed JSON body """
        response = requests.get(f"{self.api_base_url}{path}", timeout=HTTP_TIMEOUT_S)
        response.raise_for_status()
        return response.json()

    def locations(self) -> Any:
        """ Get all locations from the Inventory API and render the locations.html template """
        try:
            location_list = self.http_get("/location")
        except requests.RequestException as e:
            return f"IoT Inventory API not available: {e}", 503
        return render_template('locations.html', locations=location_list)

    def devices(self, location_id: str) -> Any:
        """ Get all devices of a location from the Inventory API and render the devices.html template """
        try:
            device_list = self.http_get(f"/location/{location_id}/device")
        except requests.HTTPError as e:
            return f"Location {location_id} not found: {e}", 404
        except requests.RequestException as e:
            return f"IoT Inventory API not available: {e}", 503
        return render_template('devices.html', devices=device_list, location_id=location_id)

    def run(self) -> None:
        """ Run the Web Server (blocking) """
        http_server = make_server(self.host, self.port, self.app, threaded=True)
        print(f"IoT Inventory Web UI running on http://{self.host}:{self.port}/locations (CTRL+C to stop)")
        try:
            http_server.serve_forever()
        finally:
            http_server.server_close()


def handle_sigterm(signum: int, frame: FrameType | None) -> None:
    """ Stop the service when the container is stopped (docker stop sends SIGTERM to the main process) """
    sys.exit(0)


def main() -> None:

    configuration = ConfigLoader.load(CONF_FILE_PATH, DEFAULT_CONFIGURATION)
    web_server = WebServer(configuration)

    # In a container the process has PID 1 and ignores SIGTERM unless a handler is installed
    signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        web_server.run()
    except (KeyboardInterrupt, SystemExit):
        print("IoT Inventory Web UI stopped")


if __name__ == "__main__":
    main()
