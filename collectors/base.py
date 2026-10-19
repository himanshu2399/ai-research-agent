"""Base collector utilities with error handling and retry logic."""
import time
import logging
from typing import List, Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def with_retry(max_attempts: int = 3, delay: float = 1.0, timeout: int = 10):
    """
    Decorator to add retry logic to collector functions.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        timeout: Request timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt < max_attempts:
                        logger.info(f"Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= 2  # Exponential backoff

            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_error

        return wrapper
    return decorator


def fetch_with_timeout(url: str, timeout: int = 10, max_retries: int = 3) -> Optional[str]:
    """
    Fetch URL with timeout and retry logic.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries

    Returns:
        Response text or None if all retries fail
    """
    import requests

    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            last_error = e
            logger.warning(f"Request attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1))  # Incremental backoff

    logger.error(f"All attempts to fetch {url} failed: {last_error}")
    return None


def safe_get(data: Dict, *keys, default=None):
    """
    Safely get nested dictionary values with a default fallback.

    Args:
        data: Dictionary to traverse
        *keys: Sequence of keys to traverse
        default: Default value if key not found

    Returns:
        Value at key path or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
        if current is None:
            return default
    return current


def validate_data_list(items: List[Dict], required_fields: List[str]) -> List[Dict]:
    """
    Validate a list of data items have required fields.

    Args:
        items: List of data dictionaries
        required_fields: List of required field names

    Returns:
        List of valid items
    """
    valid_items = []
    for item in items:
        if all(field in item and item[field] for field in required_fields):
            valid_items.append(item)
        else:
            logger.warning(f"Invalid item missing required fields: {item}")

    return valid_items