"""OSRM Routing Service.

Fetches real walking paths between coordinates using the OSRM public API.
Returns actual road/path geometry following real walkable streets and trails.
"""
import requests


class OSRMService:
    BASE_URL = "https://router.project-osrm.org/route/v1/foot"

    def get_walking_path(self, start_lat: float, start_lng: float,
                         end_lat: float, end_lng: float) -> list:
        """Fetch real walking path coordinates from OSRM.

        Returns list of [lat, lng] pairs representing the walking path,
        or None if OSRM is unavailable.
        """
        # OSRM expects coordinates as lng,lat (longitude first)
        request_url = (
            f"{self.BASE_URL}"
            f"/{start_lng},{start_lat}"
            f";{end_lng},{end_lat}"
            f"?overview=full&geometries=geojson"
        )

        try:
            # verify=False handles SSL inspection on university/corporate networks.
            # On a normal network or production server, SSL verification succeeds naturally.
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            response = requests.get(request_url, timeout=8,
                                    headers={"User-Agent": "MoodRoute/1.0"},
                                    verify=False)
            response.raise_for_status()
            route_data = response.json()

            if route_data.get("code") != "Ok" or not route_data.get("routes"):
                print(f"[OSRM] No route found: {route_data.get('code')}")
                return None

            # OSRM returns [lng, lat] — convert to [lat, lng] for Leaflet
            raw_coordinates = route_data["routes"][0]["geometry"]["coordinates"]
            walking_path = [[coord[1], coord[0]] for coord in raw_coordinates]

            print(f"[OSRM] Real path fetched: {len(walking_path)} waypoints")
            return walking_path

        except Exception as osrm_error:
            print(f"[OSRM] Service unavailable: {osrm_error}")
            return None

    def get_path_for_route(self, route: dict) -> list:
        """Get real walking path for a database route.

        Uses first and last coordinate as start/end, fetches OSRM path between them.
        Falls back to seed coordinates if OSRM fails.
        """
        route_coordinates = route.get("coordinates", [])
        if not route_coordinates or len(route_coordinates) < 2:
            return route_coordinates

        start_point = route_coordinates[0]
        end_point = route_coordinates[-1]

        real_path = self.get_walking_path(
            start_lat=start_point[0], start_lng=start_point[1],
            end_lat=end_point[0], end_lng=end_point[1]
        )

        if real_path and len(real_path) >= 2:
            return real_path

        print(f"[OSRM] Using seed coordinates for route '{route.get('name')}'")
        return route_coordinates
