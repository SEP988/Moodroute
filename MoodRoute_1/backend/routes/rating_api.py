"""Rating API endpoint."""
from flask import Blueprint, request, jsonify
from backend.database.db import save_rating

rating_bp = Blueprint('rating', __name__)


@rating_bp.route('/rate', methods=['POST'])
def rate_walk():
    """Save a post-walk rating."""
    request_data = request.get_json()

    if not request_data:
        return jsonify({'error': 'Missing request body'}), 400

    route_id = request_data.get('route_id')
    mood = request_data.get('mood')
    rating = request_data.get('rating')

    if not all([route_id, mood, rating]):
        return jsonify({'error': 'Missing required fields: route_id, mood, rating'}), 400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    weather_condition = request_data.get('weather_condition', '')

    try:
        save_rating(route_id, mood, rating, weather_condition)
        return jsonify({
            'success': True,
            'message': f'Rating of {rating}/5 saved successfully'
        })
    except Exception as save_error:
        return jsonify({'error': f'Failed to save rating: {str(save_error)}'}), 500
