"""Crowd density estimation using Foursquare Places API.

Counts venues near a route to estimate pedestrian density.
"""
import requests
from config import Config
from backend.database.db import get_cached_score, set_cached_score


class CrowdService:
    BASE_URL = 'https://api.foursquare.com/v3/places/search'

    def get_uncrowded_score(self, route_id: int, route_coords: list) -> float:
        """Calculate uncrowded score (0-10). 10 = empty, 0 = very crowded."""
        cached_score = get_cached_score(route_id, 'uncrowded')
        if cached_score is not None:
            return cached_score

        midpoint_index = len(route_coords) // 2
        midpoint_lat = route_coords[midpoint_index][0]
        midpoint_lon = route_coords[midpoint_index][1]

        uncrowded_score = self._query_foursquare(midpoint_lat, midpoint_lon)
        set_cached_score(route_id, 'uncrowded', uncrowded_score, ttl_hours=6)
        return uncrowded_score

    def _query_foursquare(self, latitude: float, longitude: float) -> float:
        """Count venues within 300m to estimate crowd density."""
        api_key = Config.FOURSQUARE_API_KEY

        if not api_key or api_key == 'your_foursquare_key_here':
            return self._estimate_from_area_type(latitude, longitude)

        try:
            headers = {
                'Authorization': api_key,
                'Accept': 'application/json'
            }
            request_params = {
                'll': f'{latitude},{longitude}',
                'radius': 300,
                'limit': 50
            }

            response = requests.get(self.BASE_URL, headers=headers, params=request_params, timeout=10)
            response.raise_for_status()
            venue_data = response.json()

            venue_count = len(venue_data.get('results', []))

            # Normalize: 0 venues = 10, 30+ venues = 0
            score = max(0, 10 - (venue_count / 3))
            return round(score, 1)

        except Exception as foursquare_error:
            print(f'[Crowd] Foursquare error: {foursquare_error}')
            return self._estimate_from_area_type(latitude, longitude)

    def _estimate_from_area_type(self, latitude: float, longitude: float) -> float:
        """Fallback: estimate crowd based on distance from Wollongong CBD."""
        cbd_latitude, cbd_longitude = -34.4278, 150.8931
        distance_from_cbd = ((latitude - cbd_latitude) ** 2 + (longitude - cbd_longitude) ** 2) ** 0.5

        if distance_from_cbd < 0.005:
            return 3.0
        elif distance_from_cbd < 0.015:
            return 5.5
        elif distance_from_cbd < 0.03:
            return 7.0
        else:
            return 8.5
