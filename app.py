# app.py
import os
from flask import Flask
from flask_cors import CORS
from backend import db
from backend.api.routes import api_bp
from backend.config import Config
# Import for scheduler (add this if you want the scheduler, otherwise remove the scheduler code block)
from apscheduler.schedulers.background import BackgroundScheduler
import atexit # For scheduler shutdown
from backend.scrapers.scraper_manager import ScraperManager # Import for scheduler
from backend.models.trend_model import Trend # Import for scheduler

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure CORS - THIS LINE AND THE BLOCK BELOW MUST BE CORRECTLY INDENTED
    frontend_origin = os.environ.get('FRONTEND_URL', 'http://localhost:8000')
    CORS(app, resources={
        r"/api/*": {
            "origins": [frontend_origin, "http://localhost:8000", "https://trendtracker-frontend.onrender.com", "https://trendtracker-046o.onrender.com"], # REMOVED TRAILING SPACES
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Initialize the database extension with the app - THIS LINE MUST BE CORRECTLY INDENTED
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    # --- Scheduler Setup (Optional) ---
    # Only include this block if you want automatic scraping
    # Remove this block if you only want manual scraping via the button
    if not app.config.get('TESTING'): # Don't run scheduler if in testing mode
        scheduler = BackgroundScheduler()

        def scheduled_scrape():
            """Function to run the scraping job."""
            print("Scheduler: Starting scheduled scrape...")
            scraper_manager = ScraperManager() # Create manager inside the function
            all_trends = []
            enabled_platforms = scraper_manager.get_enabled_platforms()
            for platform in enabled_platforms:
                try:
                    trends = scraper_manager.get_trends(platform, limit=10) # Adjust limit as needed
                    all_trends.extend(trends)
                    print(f"Scheduler: Scraped {len(trends)} trends from {platform}")
                except Exception as e:
                    print(f"Scheduler: Error scraping {platform}: {e}")

            # Save trends to database (similar logic to /scrape route)
            saved_count = 0
            for trend_data in all_trends:
                # Check if trend already exists (by platform_id and platform)
                existing_trend = Trend.query.filter_by(platform_id=trend_data.platform_id, platform=trend_data.platform).first()
                if not existing_trend:
                    db.session.add(trend_data)
                    saved_count += 1
                else:
                    print(f"Scheduler: Skipping duplicate trend: {trend_data.title[:50]}... (ID: {trend_data.platform_id})")

            try:
                db.session.commit()
                print(f"Scheduler: Committed {saved_count} new trends to database.")
            except Exception as e:
                db.session.rollback()
                print(f"Scheduler: Error committing trends to database: {e}")

        # Schedule the job to run every 6 hours
        scheduler.add_job(
            func=scheduled_scrape,
            trigger="interval",
            hours=6, # Run every 6 hours (adjust as needed)
            id='scrape_trends_job',
            name='Scrape trends from all enabled platforms',
            replace_existing=True
        )

        scheduler.start()
        print("Scheduler: Started.")

        # Shut down the scheduler when the application exits
        atexit.register(lambda: scheduler.shutdown())

    @app.route('/')
    def home():
        return "TrendTracker API is running"

    return app

# Create the application instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    # This block runs only if you execute `python app.py` locally
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) # Set debug=False for production