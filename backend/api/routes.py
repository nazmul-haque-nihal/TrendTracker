# backend/api/routes.py
from flask import Blueprint, jsonify, request
from backend.scrapers.scraper_manager import ScraperManager
from backend.models.trend_model import Trend
from backend import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/trends', methods=['GET'])
def get_trends():
    try:
        # Get query parameters
        platform = request.args.get('platform')
        category = request.args.get('category')
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)

        # Build query
        query = Trend.query

        if platform:
            query = query.filter(Trend.platform == platform)
        if category:
            query = query.filter(Trend.category.ilike(f'%{category}%')) # Case-insensitive partial match

        # Order by engagement score (descending) and published date (descending)
        query = query.order_by(Trend.engagement_score.desc(), Trend.published_at.desc())

        # Apply limit and offset for pagination
        trends = query.offset(offset).limit(limit).all()

        return jsonify([trend.to_dict() for trend in trends])
    except Exception as e:
        print(f"Error fetching trends: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/scrape', methods=['POST'])
def scrape_trends():
    try:
        scraper_manager = ScraperManager()
        data = request.get_json() or {}
        platforms = data.get('platforms') # e.g., ["youtube"]
        limit_per_platform = data.get('limit_per_platform', 10)

        all_trends = []

        if not platforms:
             platforms = scraper_manager.get_enabled_platforms()

        print(f"Scraping requested for platforms: {platforms}")

        for platform in platforms:
            if platform in scraper_manager.get_enabled_platforms():
                print(f"Calling scraper for platform: {platform}")
                trends = scraper_manager.get_trends(platform, limit_per_platform)
                print(f"Scraper returned {len(trends)} trends for {platform}.")
                all_trends.extend(trends)
            else:
                 print(f"Platform {platform} is not enabled.")

        saved_count = 0
        for trend_data in all_trends:
            # Check if trend already exists (by platform_id and platform)
            existing_trend = Trend.query.filter_by(platform_id=trend_data.platform_id, platform=trend_data.platform).first()
            if not existing_trend:
                print(f"Saving new trend: {trend_data.title[:50]}... (ID: {trend_data.platform_id})")
                db.session.add(trend_data)
                saved_count += 1
            else:
                 print(f"Skipping duplicate trend in DB: {trend_data.title[:50]}... (ID: {trend_data.platform_id})")

        db.session.commit()
        print(f"Committed {saved_count} new trends to database.")

        return jsonify({
            'message': f'Successfully scraped and saved {saved_count} new trends',
            'trends_scraped': len(all_trends),
            'trends_saved': saved_count,
            'platforms_scraped': len([p for p in platforms if p in scraper_manager.get_enabled_platforms()])
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in scrape_trends route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error during scraping: {str(e)}'}), 500

@api_bp.route('/config', methods=['GET'])
def get_config():
    scraper_manager = ScraperManager()
    # Return configuration options based on scraper manager's enabled platforms
    enabled_platforms = scraper_manager.get_enabled_platforms()
    config = {
        'platforms': {
            'youtube': {'enabled': 'youtube' in enabled_platforms},
            'reddit': {'enabled': 'reddit' in enabled_platforms},
            'twitter': {'enabled': 'twitter' in enabled_platforms},
            'tiktok': {'enabled': 'tiktok' in enabled_platforms},
        },
        'scheduler_enabled': False,
        'scheduler_interval': 3600,
        'debug': True
    }
    return jsonify(config)

# Endpoint to test a specific platform's API connection
@api_bp.route('/config/test', methods=['POST'])
def test_api():
    data = request.get_json() or {}
    platform = data.get('platform')

    if platform == 'youtube':
        api_key = Config.PLATFORM_APIS['youtube'].get('api_key')
        if api_key:
            try:
                response = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q=test&key={api_key}")
                response.raise_for_status()
                if response.json().get('items'):
                    return jsonify({'message': 'YouTube API connection successful!'}), 200
                else:
                    return jsonify({'error': 'YouTube API connection failed - no items returned.'}), 400
            except Exception as e:
                return jsonify({'error': f'YouTube API connection failed: {str(e)}'}), 400
        else:
            return jsonify({'error': 'YouTube API key not configured.'}), 400
    elif platform == 'reddit':
        # Test Reddit connection by fetching user info (already done in __init__)
        api_config = Config.PLATFORM_APIS.get('reddit', {})
        client_id = api_config.get('client_id')
        client_secret = api_config.get('client_secret')
        if client_id and client_secret:
            try:
                reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent="TrendTracker/1.0 by TestUser"
                )
                _ = reddit.user.me() # This will raise an exception if invalid
                return jsonify({'message': 'Reddit API connection successful!'}), 200
            except Exception as e:
                return jsonify({'error': f'Reddit API connection failed: {str(e)}'}), 400
        else:
            return jsonify({'error': 'Reddit API credentials not configured.'}), 400
    else:
        return jsonify({'error': f'Testing for platform {platform} is not implemented.'}), 400
