"""Hacker News collector for AI Research Agent."""
import logging
from typing import List, Dict

from collectors.base import with_retry, fetch_with_timeout
import json

logger = logging.getLogger(__name__)

HN_API_URL = "https://hn.algolia.com/api/v1/search?tags=front_page"


@with_retry(max_attempts=2, delay=1.0, timeout=15)
def fetch_hn_api() -> Dict:
    """Fetch Hacker News Algolia API with retry."""
    html = fetch_with_timeout(HN_API_URL, timeout=15, max_retries=2)
    if not html:
        return {"hits": []}
    return json.loads(html)


def collect_hn_posts() -> List[Dict]:
    """
    Collect front-page stories from Hacker News via Algolia API.

    Returns:
        List of story dictionaries with title and URL
    """
    try:
        data = fetch_hn_api()

        posts = []
        hits = data.get("hits", [])

        if not hits:
            logger.warning("No posts returned from Hacker News API")
            return []

        for item in hits[:10]:  # Limit to top 10
            post = {
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "points": item.get("points", 0),
                "author": item.get("author", ""),
                "created_at": item.get("created_at", ""),
                "object_id": item.get("objectID", "")
            }
            posts.append(post)

        logger.info(f"Collected {len(posts)} posts from Hacker News")
        return posts

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Hacker News API response: {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to collect Hacker News posts: {e}")
        return []