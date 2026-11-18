"""Shared utilities for AI Research Agent.

This module provides helper functions for sanitising inputs, validating LLM responses,
and formatting collected data for prompt injection.
"""
import re
import logging
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Maximum input lengths to prevent token overflow
MAX_TEXT_LENGTH = 8000
MAX_TITLE_LENGTH = 200


def sanitize_for_prompt(text: str, max_length: int = MAX_TEXT_LENGTH) -> str:
    """Sanitise text for use in LLM prompts.

    Removes potential prompt-injection patterns and limits length.
    """
    if not text:
        return ""

    # Remove code block markers that could disrupt prompt formatting
    sanitized = text.replace("```", "`")

    # Remove obvious instruction-injection attempts
    injection_patterns = [
        r"ignore\s+(?:all\s+)?(?:previous|above)\s+(?:instructions?|commands?|rules?)",
        r"(?:system|assistant|human)\s*:\s*"
    ]
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

    # Truncate to the requested length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized.strip()


def sanitize_title(title: str, max_length: int = MAX_TITLE_LENGTH) -> str:
    """Sanitise a title string."""
    if not title:
        return "Untitled"
    cleaned = " ".join(title.split())
    if len(cleaned) > max_length:
        cleaned = cleaned[: max_length - 3] + "..."
    return cleaned


def truncate_text(text: str, max_length: int = MAX_TEXT_LENGTH) -> str:
    """Truncate text to a maximum length with ellipsis."""
    if not text or len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def validate_topic_response(response: Dict[str, Any], required_keys: List[str] = None) -> bool:
    """Validate that a topic response has all required keys with non-empty values.

    Args:
        response: The parsed JSON response
        required_keys: List of required field names (defaults to the full schema)

    Returns:
        True if valid, False otherwise
    """
    if required_keys is None:
        required_keys = ["top_topic", "summary", "key_insight", "recommended_angle", "source_title", "source_url"]

    if not isinstance(response, dict):
        logger.warning(f"Response is not a dict: {type(response)}")
        return False

    for key in required_keys:
        if key not in response:
            logger.warning(f"Missing required key: {key}")
            return False
        if not isinstance(response[key], str) or not response[key].strip():
            logger.warning(f"Key '{key}' is empty or not a string")
            return False
    return True


def format_collected_data(rss_data: List, github_data: List, hn_data: List) -> str:
    """Format scraped data into a compact markdown block for the LLM.

    The function produces a concise, bullet-style representation that saves tokens
    compared to dumping raw Python dictionaries.
    """
    def _format_items(items: List, prefix: str) -> str:
        if not items:
            return f"{prefix}: None\n"
        lines = []
        for i, item in enumerate(items, 1):
            title = item.get("title", "<no title>")
            url = item.get("link", item.get("url", ""))
            # Show title and URL only if we have a URL - keeps the prompt short
            line = f"- {title}" if not url else f"- {title} ({url})"
            lines.append(line)
        return f"{prefix}:\n" + "\n".join(lines) + "\n"

    rss_part = _format_items(rss_data, "RSS Articles")
    github_part = _format_items(github_data, "GitHub Trends")
    hn_part = _format_items(hn_data, "HackerNews Posts")
    return f"{rss_part}\n{github_part}\n{hn_part}"