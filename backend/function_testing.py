import random
import time
from typing import Any

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_SERVER = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

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


_OVERPASS_QUERY_TEMPLATE = """
[out:json][timeout:100];
(
  nwr["shop"~"^(beauty|hairdresser)$"](around:{radius_m},{lat},{lon});
  nwr["amenity"~"^(beauty_salon|spa)$"](around:{radius_m},{lat},{lon});
  nwr["beauty"](around:{radius_m},{lat},{lon});
);
out center tags;
"""


def _build_query(lat: float, lon: float, radius_m: int) -> str:
    return _OVERPASS_QUERY_TEMPLATE.format(radius_m=radius_m, lat=lat, lon=lon)


def _parse_element(element: dict[str, Any]) -> dict[str, Any]:
    if "lat" in element:
        latitude, longitude = element["lat"], element["lon"]
    else:
        center = element["center"]
        latitude, longitude = center["lat"], center["lon"]

    tags = element.get("tags", {})

    address = ", ".join(
        filter(
            None,
            (tags.get("addr:street"), tags.get("addr:housenumber"), tags.get("addr:city")),
        )
    )

    return {
        "name": tags.get("name", "Unknown"),
        "shop_type": tags.get("shop"),
        "address": address,
        "lat": latitude,
        "lon": longitude,
    }


def find_places_near_location_overpass(
        coordinate: tuple[float, float],
        radius_km: float,
) -> list[dict[str, Any]]:
    """
    Finds all shops near the given address.

    Args:
        coordinate: Coordinate of address.
        radius_km: Search radius in kilometers.

    Returns:
        List of nearby shops.
    """
    lat, lon = coordinate
    radius_m = round(radius_km * 1000)

    query = _build_query(lat, lon, radius_m)

    # перемішуємо сервери, щоб рівномірно розподіляти навантаження
    servers = random.sample(OVERPASS_SERVER, len(OVERPASS_SERVER))

    data: dict[str, Any] | None = None
    last_error: Exception | None = None

    with requests.Session() as session:
        session.headers.update(HEADERS)
        for server in servers:
            try:
                response = session.post(server, data=query, timeout=100)
                response.raise_for_status()
                data = response.json()
                break
            except requests.RequestException as exc:
                last_error = exc
        else:
            raise RuntimeError("All Overpass servers are unavailable.") from last_error

    return [_parse_element(element) for element in data.get("elements", ())]


GEOAPIFY_API_KEY = "a7580c03d6a343c1871c71c76d55f16c"
GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"

# service.beauty охоплює hairdresser/massage/spa/tanning_salon/tattoo,
# leisure.spa додає публічні лазні та сауни (аналог amenity=spa в OSM)
PLACE_CATEGORIES = ",".join([
    "service.beauty",
    "service.beauty.hairdresser",
    "service.beauty.massage",
    "service.beauty.spa",
    "service.beauty.tanning_salon",
    "leisure.spa",
])


def find_places_near_location_geoapify(
        coordinate: tuple[float, float],
        radius_km: float,
) -> list[dict[str, Any]]:
    """
    Finds all beauty-related places near the given coordinate.

    Args:
        coordinate: Coordinate of address (lat, lon).
        radius_km: Search radius in kilometers.

    Returns:
        List of nearby shops.
    """
    lat, lon = coordinate
    radius_m = round(radius_km * 1000)

    params = {
        "categories": PLACE_CATEGORIES,
        "filter": f"circle:{lon},{lat},{radius_m}",
        "bias": f"proximity:{lon},{lat}",
        "limit": 100,
        "apiKey": GEOAPIFY_API_KEY,
    }

    response = requests.get(GEOAPIFY_PLACES_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    places = []

    for feature in data.get("features", ()):
        props = feature.get("properties", {})
        categories = props.get("categories", [])

        # найспецифічніша категорія service.beauty.* стає "типом магазину";
        # якщо такої немає (наприклад, чистий leisure.spa), беремо None
        shop_type = next(
            (c.split(".", 1)[1] for c in categories if c.startswith("service.beauty.")),
            None,
        )

        places.append(
            {
                "name": props.get("name", "Unknown"),
                "shop_type": shop_type,
                "address": props.get("formatted", ""),
                "lat": props.get("lat"),
                "lon": props.get("lon"),
            }
        )

    return places


if __name__ == "__main__":
    coordinate = get_coordinates("Київ")
    print(coordinate)
    places = find_places_near_location_overpass(
        coordinate=coordinate,
        radius_km=1,
    )

    print("Count of overpass: ", len(places))

    for place in places:
        print(place)

    print(coordinate)
    places = find_places_near_location_geoapify(
        coordinate=coordinate,
        radius_km=1,
    )

    print("Count of geoapify: ", len(places))

    for place in places:
        print(place)
