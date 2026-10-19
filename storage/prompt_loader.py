"""Prompt loading utilities for AI Research Agent."""
import logging
from pathlib import Path

from config import get_project_path

logger = logging.getLogger(__name__)


def load_prompt(filepath: str) -> str:
    """
    Load a prompt file from the prompts directory.

    Args:
        filepath: Relative path from project root (e.g., "prompts/research_prompt.txt")

    Returns:
        Contents of the prompt file

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
        IOError: If the file cannot be read
    """
    prompt_path = get_project_path(filepath)

    if not prompt_path.exists():
        available = list(get_project_path("prompts").glob("*.txt"))
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}\n"
            f"Available prompts: {[p.name for p in available]}"
        )

    try:
        with open(prompt_path, "r", encoding="utf-8") as file:
            content = file.read()

        if not content.strip():
            logger.warning(f"Prompt file is empty: {prompt_path}")
            raise ValueError(f"Prompt file is empty: {filepath}")

        logger.info(f"Loaded prompt: {filepath} ({len(content)} chars)")
        return content

    except IOError as e:
        logger.error(f"Failed to read prompt file {filepath}: {e}")
        raise