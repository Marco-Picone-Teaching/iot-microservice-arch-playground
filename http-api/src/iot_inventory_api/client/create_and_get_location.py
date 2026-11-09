# Create a new Location and read it through the URI returned in the Location header.
# From the service folder run: uv run create-and-get-location [location_id]

import sys
from typing import Any

import requests

from iot_inventory_api.client.api_config import API_BASE_URL


def main() -> None:

    location_id = sys.argv[1] if len(sys.argv) > 1 else "l112"
    api_url = f"{API_BASE_URL}/location"

    request_dictionary: dict[str, Any] = {
        "uuid": location_id,
        "name": "PythonTestBuilding",
        "latitude": 48.412321,
        "longitude": 10.533423211
    }

    response = requests.post(api_url, json=request_dictionary)

    if response.status_code == 201 and "Location" in response.headers:

        location_header = response.headers["Location"]
        print(f"HTTP Response Code: {response.status_code} - Location Header: {location_header}")

        # The Location header contains the URI of the new resource
        response = requests.get(location_header)
        print("Reading the new created Location Resource ...")
        print(f"HTTP Response Code: {response.status_code} - JSON Parsed Body: {response.json()}")
    else:
        print(f"Error creating the Location ! Code: {response.status_code} and Reason: {response.text.strip()}")


if __name__ == "__main__":
    main()
