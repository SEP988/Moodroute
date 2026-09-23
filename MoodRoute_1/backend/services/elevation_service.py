"""Elevation and flatness scoring using Open-Elevation API.

Calculates total elevation gain along a route to determine flatness.
"""
import requests
from backend.database.db import get_cached_score, set_cached_score


class ElevationService:
    API_URL = 'https://api.open-elevation.com/api/v1/lookup'

    def get_flatness_score(self, route_id: int, route_coords: list) -> float:
        """Calculate flatness score (0-10). 10 = perfectly flat, 0 = very steep."""
        cached_score = get_cached_score(route_id, 'flat')
        if cached_score is not None:
            return cached_score

        flatness_score = self._calculate_flatness(route_coords)
        set_cached_score(route_id, 'flat', flatness_score, ttl_hours=48)
        return flatness_score

    def _calculate_flatness(self, route_coords: list) -> float:
        """Fetch elevation profile and compute flatness from total gain."""
        # Sample up to 15 points along route
        sample_step = max(1, len(route_coords) // 15)
        sampled_points = route_coords[::sample_step]

        locations = [{'latitude': point[0], 'longitude': point[1]} for point in sampled_points]

        try:
            response = requests.post(
                self.API_URL,
                json={'locations': locations},
                timeout=15,
                headers={'Content-Type': 'application/json', 'User-Agent': 'MoodRoute/1.0'}
            )
            response.raise_for_status()
            elevation_data = response.json()
            elevations = [result['elevation'] for result in elevation_data['results']]

            if len(elevations) < 2:
                return 5.0

            total_elevation_gain = sum(
                max(0, elevations[i + 1] - elevations[i])
                for i in range(len(elevations) - 1)
            )

            # Normalize: 0m gain = 10 (flat), 100m+ gain = 0 (very hilly)
            flatness = max(0, 10 - (total_elevation_gain / 10))
            return round(min(10, flatness), 1)

        except Exception as elevation_error:
            print(f'[Elevation] API error: {elevation_error}')
            return 5.0
