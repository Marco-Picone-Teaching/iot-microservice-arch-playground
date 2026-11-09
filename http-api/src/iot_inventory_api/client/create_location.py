# Create a new Location. From the service folder run: uv run create-location [location_id]

import sys
from typing import Any

import requests

from iot_inventory_api.client.api_config import API_BASE_URL


def main() -> None:

    location_id = sys.argv[1] if len(sys.argv) > 1 else "l101"
    api_url = f"{API_BASE_URL}/location"

    # Request Body as Python dictionary
    request_dictionary: dict[str, Any] = {
        "uuid": location_id,
        "name": "PythonTestBuilding",
        "latitude": 48.412321,
        "longitude": 10.533423211
    }

    # Send the POST Request with the body serialized as JSON (internally managed by the library)
    response = requests.post(api_url, json=request_dictionary)

    print(f"HTTP Response Code: {response.status_code} - Body: {response.content!r} "
          f"- Location Header: {response.headers.get('Location')}")


if __name__ == "__main__":
    main()
