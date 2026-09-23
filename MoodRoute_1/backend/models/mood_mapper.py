"""Mood configuration and weight mappings for route scoring.

Each mood has specific weights and ideal distances that produce unique
route recommendations from the pre-seeded Wollongong routes.
"""

MOOD_CONFIG = {
    'stressed': {
        'emoji': '😰',
        'label': 'Stressed',
        'color': '#e74c3c',
        'weights': {
            'greenery': 0.90,
            'quiet': 0.75,
            'flat': 0.65,
            'distance': 0.55,
            'uncrowded': 0.65
        },
        'ideal_distance': (1.5, 2.5),
        'description': 'Quiet, green routes at a gentle pace to help you decompress'
    },
    'anxious': {
        'emoji': '😟',
        'label': 'Anxious',
        'color': '#e67e22',
        'weights': {
            'greenery': 0.70,
            'quiet': 0.98,
            'flat': 0.80,
            'distance': 0.20,
            'uncrowded': 0.98
        },
        'ideal_distance': (0.5, 1.2),
        'description': 'Very quiet, very secluded short paths with minimal stimulation'
    },
    'tired': {
        'emoji': '😴',
        'label': 'Tired',
        'color': '#8e44ad',
        'weights': {
            'greenery': 0.50,
            'quiet': 0.60,
            'flat': 0.98,
            'distance': 0.30,
            'uncrowded': 0.55
        },
        'ideal_distance': (0.7, 1.5),
        'description': 'Short, flat, gentle walks to restore your energy'
    },
    'sad': {
        'emoji': '😢',
        'label': 'Sad',
        'color': '#2980b9',
        'weights': {
            'greenery': 0.98,
            'quiet': 0.55,
            'flat': 0.60,
            'distance': 0.65,
            'uncrowded': 0.40
        },
        'ideal_distance': (2.5, 4.0),
        'description': 'Nature-rich, immersive routes to lift your spirits'
    },
    'happy': {
        'emoji': '😊',
        'label': 'Happy',
        'color': '#27ae60',
        'weights': {
            'greenery': 0.05,
            'quiet': 0.20,
            'flat': 0.55,
            'distance': 0.90,
            'uncrowded': 0.30
        },
        'ideal_distance': (3.5, 5.5),
        'description': 'Scenic, enjoyable longer routes to celebrate your mood'
    },
    'energetic': {
        'emoji': '⚡',
        'label': 'Energetic',
        'color': '#f39c12',
        'weights': {
            'greenery': 0.20,
            'quiet': 0.10,
            'flat': 0.10,
            'distance': 0.98,
            'uncrowded': 0.30
        },
        'ideal_distance': (5.0, 7.5),
        'description': 'Long, challenging routes to channel your energy'
    },
    'neutral': {
        'emoji': '😐',
        'label': 'Neutral',
        'color': '#7f8c8d',
        'weights': {
            'greenery': 0.50,
            'quiet': 0.50,
            'flat': 0.50,
            'distance': 0.50,
            'uncrowded': 0.50
        },
        'ideal_distance': (1.5, 3.0),
        'description': 'Balanced, well-rounded walking routes'
    }
}


def get_mood_config(mood: str) -> dict:
    return MOOD_CONFIG.get(mood, MOOD_CONFIG['neutral'])


def get_all_moods() -> dict:
    return MOOD_CONFIG
