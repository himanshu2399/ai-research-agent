"""LinkedIn post writer agent for AI Research Agent."""
import logging
from typing import Optional

from config import get_openai_client
from storage.prompt_loader import load_prompt
from utils import sanitize_for_prompt

logger = logging.getLogger(__name__)


def generate_linkedin_post(topic: str, temperature: float = 0.8) -> str:
    """
    Generate a LinkedIn post from topic research.

    Args:
        topic: Research topic with summary, key insight, and recommended angle
        temperature: Model temperature (higher = more creative)

    Returns:
        Generated LinkedIn post content

    Raises:
        ValueError: If the generated post is empty
    """
    client = get_openai_client()
    prompt_template = load_prompt("prompts/content_strategist.txt")

    # Sanitize input to prevent prompt injection
    sanitized_topic = sanitize_for_prompt(topic, max_length=10000)

    final_prompt = f"""
{prompt_template}

TOPIC:
{sanitized_topic}
"""

    logger.info("Generating LinkedIn post...")

    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
                    )

        post_content = response.choices[0].message.content

        if not post_content or not post_content.strip():
            raise ValueError("Generated LinkedIn post is empty")

        logger.info(f"Successfully generated LinkedIn post ({len(post_content)} chars)")
        return post_content

    except Exception as e:
        logger.error(f"Failed to generate LinkedIn post: {e}")
        raise