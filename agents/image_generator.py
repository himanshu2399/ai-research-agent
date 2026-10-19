"""Image generator agent for AI Research Agent."""
import base64
import logging
from typing import Optional

from config import get_openai_client
from storage.save_output import save_image
from utils import sanitize_for_prompt

logger = logging.getLogger(__name__)


def generate_image(image_prompt: str, size: str = "1024x1024") -> str:
    """
    Generate an AI image from a prompt.

    Args:
        image_prompt: Text prompt for image generation
        size: Image dimensions (default: 1024x1024)

    Returns:
        Path to saved image file

    Raises:
        ValueError: If image generation fails or returns empty data
    """
    client = get_openai_client()

    # Sanitize prompt to remove potential injection
    sanitized_prompt = sanitize_for_prompt(image_prompt, max_length=3000)

    logger.info(f"Generating image ({size})...")

    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=sanitized_prompt,
            size=size
        )

        # Validate response
        if not response.data:
            raise ValueError("No image data in response")

        if len(response.data) == 0:
            raise ValueError("Empty image data array in response")

        image_base64 = response.data[0].b64_json

        if not image_base64:
            raise ValueError("No b64_json in image response")

        # Decode base64 to bytes
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as decode_error:
            logger.error(f"Failed to decode base64 image: {decode_error}")
            raise ValueError(f"Invalid base64 image data: {decode_error}")

        if len(image_bytes) == 0:
            raise ValueError("Decoded image bytes is empty")

        # Generate timestamped filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"

        # Save to disk
        image_path = save_image(image_bytes, filename)

        logger.info(f"Image saved: {image_path} ({len(image_bytes)} bytes)")
        return image_path

    except Exception as e:
        logger.error(f"Failed to generate image: {e}")
        raise


def extract_image_prompt(visual_content: str) -> str:
    """
    Extract the AI Image Prompt section from visual agent output.

    Args:
        visual_content: Full visual agent output

    Returns:
        Extracted image prompt or full content if not found
    """
    import re

    # Try to find the AI Image Prompt section
    pattern = r"### AI Image Prompt\s*\n(.+?)(?=###|$)"
    match = re.search(pattern, visual_content, re.DOTALL | re.IGNORECASE)

    if match:
        prompt = match.group(1).strip()
        logger.info("Extracted AI Image Prompt section")
        return prompt

    logger.warning("Could not find AI Image Prompt section, using full content")
    return visual_content