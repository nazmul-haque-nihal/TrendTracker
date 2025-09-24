# backend/scrapers/reddit_scraper.py
import praw
from datetime import datetime, timedelta
from backend.models.trend_model import Trend
from backend.config import Config

class RedditScraper:
    def __init__(self):
        api_config = Config.PLATFORM_APIS.get('reddit', {})
        self.client_id = api_config.get('client_id')
        self.client_secret = api_config.get('client_secret')
        self.user_agent = "TrendTracker/1.0 by YourUsername" # Replace with your Reddit username

        if self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                # Test connection
                _ = self.reddit.user.me()
                print("[RedditScraper] Successfully authenticated with Reddit API.")
            except Exception as e:
                print(f"[RedditScraper] Error authenticating with Reddit API: {e}")
                self.reddit = None
        else:
            print("[RedditScraper] Warning: Reddit API credentials not configured.")
            self.reddit = None

    def is_configured(self):
        """Check if the scraper has the necessary API keys."""
        return bool(self.client_id and self.client_secret and self.reddit)

    def get_trending_videos(self, limit=20):
        """Get trending posts from Reddit that might be videos."""
        if not self.reddit:
            print("[RedditScraper] Cannot scrape, Reddit API not configured or authenticated.")
            return []

        trends = []
        try:
            # Search for posts that might contain videos in popular subreddits
            # This is a basic search; you might want to target specific subreddits
            search_terms = [
                "video", "funny video", "sad video", "emotional video", "anime video",
                "movie clip", "music video", "dance video", "technology video"
            ]

            seen_urls = set()
            for term in search_terms:
                if len(trends) >= limit:
                    break
                print(f"[RedditScraper] Searching Reddit for: {term}")
                # Search within the last 7 days
                start_time = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
                search_query = f"{term} timestamp:{start_time}..now"
                # Note: PRAW doesn't directly support timestamp in search, this is a limitation
                # A better approach might be to fetch hot/new posts from specific subreddits
                # For now, we'll search globally for the term
                posts = self.reddit.subreddit("all").search(term, limit=limit//len(search_terms))
                for post in posts:
                    if len(trends) >= limit:
                        break
                    # Check if post is a video link or hosted video
                    if post.url and post.url not in seen_urls:
                        if post.url.endswith(('.mp4', '.mov', '.avi', '.webm', '.gif')) or 'v.redd.it' in post.url:
                            trend = self._parse_post_data(post)
                            if trend:
                                trends.append(trend)
                                seen_urls.add(post.url)
                                print(f"[RedditScraper] Added: {trend.title[:40]}... from r/{post.subreddit.display_name}")
        except Exception as e:
            print(f"[RedditScraper] Error fetching trends: {e}")
            import traceback
            traceback.print_exc()

        print(f"[RedditScraper] === COMPLETED. Final trends list size: {len(trends)} ===")
        return trends

    def _parse_post_data(self, post):
        """Parse PRAW post object into a Trend object."""
        try:
            # Determine URL (might be self-post text or link)
            url = post.url if not post.is_self else f"https://reddit.com{post.permalink}"
            # Determine thumbnail (use post's thumbnail, or a default)
            thumbnail_url = post.thumbnail if post.thumbnail and post.thumbnail != 'self' else ''
            # Determine author
            author = str(post.author) if post.author else 'Deleted'

            # Calculate engagement score (upvotes + comments)
            engagement_score = post.score + post.num_comments

            # Create Trend object
            trend = Trend(
                title=post.title[:255],
                description=post.selftext[:500] if post.is_self else f"Link post to: {post.url}",
                url=url,
                platform='reddit',
                platform_id=post.id, # Reddit's unique post ID
                author=author,
                thumbnail_url=thumbnail_url,
                view_count=0, # Reddit doesn't have views, use score
                like_count=post.score, # Use upvotes as likes
                comment_count=post.num_comments,
                engagement_score=engagement_score,
                published_at=datetime.fromtimestamp(post.created_utc),
                duration=0, # Not applicable for Reddit posts
                category='misc' # Could try to infer from subreddit
            )
            return trend
        except Exception as e:
            print(f"[RedditScraper] Error parsing post {post.id}: {e}")
            return None