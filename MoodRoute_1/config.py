import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-me')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    FOURSQUARE_API_KEY = os.getenv('FOURSQUARE_API_KEY', '')
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'moodroute.db')
    RATE_LIMIT = '30 per minute'
    MAX_INPUT_LENGTH = 500
