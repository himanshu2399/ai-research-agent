"""Topic researcher agent for AI Research Agent."""
import json
import logging
import time
from typing import Dict, Any

from config import get_openai_client
from storage.prompt_loader import load_prompt
from storage.topic_memory import format_memory_for_prompt
from utils import validate_topic_response, sanitize_for_prompt

logger = logging.getLogger(__name__)


def generate_research_topic(data: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Select a research topic from collected data using GPT-5.

    Args:
        data: Combined string of collected RSS, GitHub, and HN data
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary with keys: top_topic, summary, key_insight, recommended_angle

    Raises:
        Exception: If all retry attempts fail
    """
    client = get_openai_client()
    prompt_template = load_prompt("prompts/research_prompt.txt")

    # Get previous topics to avoid duplicates
    memory_context = format_memory_for_prompt()

    # Sanitize input data to prevent prompt injection
    sanitized_data = sanitize_for_prompt(data, max_length=15000)

    prompt = f"""
{prompt_template}

{memory_context}

DATA:
{sanitized_data}
"""

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Generating research topic (attempt {attempt}/{max_retries})")

            response = client.chat.completions.create(
                model="gpt-5",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )

            content = response.choices[0].message.content

            # Parse JSON response
            try:
                topic = json.loads(content)
            except json.JSONDecodeError as parse_error:
                logger.error(f"JSON decode error: {parse_error}")
                raise ValueError(
                    f"Failed to parse model response as JSON.\nResponse content:\n{content}"
                ) from parse_error

            # Validate structure
            if not isinstance(topic, dict):
                raise ValueError(
                    f"Model returned JSON, but not an object. Response content:\n{content}"
                )

            # Validate required fields
            if not validate_topic_response(topic):
                raise ValueError(
                    f"Response missing required fields or has empty values.\n"
                    f"Response: {topic}"
                )

            logger.info("Successfully generated research topic")
            return topic

        except Exception as e:
            logger.warning(f"Attempt {attempt}/{max_retries} failed: {e}")

            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8 seconds
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

    error_msg = f"Research Agent failed after {max_retries} retries."
    logger.error(error_msg)
    raise Exception(error_msg)