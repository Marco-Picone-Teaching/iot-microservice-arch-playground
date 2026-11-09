# Update a Location. From the service folder run: uv run update-location [location_id]

import sys
from typing import Any

import requests

from iot_inventory_api.client.api_config import API_BASE_URL


def main() -> None:

    location_id = sys.argv[1] if len(sys.argv) > 1 else "l0001"

    # The uuid in the body must match the uuid in the URI
    request_dictionary: dict[str, Any] = {
        "uuid": location_id,
        "name": "PythonUpdated-TestBuilding",
        "latitude": 48.412321,
        "longitude": 10.533423211
    }

    response = requests.put(f"{API_BASE_URL}/location/{location_id}", json=request_dictionary)

    print(f"HTTP Response Code: {response.status_code} - Body: {response.content!r}")


if __name__ == "__main__":
    main()
