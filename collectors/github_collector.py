"""GitHub Trending collector for AI Research Agent."""
import logging
from typing import List, Dict, Optional

from bs4 import BeautifulSoup
from collectors.base import with_retry, fetch_with_timeout

logger = logging.getLogger(__name__)


@with_retry(max_attempts=2, delay=1.0, timeout=15)
def fetch_trending_page() -> Optional[str]:
    """Fetch GitHub trending page with retry."""
    url = "https://github.com/trending"
    return fetch_with_timeout(url, timeout=15, max_retries=2)


def parse_repos(html_content: str) -> List[Dict]:
    """
    Parse GitHub trending HTML for repository data.

    Args:
        html_content: Raw HTML from GitHub trending page

    Returns:
        List of repository dictionaries
    """
    if not html_content:
        logger.warning("Empty HTML content passed to parser")
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    repos = soup.find_all("article")

    if not repos:
        logger.warning("No repository articles found in HTML")
        return []

    results = []
    for repo in repos[:10]:  # Limit to top 10
        repo_data = {}

        # Parse repository title (owner/repo)
        title_elem = repo.h2
        if title_elem:
            title = title_elem.text.strip().replace("\n", "").replace(" ", "")
            repo_data["repo"] = title

        # Parse repository description
        desc_elem = repo.find("p")
        if desc_elem:
            repo_data["description"] = desc_elem.text.strip()

        # Parse language
        lang_elem = repo.find("span", {"itemprop": "programmingLanguage"})
        if lang_elem:
            repo_data["language"] = lang_elem.text.strip()

        # Parse stars/trending
        stars_elem = repo.find("a", {"href": lambda x: x and "stargazers" in x})
        if stars_elem:
            stars_text = stars_elem.text.strip()
            repo_data["stars"] = stars_text

        # Only add if we have at least repo name
        if "repo" in repo_data:
            results.append(repo_data)

    logger.info(f"Parsed {len(results)} repositories from GitHub trending")
    return results


def collect_github_trends() -> List[Dict]:
    """
    Collect trending repositories from GitHub.

    Returns:
        List of repository data dictionaries
    """
    try:
        html = fetch_trending_page()
        repos = parse_repos(html)

        if not repos:
            logger.warning("No repositories collected from GitHub trending")
            return []

        return repos
    except Exception as e:
        logger.error(f"Failed to collect GitHub trends: {e}")
        return []


def get_repo_links(repos: List[Dict]) -> List[str]:
    """Extract GitHub URLs from repository data."""
    return [
        f"https://github.com/{repo.get('repo', '')}"
        for repo in repos
    ]