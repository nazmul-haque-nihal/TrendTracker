# backend/scrapers/scraper_manager.py
from backend.scrapers.youtube_scraper import YouTubeScraper
from backend.scrapers.reddit_scraper import RedditScraper
# Add other scrapers when implemented
# from backend.scrapers.twitter_scraper import TwitterScraper
# from backend.scrapers.tiktok_scraper import TikTokScraper

class ScraperManager:
    def __init__(self):
        self.scrapers = {
            'youtube': YouTubeScraper(),
            'reddit': RedditScraper(),
            # 'twitter': TwitterScraper(),
            # 'tiktok': TikTokScraper(),
            # Add other scrapers here
        }
        # Determine enabled platforms based on config or environment variables
        self.enabled_platforms = self._get_enabled_platforms()

    def _get_enabled_platforms(self):
        """Determine enabled platforms based on API keys."""
        enabled = []
        for platform, api_config in self.scrapers.items():
            # Assume each scraper has a method to check if its API is configured
            if api_config.is_configured():
                enabled.append(platform)
        return enabled

    def get_enabled_platforms(self):
        """Return list of enabled platform names."""
        return self.enabled_platforms

    def get_trends(self, platform, limit=10):
        """Get trends from a specific platform."""
        if platform in self.scrapers and platform in self.enabled_platforms:
            scraper = self.scrapers[platform]
            try:
                return scraper.get_trending_videos(limit)
            except Exception as e:
                print(f"Error scraping {platform}: {e}")
                import traceback
                traceback.print_exc()
                return []
        else:
            print(f"Platform {platform} is not enabled or scraper not found.")
            return []