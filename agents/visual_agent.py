"""Visual concept agent for AI Research Agent."""
import logging
from typing import Optional

from config import get_openai_client
from storage.prompt_loader import load_prompt
from utils import sanitize_for_prompt

logger = logging.getLogger(__name__)


def generate_visual_prompt(topic: str, temperature: float = 0.8) -> str:
    """
    Generate visual concepts and image prompts for a topic.

    Args:
        topic: Research topic with key insights
        temperature: Model temperature (higher = more creative)

    Returns:
        Visual concept description with AI image prompt

    Raises:
        ValueError: If the generated visual prompt is empty
    """
    client = get_openai_client()
    prompt_template = load_prompt("prompts/visual_agent.txt")

    # Sanitize input to prevent prompt injection
    sanitized_topic = sanitize_for_prompt(topic, max_length=8000)

    final_prompt = f"""
{prompt_template}

TOPIC:
{sanitized_topic}
"""

    logger.info("Generating visual concept...")

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

        visual_content = response.choices[0].message.content

        if not visual_content or not visual_content.strip():
            raise ValueError("Generated visual prompt is empty")

        logger.info(f"Successfully generated visual prompt ({len(visual_content)} chars)")
        return visual_content

    except Exception as e:
        logger.error(f"Failed to generate visual prompt: {e}")
        raise