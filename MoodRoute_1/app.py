from flask import Flask, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from config import Config
from backend.database.db import init_db
from backend.routes.mood_api import mood_bp
from backend.routes.route_api import route_bp
from backend.routes.rating_api import rating_bp


def create_app():
    app = Flask(
        __name__,
        template_folder='frontend/templates',
        static_folder='frontend/static'
    )
    app.config.from_object(Config)

    is_production = not Config.DEBUG
    Talisman(
        app,
        force_https=is_production,
        strict_transport_security=is_production,
        content_security_policy={
            'default-src': ["'self'"],
            'script-src':  ["'self'", "'unsafe-inline'", 'unpkg.com'],
            'style-src':   ["'self'", "'unsafe-inline'", 'fonts.googleapis.com', 'unpkg.com'],
            'font-src':    ["'self'", 'fonts.gstatic.com'],
            'img-src':     ["'self'", 'data:', '*.tile.openstreetmap.org',
                            'nominatim.openstreetmap.org'],
            'connect-src': ["'self'",
                            'https://nominatim.openstreetmap.org',
                            'https://router.project-osrm.org',
                            'https://overpass-api.de',
                            'https://api.open-elevation.com',
                            'https://api.openweathermap.org',
                            'https://api.foursquare.com'],
        },
        content_security_policy_nonce_in=['script-src'],
        referrer_policy='no-referrer',
    )

    CORS(app)

    Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[Config.RATE_LIMIT]
    )

    init_db(app)

    app.register_blueprint(mood_bp, url_prefix='/api')
    app.register_blueprint(route_bp, url_prefix='/api')
    app.register_blueprint(rating_bp, url_prefix='/api')

    # Initialize the NLP model synchronously here, before gunicorn forks workers.
    #
    # Why synchronous instead of a background thread:
    #   gunicorn uses fork() to create worker processes. Threads started before
    #   the fork do NOT carry over into worker processes. If we use a thread,
    #   the warmup runs in the master process but each forked worker starts with
    #   _model_available = None and hits _load_model() on the first request.
    #
    # With TRANSFORMERS_OFFLINE=1 set on Render, this call returns in <1ms
    # because it detects offline mode immediately and sets _model_available=False.
    # No network calls, no timeout, no gunicorn worker kill.
    #
    # With the model cached locally (dev environment), this loads from disk.
    from backend.services.nlp_service import MoodDetector
    MoodDetector().initialize()

    @app.route('/')
    def index():
        return render_template('index.html')

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)