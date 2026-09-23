"""Greenery scoring using OpenStreetMap Overpass API.

Queries green features (parks, forests, gardens, trees) near route coordinates.
"""
import requests
from backend.database.db import get_cached_score, set_cached_score


class GreeneryService:
    OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

    def get_greenery_score(self, route_id: int, route_coords: list) -> float:
        """Calculate greenery score (0-10) for a route."""
        cached_score = get_cached_score(route_id, 'greenery')
        if cached_score is not None:
            return cached_score

        midpoint_index = len(route_coords) // 2
        midpoint_lat = route_coords[midpoint_index][0]
        midpoint_lon = route_coords[midpoint_index][1]

        greenery_score = self._query_overpass(midpoint_lat, midpoint_lon)

        set_cached_score(route_id, 'greenery', greenery_score, ttl_hours=24)
        return greenery_score

    def _query_overpass(self, latitude: float, longitude: float) -> float:
        """Query Overpass API for green features within 300m radius."""
        query = f"""
        [out:json][timeout:10];
        (
          way["leisure"="park"](around:300,{latitude},{longitude});
          way["landuse"="forest"](around:300,{latitude},{longitude});
          way["landuse"="grass"](around:300,{latitude},{longitude});
          way["natural"="wood"](around:300,{latitude},{longitude});
          node["natural"="tree"](around:300,{latitude},{longitude});
          way["leisure"="garden"](around:300,{latitude},{longitude});
          way["landuse"="recreation_ground"](around:300,{latitude},{longitude});
        );
        out count;
        """

        try:
            response = requests.post(
                self.OVERPASS_URL,
                data={'data': query},
                timeout=15,
                headers={'User-Agent': 'MoodRoute/1.0'}
            )
            response.raise_for_status()
            response_data = response.json()

            feature_count = 0
            if response_data.get('elements'):
                tags = response_data['elements'][0].get('tags', {})
                feature_count = int(tags.get('total', 0))

            # Normalize: 0 features = 0, 40+ features = 10
            max_green_features = 40
            score = min(10.0, (feature_count / max_green_features) * 10)
            return round(score, 1)

        except Exception as overpass_error:
            print(f'[Greenery] Overpass error: {overpass_error}')
            return 5.0
