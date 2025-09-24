# backend/scrapers/youtube_scraper.py
import os
import requests
import time
from datetime import datetime, timedelta
from backend import db
from backend.models.trend_model import Trend
from backend.config import Config

class YouTubeScraper:
    def __init__(self):
        self.api_key = Config.PLATFORM_APIS['youtube']['api_key']
        if not self.api_key:
            print("[YouTubeScraper] Warning: YouTube API key is not configured.")
        self.base_url = "https://www.googleapis.com/youtube/v3"

        # --- Global, diverse search queries for short-form content ---
        # Focused on your specific requests, language-agnostic terms.
        self.search_queries = [
            # Emotional / Sad
            "emotional scene", "sad scene", "heartbreaking moment", "touching story",
            "emotional anime scene", "emotional cartoon scene", "emotional movie scene",
            "sad anime moment", "sad cartoon moment", "sad movie moment",
            "emotional music video", "sad music video",

            # Anime / Cartoon / Movies
            "anime scene", "anime clip", "iconic anime moment", "anime short",
            "cartoon scene", "cartoon clip", "funny cartoon compilation", "cartoon short",
            "movie clip", "best movie scene", "movie reaction compilation", "movie short",

            # Funny / Viral
            "funny", "comedy skit", "stand up comedy", "funny moments", "hilarious",
            "meme compilation", "funny status", "tiktok funny", "prank compilation",

            # Music / Dance / Tech
            "music video", "new song", "viral music", "top hits", "lyrics",
            "dance", "viral dance", "tiktok dance", "dance challenge",
            "technology", "tech review", "viral technology", "gadget unboxing", "ai",

            # General Short-Form
            "short film", "mini documentary", "life hack", "motivational video",
            "fail compilation", "win compilation", "reaction video"
        ]

    def is_configured(self):
        """Check if the scraper has the necessary API keys."""
        return bool(self.api_key)

    def _search_videos(self, query, max_results=8, duration="short", order="relevance"):
        """Search for videos globally on YouTube."""
        if not self.api_key:
            print("[YouTubeScraper] API key missing, cannot search.")
            return []

        url = f"{self.base_url}/search"
        # KEY CHANGE: NO regionCode parameter. This ensures GLOBAL search results.
        # Add publishedAfter to focus on recent content (last 7 days)
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')

        params = {
            'part': 'snippet',
            'type': 'video',
            'q': query,
            # 'regionCode': 'BD',  # <-- EXPLICITLY REMOVED to get global results
            'maxResults': min(max_results, 50),
            'key': self.api_key,
            'order': order, # 'relevance' or 'viewCount'
            'videoDuration': duration, # 'short', 'medium'
            'publishedAfter': seven_days_ago # Focus on recent trends
        }
        try:
            print(f"[YouTubeScraper] Searching GLOBALLY for: '{query}' (Duration: {duration}, Order: {order})")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            print(f"[YouTubeScraper] Found {len(items)} items for '{query}'")
            return items
        except requests.exceptions.RequestException as e:
            print(f"[YouTubeScraper ERROR] Search failed for '{query}': {e}")
            # Retry with 'relevance' if 'viewCount' failed?
            if order != 'relevance':
                print(f"[YouTubeScraper] Retrying '{query}' with 'relevance' order...")
                return self._search_videos(query, max_results, duration, 'relevance')
            return []
        except Exception as e:
            print(f"[YouTubeScraper ERROR] Unexpected error for '{query}': {e}")
            return []

    def _get_video_ids(self, search_results):
        """Extract unique video IDs."""
        ids = set(item.get('id', {}).get('videoId') for item in search_results if item.get('id', {}).get('videoId'))
        print(f"[YouTubeScraper] Extracted {len(ids)} unique video IDs from search results.")
        return list(ids)

    def _get_video_details_batch(self, video_ids):
        """Get detailed stats for video IDs."""
        if not video_ids or not self.api_key:
            return {}
        url = f"{self.base_url}/videos"
        batches = [video_ids[i:i + 50] for i in range(0, len(video_ids), 50)]
        all_details = {}
        for batch in batches:
            params = {
                'part': 'statistics,contentDetails,snippet',
                'id': ','.join(batch),
                'key': self.api_key
            }
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                batch_details = {item['id']: item for item in data.get('items', [])}
                all_details.update(batch_details)
            except Exception as e:
                print(f"[YouTubeScraper ERROR] Failed to get details for a batch: {e}")
        print(f"[YouTubeScraper] Retrieved details for {len(all_details)} videos.")
        return all_details

    def _parse_duration(self, duration_str):
        """Parse ISO 8601 duration to seconds."""
        import re
        pattern = re.compile(r'P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?')
        match = pattern.match(duration_str)
        if not match:
            return 0
        days = int(match.group(1)) if match.group(1) else 0
        hours = int(match.group(2)) if match.group(2) else 0
        minutes = int(match.group(3)) if match.group(3) else 0
        seconds = float(match.group(4)) if match.group(4) else 0.0
        return int(days * 86400 + hours * 3600 + minutes * 60 + seconds)

    def get_trending_videos(self, limit=60): # Increased limit for YouTube
        """Get diverse, short, global videos based on specific categories."""
        if not self.api_key:
            print("[YouTubeScraper] Cannot scrape, API key not configured.")
            return []
        print(f"[YouTubeScraper] === STARTING GLOBAL scrape (Target: {limit} videos) ===")

        # 1. Collect candidate videos from various searches
        all_candidates = []
        seen_ids = set()

        for query in self.search_queries:
            print(f"[YouTubeScraper] --- Searching for specific query: '{query}' ---")

            # Alternate strategies slightly to get variety
            # Prioritize 'viewCount' for popularity, fallback to 'relevance'
            # Alternate duration to get a mix of very short and slightly longer relevant clips
            order_strategy = 'viewCount' if len(all_candidates) % 4 == 0 else 'relevance'
            duration_strategy = 'short' if len(all_candidates) % 3 != 0 else 'medium'

            items = self._search_videos(
                query,
                max_results=8, # Increased per query to get more candidates
                duration=duration_strategy,
                order=order_strategy
            )

            added_this_query = 0
            for item in items:
                video_id = item.get('id', {}).get('videoId')
                # Avoid Rickroll and duplicates
                if video_id and video_id not in seen_ids and video_id != "dQw4w9WgXcQ":
                    seen_ids.add(video_id)
                    all_candidates.append(item)
                    added_this_query += 1

            print(f"[YouTubeScraper] Added {added_this_query} candidates for '{query}'. Total candidates: {len(all_candidates)}")

            time.sleep(0.05) # Be kind to the API

            # Stop early if we have plenty of candidates
            if len(all_candidates) >= limit * 3: # Aim for 3x candidates
                print(f"[YouTubeScraper] Found enough candidates ({len(all_candidates)}). Stopping search loop.")
                break

        print(f"[YouTubeScraper] Finished search loop. Total unique candidates collected: {len(all_candidates)}")

        # 2. Get detailed information for candidates
        candidate_ids = self._get_video_ids(all_candidates)
        video_details = self._get_video_details_batch(candidate_ids)

        # 3. Process, filter by final duration, recalculate score, and create Trend objects
        trends = []
        processed_ids = set() # Double-check against duplicates in final list

        for item in all_candidates:
            video_id = item.get('id', {}).get('videoId')
            if not video_id or video_id in processed_ids:
                continue

            detail = video_details.get(video_id)
            if not detail:
                print(f"[YouTubeScraper] Warning: No details for {video_id}, skipping.")
                continue

            # Final, strict duration filter: max 12 minutes (720 seconds)
            duration_str = detail.get('contentDetails', {}).get('duration', 'PT0S')
            duration_sec = self._parse_duration(duration_str)
            if duration_sec > 720 or duration_sec == 0: # Exclude 0s or very long videos
                print(f"[YouTubeScraper] Filtering out video {video_id} (Duration: {duration_sec}s)")
                continue

            trend_obj = self._parse_video_data(item, detail)
            if trend_obj:
                # Assign a more specific category based on the original query
                # Find the best matching query term
                best_match = "misc"
                snippet = item.get('snippet', {})
                title_lower = (snippet.get('title', '')).lower()
                description_lower = (snippet.get('description', '')).lower()

                for q in self.search_queries:
                     # Check if the query term (or its main part) is in title/description
                     # e.g., match "emotional scene" if title has "emotional" and "scene"
                     query_parts = q.split()
                     if len(query_parts) > 1:
                         # For multi-word queries, check main parts
                         if query_parts[0] in title_lower and query_parts[1] in title_lower:
                             best_match = q
                             break
                     else:
                         # For single word, direct check
                         if q in title_lower or q in description_lower:
                             best_match = q
                             break

                trend_obj.category = best_match
                trends.append(trend_obj)
                processed_ids.add(video_id)
                print(f"[YouTubeScraper] Finalized: {trend_obj.title[:40]}... ({trend_obj.category}, {duration_sec}s)")

            if len(trends) >= limit:
                print(f"[YouTubeScraper] Reached target limit of {limit}. Stopping processing.")
                break

        print(f"[YouTubeScraper] === COMPLETED. Final unique trends list size: {len(trends)} ===")
        return trends

    def _parse_video_data(self, search_item, video_detail):
        """Parse API data into a Trend object."""
        try:
            snippet = search_item.get('snippet', {})
            video_id = search_item.get('id', {}).get('videoId')
            if not video_id:
                print("[YouTubeScraper] Skipping item, no videoId.")
                return None

            title = snippet.get('title', 'N/A')
            description = snippet.get('description', '')
            published_at = snippet.get('publishedAt', '')
            channel_title = snippet.get('channelTitle', 'N/A')

            try:
                published_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                print(f"[YouTubeScraper] Bad date '{published_at}' for {video_id}, using now.")
                published_date = datetime.utcnow()

            thumbnails = snippet.get('thumbnails', {})
            # Get best available thumbnail
            thumbnail_url = (
                thumbnails.get('maxres', {}).get('url') or
                thumbnails.get('standard', {}).get('url') or
                thumbnails.get('high', {}).get('url') or
                thumbnails.get('medium', {}).get('url') or
                thumbnails.get('default', {}).get('url') or ''
            )

            url = f"https://www.youtube.com/watch?v={video_id}"

            stats = video_detail.get('statistics', {})
            view_count = int(stats.get('viewCount', 0))
            like_count = int(stats.get('likeCount', 0)) # Might be 0 if disabled
            comment_count = int(stats.get('commentCount', 0))

            duration_str = video_detail.get('contentDetails', {}).get('duration', 'PT0S')
            duration_seconds = self._parse_duration(duration_str)

            # Potentially better engagement score, considering view count magnitude
            # and boosting shorter, highly engaged videos
            base_score = view_count + (like_count * 2) + (comment_count * 3)
            # Boost score for very short videos (< 90s) if they have decent engagement
            if duration_seconds > 0 and duration_seconds < 90:
                 boost_factor = min(2.0, 90.0 / duration_seconds) # Up to 2x boost
                 engagement_score = int(base_score * boost_factor)
            else:
                 engagement_score = base_score

            # --- Create Trend Object ---
            trend = Trend(
                title=title[:255],
                description=description[:500], # Include description field
                url=url,
                platform='youtube',
                platform_id=video_id,
                author=channel_title[:150],
                thumbnail_url=thumbnail_url,
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                engagement_score=engagement_score,
                published_at=published_date,
                duration=duration_seconds,
                category='' # Will be set by caller
            )
            return trend

        except Exception as e:
            video_id = search_item.get('id', {}).get('videoId', 'Unknown_ID')
            print(f"[YouTubeScraper ERROR] Parsing failed for {video_id}: {e}")
            import traceback
            traceback.print_exc()
            return None