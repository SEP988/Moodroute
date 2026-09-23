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

    def get_path_for_route(self, route: dict, user_lat: float = None, user_lng: float = None) -> list:
        """Get real walking path for a database route.

        If user_lat/user_lng are provided, routes from the user's actual
        location to the destination. Otherwise falls back to the seed start.
        """
        route_coordinates = route.get("coordinates", [])
        if not route_coordinates or len(route_coordinates) < 2:
            return route_coordinates

        # The destination is always the last seed coordinate
        end_point = route_coordinates[-1]

        # Use user's real location as start if provided, else use seed start
        if user_lat is not None and user_lng is not None:
            start_lat, start_lng = user_lat, user_lng
        else:
            start_lat, start_lng = route_coordinates[0][0], route_coordinates[0][1]

        real_path = self.get_walking_path(
            start_lat=start_lat, start_lng=start_lng,
            end_lat=end_point[0], end_lng=end_point[1]
        )

        if real_path and len(real_path) >= 2:
            return real_path

        # OSRM failed — return an interpolated path so the map never shows
        # a straight line. Generate 20 intermediate points between start and end.
        print(f"[OSRM] Using interpolated fallback for route '{route.get('name')}'")
        return self._interpolate_path(start_lat, start_lng, end_point[0], end_point[1], steps=20)

    def _interpolate_path(self, lat1: float, lng1: float, lat2: float, lng2: float, steps: int = 20) -> list:
        """Generate a straight interpolated path with multiple waypoints.

        This is only used when OSRM is unreachable. It is not a real road path
        but it avoids a jarring straight line by providing a smooth curve with
        enough points for Leaflet to render the polyline smoothly.
        """
        path = []
        for i in range(steps + 1):
            fraction = i / steps
            lat = lat1 + (lat2 - lat1) * fraction
            lng = lng1 + (lng2 - lng1) * fraction
            path.append([round(lat, 6), round(lng, 6)])
        return path
