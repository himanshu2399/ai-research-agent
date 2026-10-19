"""Orchestrator agent for AI Research Agent."""
import logging
from typing import Dict, Any

from config import get_openai_client
from storage.prompt_loader import load_prompt
from utils import sanitize_for_prompt

logger = logging.getLogger(__name__)


def orchestrate_final_output(
    topic: Dict[str, Any],
    linkedin_post: str,
    visual_prompt: str,
    temperature: float = 0.6
) -> str:
    """
    Assemble final deliverable from research, post, and visual concepts.

    Args:
        topic: Research topic dictionary
        linkedin_post: Generated LinkedIn post
        visual_prompt: Visual concept description
        temperature: Model temperature (lower for more consistent assembly)

    Returns:
        Final Markdown deliverable

    Raises:
        ValueError: If the generated output is empty
    """
    client = get_openai_client()
    prompt_template = load_prompt("prompts/orchestrator.txt")

    # Sanitize inputs
    topic_str = str(topic) if isinstance(topic, dict) else topic
    sanitized_topic = sanitize_for_prompt(topic_str, max_length=5000)
    sanitized_post = sanitize_for_prompt(linkedin_post, max_length=8000)
    sanitized_visual = sanitize_for_prompt(visual_prompt, max_length=5000)

    final_prompt = f"""
{prompt_template}

RESEARCH TOPIC:
{sanitized_topic}

LINKEDIN POST:
{sanitized_post}

VISUAL CONCEPTS:
{sanitized_visual}
"""

    logger.info("Orchestrating final deliverable...")

    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            temperature=temperature  # Lower for consistent assembly
        )

        output_content = response.choices[0].message.content

        if not output_content or not output_content.strip():
            raise ValueError("Generated final output is empty")

        logger.info(f"Successfully orchestrated final deliverable ({len(output_content)} chars)")
        return output_content

    except Exception as e:
        logger.error(f"Failed to orchestrate final output: {e}")
        raise