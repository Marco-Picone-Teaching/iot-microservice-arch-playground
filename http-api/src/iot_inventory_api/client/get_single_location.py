# Read a single Location. From the service folder run: uv run get-location [location_id]

import sys

import requests

from iot_inventory_api.client.api_config import API_BASE_URL


def main() -> None:

    location_id = sys.argv[1] if len(sys.argv) > 1 else "l0001"
    response = requests.get(f"{API_BASE_URL}/location/{location_id}")

    print(f"HTTP Response Code: {response.status_code} - String Body: {response.text.strip()}")
    if response.ok:
        print(f"JSON Parsed Body (Type: {type(response.json())}): {response.json()}")


if __name__ == "__main__":
    main()
