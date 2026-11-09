# Read the list of the Locations. From the service folder run: uv run get-location-list

import requests

from iot_inventory_api.client.api_config import API_BASE_URL


def main() -> None:

    response = requests.get(f"{API_BASE_URL}/location")

    # Read Status code and Body in 3 different ways (Byte Buffer, String, JSON)
    print(f"HTTP Response Code: {response.status_code} - Buffer Body: {response.content!r}")
    print(f"HTTP Response Code: {response.status_code} - String Body: {response.text.strip()}")
    print(f"HTTP Response Code: {response.status_code} - JSON Parsed Body (Type: {type(response.json())}): {response.json()}")


if __name__ == "__main__":
    main()
