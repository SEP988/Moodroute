"""Noise estimation using OpenStreetMap road classification.

Estimates noise levels based on highway types near a route.
"""
import requests
from backend.database.db import get_cached_score, set_cached_score


class NoiseService:
    OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

    # Noise levels by road type (0 = silent, 10 = extremely loud)
    ROAD_NOISE_LEVELS = {
        'motorway': 10, 'motorway_link': 9,
        'trunk': 9, 'trunk_link': 8,
        'primary': 8, 'primary_link': 7,
        'secondary': 6, 'secondary_link': 5,
        'tertiary': 4, 'tertiary_link': 3,
        'unclassified': 3,
        'residential': 2,
        'service': 2, 'living_street': 1,
        'pedestrian': 0, 'footway': 0,
        'path': 0, 'cycleway': 1,
        'track': 1, 'steps': 0
    }

    def get_quietness_score(self, route_id: int, route_coords: list) -> float:
        """Calculate quietness score (0-10) for a route. High = very quiet."""
        cached_score = get_cached_score(route_id, 'quiet')
        if cached_score is not None:
            return cached_score

        midpoint_index = len(route_coords) // 2
        midpoint_lat = route_coords[midpoint_index][0]
        midpoint_lon = route_coords[midpoint_index][1]

        quietness_score = self._query_road_types(midpoint_lat, midpoint_lon)
        set_cached_score(route_id, 'quiet', quietness_score, ttl_hours=24)
        return quietness_score

    def _query_road_types(self, latitude: float, longitude: float) -> float:
        """Query OSM for road types near coordinate, compute average noise, invert to quietness."""
        query = f"""
        [out:json][timeout:10];
        way["highway"](around:200,{latitude},{longitude});
        out tags;
        """

        try:
            response = requests.post(
                self.OVERPASS_URL,
                data={'data': query},
                timeout=15,
                headers={'User-Agent': 'MoodRoute/1.0'}
            )
            response.raise_for_status()
            road_data = response.json()

            noise_values = []
            for element in road_data.get('elements', []):
                highway_type = element.get('tags', {}).get('highway', '')
                if highway_type in self.ROAD_NOISE_LEVELS:
                    noise_values.append(self.ROAD_NOISE_LEVELS[highway_type])

            if noise_values:
                average_noise = sum(noise_values) / len(noise_values)
                quietness = 10.0 - average_noise
                return round(max(0, min(10, quietness)), 1)

        except Exception as overpass_error:
            print(f'[Noise] Overpass error: {overpass_error}')

        return 5.0
