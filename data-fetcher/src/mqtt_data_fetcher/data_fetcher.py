# MQTT Data Fetcher microservice. From the service folder run: uv run mqtt-data-fetcher
# In the container the same command is the CMD of the Docker image.
#
# The fetcher subscribes to the telemetry topic of the devices and, for each device publishing data, checks if the
# device is registered in the IoT Inventory (HTTP GET) and registers it if it does not exist yet (HTTP POST).

import json
import signal
import sys
from types import FrameType
from typing import Any

import paho.mqtt.client as mqtt
import requests
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from mqtt_data_fetcher.config.config_loader import ConfigLoader

# Configuration file (searched in the working directory and in the service root)
CONF_FILE_PATH = "fetcher_conf.yaml"

# Default configuration, used for the parameters not defined in the configuration file
DEFAULT_CONFIGURATION: dict[str, Any] = {
    "broker_ip": "127.0.0.1",
    "broker_port": 1883,
    "client_id": "mqtt-data-fetcher",
    "username": None,
    "password": None,
    "target_telemetry_topic": "device/+/temperature",
    "device_api_url": "http://127.0.0.1:7070/api/v1/iot/inventory/location/l0001/device"
}

# Timeout (seconds) of the HTTP requests to the Inventory API
HTTP_TIMEOUT_S = 5


class MqttDataFetcher:
    """ MQTT to HTTP integration: registers in the IoT Inventory the devices that publish telemetry data """

    def __init__(self, configuration: dict[str, Any]) -> None:

        self.broker_host: str = configuration["broker_ip"]
        self.broker_port: int = configuration["broker_port"]
        self.topic_filter: str = configuration["target_telemetry_topic"]
        self.device_api_url: str = configuration["device_api_url"]

        # Create the MQTT client (Paho 2.x requires the Callback API version)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, configuration["client_id"])
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        # Set the credentials only if they are configured
        if configuration["username"] and configuration["password"]:
            self.client.username_pw_set(configuration["username"], configuration["password"])

    def on_connect(self, client: mqtt.Client, userdata: Any, flags: mqtt.ConnectFlags,
                   reason_code: ReasonCode, properties: Properties | None) -> None:
        """ Subscribe only after a successful connection (called again at each automatic reconnection) """

        if reason_code.is_failure:
            print(f"Connection refused: {reason_code}")
            return

        print(f"Connected to MQTT Broker {self.broker_host}:{self.broker_port} ({reason_code})")
        client.subscribe(self.topic_filter)
        print(f"Subscribed to topic: {self.topic_filter}")

    def on_disconnect(self, client: mqtt.Client, userdata: Any, flags: mqtt.DisconnectFlags,
                      reason_code: ReasonCode, properties: Properties | None) -> None:
        print(f"Disconnected from MQTT Broker: {reason_code}")

    def on_message(self, client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
        """ For each telemetry message, register the device in the Inventory if it is not registered yet """

        if not mqtt.topic_matches_sub(self.topic_filter, message.topic):
            return

        try:
            # The payload must be valid JSON, while the device id is extracted from the topic
            json.loads(message.payload.decode("utf-8"))
            device_id = message.topic.split('/')[1]
            self.register_device_if_needed(device_id)
        except Exception as e:
            print(f"Error processing MQTT message on {message.topic}: {e}")

    def register_device_if_needed(self, device_id: str) -> None:
        """ Check if the device exists in the Inventory (GET) and create it if needed (POST) """

        check_device_url = f"{self.device_api_url}/{device_id}"
        check_device_response = requests.get(check_device_url, timeout=HTTP_TIMEOUT_S)
        print(f"Checking Device availability {check_device_url} -> Response Code: {check_device_response.status_code}")

        if check_device_response.status_code != 404:
            return

        print(f"New Device Detected: {device_id} Sending HTTP POST Request to: {self.device_api_url}")

        create_device_payload: dict[str, Any] = {
            "uuid": device_id,
            "name": f"Demo Temperature Sensor {device_id}",
            "device_type": "device.temperature",
            "manufacturer": "ACME Inc",
            "software_version": "0.0.1beta",
            "latitude": 48.312321,
            "longitude": 10.433423211
        }

        create_device_response = requests.post(self.device_api_url, json=create_device_payload, timeout=HTTP_TIMEOUT_S)

        if create_device_response.status_code == 201:
            print(f"Device {device_id} created successfully.")
        else:
            print(f"Failed to create device {device_id}. Status code: {create_device_response.status_code}")

    def run(self) -> None:
        """ Connect to the broker and run the network loop (blocking). If the broker is not available yet
        (e.g., its container is still starting), the connection is retried until it succeeds """

        print(f"Connecting to MQTT Broker {self.broker_host}:{self.broker_port} ...")
        self.client.connect_async(self.broker_host, self.broker_port, 60)
        self.client.loop_forever(retry_first_connection=True)

    def stop(self) -> None:
        """ Disconnect from the broker: this also stops loop_forever() """
        self.client.disconnect()


def main() -> None:

    configuration = ConfigLoader.load(CONF_FILE_PATH, DEFAULT_CONFIGURATION)
    data_fetcher = MqttDataFetcher(configuration)

    # In a container the process has PID 1 and ignores SIGTERM unless a handler is installed
    def handle_sigterm(signum: int, frame: FrameType | None) -> None:
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        data_fetcher.run()
    except (KeyboardInterrupt, SystemExit):
        data_fetcher.stop()
        print("MQTT Data Fetcher stopped")


if __name__ == "__main__":
    main()
