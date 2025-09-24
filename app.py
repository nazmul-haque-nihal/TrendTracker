# app.py
import os
from flask import Flask
from flask_cors import CORS
from backend import db
from backend.api.routes import api_bp
from backend.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure CORS
    frontend_origin = os.environ.get('FRONTEND_URL', 'http://localhost:8000')
    CORS(app, resources={
        r"/api/*": {
            "origins": [frontend_origin, "http://localhost:8000", "https://*.onrender.com"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def home():
        return "TrendTracker API is running"

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) # Set debug=False for production