import time
from typing import Any

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "BeautyFinder/1.0 (kluzodota@gmail.com)",
}


def get_coordinates(address: str) -> tuple[float, float]:
    """
    Convert address to latitude and longitude.
    """

    response = requests.get(
        NOMINATIM_URL,
        params={
            "q": address,
            "format": "jsonv2",
            "limit": 1,
        },
        headers=HEADERS,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        raise ValueError("Address not found.")

    return float(data[0]["lat"]), float(data[0]["lon"])


def find_places_near_location(
        address: str,
        radius_km: float,
) -> list[dict[str, Any]]:
    """
    Finds all shops near the given address.

    Args:
        address: Human-readable address.
        radius_km: Search radius in kilometers.

    Returns:
        List of nearby shops.
    """

    lat, lon = get_coordinates(address)

    radius_m = int(radius_km * 1000)

    query = f"""
    [out:json][timeout:25];
    (
      node["shop"](around:{radius_m},{lat},{lon});
      way["shop"](around:{radius_m},{lat},{lon});
      relation["shop"](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """

    response = requests.post(
        OVERPASS_URL,
        data=query,
        headers=HEADERS,
        timeout=600,
    )

    response.raise_for_status()

    data = response.json()

    places = []

    for element in data["elements"]:
        if "lat" in element:
            latitude = element["lat"]
            longitude = element["lon"]
        else:
            latitude = element["center"]["lat"]
            longitude = element["center"]["lon"]

        tags = element.get("tags", {})

        places.append(
            {
                "name": tags.get("name", "Unknown"),
                "shop_type": tags.get("shop"),
                "address": ", ".join(
                    filter(
                        None,
                        [
                            tags.get("addr:street"),
                            tags.get("addr:housenumber"),
                            tags.get("addr:city"),
                        ],
                    )
                ),
                "lat": latitude,
                "lon": longitude,
            }
        )

    return places


if __name__ == "__main__":
    coordinate = get_coordinates("Київ")
    print(coordinate)
    places = find_places_near_location(
        address="Київ",
        radius_km=3,
    )

    for place in places:
        print(place)
