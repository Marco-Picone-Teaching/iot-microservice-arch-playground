# Delete a Location. From the service folder run: uv run delete-location [location_id]

import sys

import requests

from iot_inventory_api.client.api_config import API_BASE_URL


def main() -> None:

    location_id = sys.argv[1] if len(sys.argv) > 1 else "l101"
    print(f"Deleting Location with id: {location_id}")

    response = requests.delete(f"{API_BASE_URL}/location/{location_id}")

    print(f"HTTP Response Code: {response.status_code} - String Body: {response.text.strip()}")


if __name__ == "__main__":
    main()
