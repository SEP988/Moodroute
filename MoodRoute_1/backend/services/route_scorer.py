"""Route Scoring Algorithm using Weighted Linear Combination (WLC).

Scores walking routes based on environmental factors weighted by mood.
Formula: Score = [w1*Greenery + w2*Quietness + w3*Flatness + w4*Distance + w5*Uncrowded] / 5
"""
import math
from backend.models.mood_mapper import MOOD_CONFIG
from backend.services.greenery_service import GreeneryService
from backend.services.noise_service import NoiseService
from backend.services.elevation_service import ElevationService
from backend.services.crowd_service import CrowdService


class RouteScorer:
    def __init__(self):
        self.greenery_service = GreeneryService()
        self.noise_service = NoiseService()
        self.elevation_service = ElevationService()
        self.crowd_service = CrowdService()

    def score_route(self, route: dict, mood: str, weather_data: dict = None) -> dict:
        """Score a single route for a given mood using weighted linear combination."""
        mood_config = MOOD_CONFIG.get(mood, MOOD_CONFIG['neutral'])
        mood_weights = mood_config['weights']
        route_id = route['id']
        route_coordinates = route['coordinates']

        greenery_score = route.get('score_greenery', 5.0)
        quietness_score = route.get('score_quietness', 5.0)
        flatness_score = route.get('score_flatness', 5.0)
        uncrowded_score = route.get('score_uncrowded', 5.0)

        distance_score = self._calculate_distance_score(route['distance_km'], mood)

        weighted_total = (
            mood_weights['greenery'] * greenery_score +
            mood_weights['quiet'] * quietness_score +
            mood_weights['flat'] * flatness_score +
            mood_weights['distance'] * distance_score +
            mood_weights['uncrowded'] * uncrowded_score
        ) / 5

        weather_modifier = 1.0
        if weather_data:
            weather_condition = weather_data.get('condition', 'Clear')
            temperature = weather_data.get('temp', 20)
            if weather_condition in ['Thunderstorm', 'Tornado', 'Snow']:
                weighted_total = 0
                weather_modifier = 0
            elif weather_condition in ['Rain', 'Drizzle']:
                weather_modifier = 0.6
                weighted_total *= weather_modifier
            elif weather_condition == 'Clear' and 15 <= temperature <= 28:
                weather_modifier = 1.05
                weighted_total *= weather_modifier

        final_score = round(min(10, max(0, weighted_total)), 2)

        explanation = self._build_explanation(
            mood, greenery_score, quietness_score, flatness_score, uncrowded_score, mood_weights
        )

        return {
            'total_score': final_score,
            'scores': {
                'greenery': round(greenery_score, 1),
                'quietness': round(quietness_score, 1),
                'flatness': round(flatness_score, 1),
                'distance': round(distance_score, 1),
                'uncrowded': round(uncrowded_score, 1),
            },
            'weights_used': mood_weights,
            'weather_modifier': weather_modifier,
            'explanation': explanation
        }

    def score_routes(self, routes: list, mood: str, weather_data: dict = None) -> list:
        """Score multiple routes and return sorted by score (highest first)."""
        scored_routes = []
        for route in routes:
            score_result = self.score_route(route, mood, weather_data)
            scored_routes.append({**route, 'score_data': score_result})

        scored_routes.sort(key=lambda r: r['score_data']['total_score'], reverse=True)
        return scored_routes

    def _calculate_distance_score(self, route_distance_km: float, mood: str) -> float:
        """Score how well route distance matches mood preference using Gaussian falloff."""
        mood_config = MOOD_CONFIG.get(mood, MOOD_CONFIG['neutral'])
        ideal_min, ideal_max = mood_config['ideal_distance']
        ideal_range = ideal_max - ideal_min

        if ideal_min <= route_distance_km <= ideal_max:
            return 10.0

        if route_distance_km < ideal_min:
            deviation = ideal_min - route_distance_km
        else:
            deviation = route_distance_km - ideal_max

        score = 10.0 * math.exp(-(deviation ** 2) / (2 * (ideal_range ** 2)))
        return round(max(0, min(10, score)), 1)

    def _build_explanation(self, mood, greenery_score, quietness_score, flatness_score, uncrowded_score, mood_weights):
        """Build a human-readable explanation of why this route suits the mood."""
        factors = []

        if mood_weights['greenery'] >= 0.7 and greenery_score >= 7.5:
            factors.append('surrounded by greenery and nature')
        if mood_weights['quiet'] >= 0.7 and quietness_score >= 7.5:
            factors.append('very quiet with minimal noise')
        if mood_weights['flat'] >= 0.7 and flatness_score >= 8.0:
            factors.append('flat and easy to walk')
        if mood_weights['uncrowded'] >= 0.7 and uncrowded_score >= 8.0:
            factors.append('secluded with very few people')
        if mood_weights['distance'] >= 0.7:
            factors.append('the perfect length for your energy level')
        if mood_weights['greenery'] < 0.4 and mood_weights['distance'] >= 0.8:
            factors.append('long and physically stimulating')

        if factors:
            return f"This route is {', '.join(factors)} — well suited to your {mood} mood."
        return f"This route offers a balanced environment well suited to your {mood} mood."
