"""RSS feed collector for AI Research Agent."""
import logging
from typing import List, Dict

import feedparser

from collectors.base import with_retry, safe_get

logger = logging.getLogger(__name__)

# Configurable RSS feeds with collection limits
FEEDS_CONFIG = [
    {
        "url": "https://aws.amazon.com/blogs/devops/feed/",
        "limit": 5,
        "name": "AWS DevOps Blog"
    },
    {
        "url": "https://cloud.google.com/blog/topics/developers-practitioners/rss/",
        "limit": 5,
        "name": "Google Cloud Developers & Practitioners Blog"
    },
    {
        "url": "https://kubernetes.io/feed.xml",
        "limit": 5,
        "name": "Kubernetes Blog"
    },
    {
        "url": "https://www.cncf.io/feed/",
        "limit": 5,
        "name": "Cloud Native Computing Foundation (CNCF)"
    }
]


@with_retry(max_attempts=2, delay=1.0, timeout=15)
def fetch_feed(url: str, limit: int) -> List[Dict]:
    """
    Fetch and parse an RSS feed.

    Args:
        url: RSS feed URL
        limit: Maximum number of entries to return

    Returns:
        List of article dictionaries
    """
    logger.info(f"Fetching RSS feed: {url}")
    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries[:limit]:
        article = {
            "title": entry.get("title", "Untitled"),
            "summary": entry.get("summary", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "source": url
        }
        articles.append(article)

    logger.info(f"Collected {len(articles)} articles from {url}")
    return articles


def collect_rss_articles() -> List[Dict]:
    """
    Collect articles from all configured RSS feeds.

    Returns:
        Combined list of all articles from all feeds
    """
    all_articles = []

    for feed_config in FEEDS_CONFIG:
        try:
            articles = fetch_feed(
                url=feed_config["url"],
                limit=feed_config["limit"]
            )
            all_articles.extend(articles)
        except Exception as e:
            logger.error(f"Failed to collect from {feed_config['name']}: {e}")
            # Continue collecting from other feeds even if one fails

    logger.info(f"Total RSS articles collected: {len(all_articles)}")
    return all_articles


def get_feed_names() -> List[str]:
    """Get list of configured feed names."""
    return [feed["name"] for feed in FEEDS_CONFIG]