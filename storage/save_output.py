"""Output saving utilities for AI Research Agent."""
import logging
from pathlib import Path
from datetime import datetime

from config import get_project_path

logger = logging.getLogger(__name__)


def save_to_file(content: str, filename: str = None) -> str:
    """
    Save content to a timestamped Markdown file.

    Args:
        content: The content to save
        filename: Optional custom filename (without path). If None, generates timestamped name.

    Returns:
        Full path to saved file

    Raises:
        IOError: If the file cannot be written
    """
    if not content or not content.strip():
        raise ValueError("Cannot save empty content")

    # Create outputs directory
    output_dir = get_project_path("outputs")
    output_dir.mkdir(exist_ok=True)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"post_{timestamp}.md"

    filepath = output_dir / filename

    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

        logger.info(f"Saved output to: {filepath} ({len(content)} chars)")
        return str(filepath)

    except IOError as e:
        logger.error(f"Failed to save output to {filepath}: {e}")
        raise


def save_image(image_bytes: bytes, filename: str = "generated_image.png") -> str:
    """
    Save binary image data to file.

    Args:
        image_bytes: Raw image bytes
        filename: Image filename (with extension)

    Returns:
        Full path to saved image

    Raises:
        IOError: If the file cannot be written
        ValueError: If image_bytes is empty
    """
    if not image_bytes:
        raise ValueError("Cannot save empty image data")

    # Create outputs/images directory
    output_dir = get_project_path("outputs", "images")
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename

    try:
        with open(filepath, "wb") as f:
            f.write(image_bytes)

        logger.info(f"Saved image to: {filepath} ({len(image_bytes)} bytes)")
        return str(filepath)

    except IOError as e:
        logger.error(f"Failed to save image to {filepath}: {e}")
        raise


def get_latest_output() -> str:
    """
    Get the most recently created output file.

    Returns:
        Path to the latest output file or None
    """
    output_dir = get_project_path("outputs")

    if not output_dir.exists():
        return None

    md_files = sorted(output_dir.glob("post_*.md"), reverse=True)
    return str(md_files[0]) if md_files else None