"""Route recommendation API endpoint."""
from flask import Blueprint, request, jsonify
import bleach
from backend.services.nlp_service import MoodDetector
from backend.services.weather_service import WeatherService
from backend.services.route_scorer import RouteScorer
from backend.services.osrm_service import OSRMService
from backend.database.db import get_routes_near
from backend.models.mood_mapper import get_mood_config, get_all_moods
from config import Config

route_bp = Blueprint('route', __name__)
mood_detector = MoodDetector()
weather_service = WeatherService()
route_scorer = RouteScorer()
osrm_service = OSRMService()

# All routes are searched relative to University of Wollongong campus
UOW_CENTER_LAT = -34.4054
UOW_CENTER_LNG = 150.8784
UOW_SEARCH_RADIUS_KM = 5.0


@route_bp.route('/find-route', methods=['POST'])
def find_route():
    """Find best walking route based on mood.

    Routes are always searched within 5km of UOW campus center.
    User location is used for weather only.
    """
    request_data = request.get_json()

    if not request_data:
        return jsonify({'error': 'Missing request body'}), 400

    user_latitude = request_data.get('lat', UOW_CENTER_LAT)
    user_longitude = request_data.get('lng', UOW_CENTER_LNG)

    try:
        user_latitude = float(user_latitude)
        user_longitude = float(user_longitude)
        if not (-90 <= user_latitude <= 90) or not (-180 <= user_longitude <= 180):
            user_latitude, user_longitude = UOW_CENTER_LAT, UOW_CENTER_LNG
    except (ValueError, TypeError):
        user_latitude, user_longitude = UOW_CENTER_LAT, UOW_CENTER_LNG

    provided_mood = request_data.get('mood')
    if provided_mood and provided_mood in get_all_moods():
        mood_category = provided_mood
        confidence = 0.95
        detected_emotion = provided_mood
    elif request_data.get('text'):
        sanitized_text = bleach.clean(request_data['text'], tags=[], strip=True)[:Config.MAX_INPUT_LENGTH]
        if len(sanitized_text.strip()) < 3:
            return jsonify({'error': 'Text too short'}), 400
        detection_result = mood_detector.detect(sanitized_text)
        mood_category = detection_result['mood_category']
        confidence = detection_result['confidence']
        detected_emotion = detection_result['detected_emotion']
    else:
        return jsonify({'error': 'Provide either text or mood'}), 400

    current_weather = weather_service.get_weather(user_latitude, user_longitude)

    if current_weather['walkable'] == 'dangerous':
        return jsonify({
            'success': True,
            'mood_category': mood_category,
            'confidence': confidence,
            'weather': current_weather,
            'indoor_alternatives': True,
            'message': 'Weather is too dangerous for outdoor walking.',
            'alternatives': _get_indoor_alternatives()
        })

    nearby_routes = get_routes_near(UOW_CENTER_LAT, UOW_CENTER_LNG, radius_km=UOW_SEARCH_RADIUS_KM)

    if not nearby_routes:
        return jsonify({'error': 'No routes found near University of Wollongong'}), 404

    scored_routes = route_scorer.score_routes(nearby_routes, mood_category, current_weather)

    top_routes = scored_routes[:3]
    mood_config = get_mood_config(mood_category)

    # Fetch real walking paths for all 3 routes in parallel instead of sequentially.
    # Sequential: 3 x ~500ms = ~1500ms. Parallel: ~500ms total.
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def fetch_route_with_path(route):
        real_walking_path = osrm_service.get_path_for_route(route)
        return {
            'id': route['id'],
            'name': route['name'],
            'description': route['description'],
            'distance_km': route['distance_km'],
            'area_type': route['area_type'],
            'coordinates': real_walking_path,
            'start_point': route.get('start_point', 'Start'),
            'end_point': route.get('end_point', 'End'),
            'total_score': route['score_data']['total_score'],
            'scores': route['score_data']['scores'],
            'explanation': route['score_data']['explanation']
        }

    response_routes = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_route = {
            executor.submit(fetch_route_with_path, route): route
            for route in top_routes
        }
        # Collect results and preserve ranking order
        ranked_results = {id(route): None for route in top_routes}
        for future in as_completed(future_to_route):
            original_route = future_to_route[future]
            ranked_results[id(original_route)] = future.result()

        response_routes = [ranked_results[id(route)] for route in top_routes]

    return jsonify({
        'success': True,
        'mood': {
            'category': mood_category,
            'emotion': detected_emotion,
            'confidence': confidence,
            'emoji': mood_config['emoji'],
            'label': mood_config['label'],
            'description': mood_config['description']
        },
        'weather': current_weather,
        'routes': response_routes,
        'indoor_alternatives': current_weather['walkable'] == 'poor'
    })


@route_bp.route('/weather', methods=['GET'])
def get_weather():
    """Get current weather for coordinates (defaults to UOW)."""
    latitude = request.args.get('lat', type=float, default=UOW_CENTER_LAT)
    longitude = request.args.get('lng', type=float, default=UOW_CENTER_LNG)

    current_weather = weather_service.get_weather(latitude, longitude)
    return jsonify({'success': True, 'weather': current_weather})


def _get_indoor_alternatives():
    return [
        {'icon': '🏋️', 'name': 'UOW UniActive Gym', 'description': 'Full gym facilities on campus'},
        {'icon': '📚', 'name': 'UOW Library (Building 16)', 'description': 'Quiet floors for reflection and study'},
        {'icon': '☕', 'name': 'UniBar or Campus Café', 'description': 'Warm space to sit and decompress'},
        {'icon': '🧘', 'name': 'UOW Recreation Hall', 'description': 'Indoor yoga and meditation sessions'},
        {'icon': '🎮', 'name': 'UniCentre Games Room', 'description': 'Social indoor activity space'}
    ]
