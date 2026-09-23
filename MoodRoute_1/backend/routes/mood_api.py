"""Mood detection API endpoint."""
from flask import Blueprint, request, jsonify
import bleach
from backend.services.nlp_service import MoodDetector
from config import Config

mood_bp = Blueprint('mood', __name__)
mood_detector = MoodDetector()


@mood_bp.route('/detect-mood', methods=['POST'])
def detect_mood():
    """Detect mood from text input."""
    request_data = request.get_json()

    if not request_data or 'text' not in request_data:
        return jsonify({'error': 'Missing text field'}), 400

    raw_text = request_data['text']
    sanitized_text = bleach.clean(raw_text, tags=[], strip=True)[:Config.MAX_INPUT_LENGTH]

    if len(sanitized_text.strip()) < 3:
        return jsonify({'error': 'Text too short. Please describe how you feel.'}), 400

    detection_result = mood_detector.detect(sanitized_text)

    return jsonify({
        'success': True,
        'input_text': sanitized_text,
        'detected_emotion': detection_result['detected_emotion'],
        'mood_category': detection_result['mood_category'],
        'confidence': detection_result['confidence'],
        'description': detection_result['description'],
        'all_scores': detection_result['all_scores']
    })
