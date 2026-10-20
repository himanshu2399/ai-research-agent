"""Topic memory manager to prevent duplicate content generation."""
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

MEMORY_FILE = "outputs/topic_memory.md"


def initialize_memory_file() -> None:
    """Create the topic memory file if it doesn't exist."""
    if not os.path.exists(MEMORY_FILE):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            f.write("# AI Research Agent - Topic Memory\n\n")
            f.write("This file tracks all topics generated to prevent duplicates.\n\n")
            f.write("---\n\n")
        logger.info(f"Created new topic memory file: {MEMORY_FILE}")


def add_topic_to_memory(topic: str, summary: str, post_file: str) -> None:
    """
    Add a generated topic to memory.

    Args:
        topic: The main topic string
        summary: Brief summary or key insight
        post_file: Path to the generated post file
    """
    initialize_memory_file()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"## {timestamp}\n\n")
        f.write(f"**Topic:** {topic}\n\n")
        f.write(f"**Summary:** {summary}\n\n")
        f.write(f"**File:** `{post_file}`\n\n")
        f.write("---\n\n")

    logger.info(f"Added topic to memory: {topic[:60]}...")


def get_previous_topics() -> List[Dict[str, str]]:
    """
    Read all previously generated topics from memory.

    Returns:
        List of dictionaries with 'topic' and 'summary' keys
    """
    if not os.path.exists(MEMORY_FILE):
        initialize_memory_file()
        return []

    topics = []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the markdown file
        entries = content.split("---\n\n")[1:]  # Skip header

        for entry in entries:
            if not entry.strip():
                continue

            lines = entry.strip().split("\n")
            topic = None
            summary = None

            for line in lines:
                if line.startswith("**Topic:**"):
                    topic = line.replace("**Topic:**", "").strip()
                elif line.startswith("**Summary:**"):
                    summary = line.replace("**Summary:**", "").strip()

            if topic:
                topics.append({
                    "topic": topic,
                    "summary": summary or ""
                })

        logger.info(f"Loaded {len(topics)} topics from memory")
        return topics

    except Exception as e:
        logger.error(f"Error reading topic memory: {e}")
        return []


def format_memory_for_prompt() -> str:
    """
    Format previous topics as a string to inject into the research prompt.

    Returns:
        Formatted string of previous topics for LLM consumption
    """
    topics = get_previous_topics()

    if not topics:
        return "No previous topics found."

    # Get recent topics (last 30 to keep prompt manageable)
    recent_topics = topics[-30:]

    formatted = "## PREVIOUSLY COVERED TOPICS (DO NOT REPEAT):\n\n"

    for i, topic_data in enumerate(recent_topics, 1):
        formatted += f"{i}. {topic_data['topic']}\n"
        if topic_data['summary']:
            formatted += f"   Summary: {topic_data['summary']}\n"

    formatted += "\nIMPORTANT: Select a NEW topic that is meaningfully different from all topics above.\n"

    return formatted


def is_topic_duplicate(new_topic: str, similarity_threshold: float = 0.7) -> bool:
    """
    Check if a topic is too similar to previously covered topics.

    Args:
        new_topic: The topic to check
        similarity_threshold: Threshold for considering topics similar (not used yet, placeholder)

    Returns:
        True if likely duplicate, False otherwise
    """
    previous = get_previous_topics()

    if not previous:
        return False

    # Simple keyword-based duplicate detection
    # Convert to lowercase for comparison
    new_lower = new_topic.lower()

    for prev in previous:
        prev_lower = prev['topic'].lower()

        # Exact match
        if new_lower == prev_lower:
            logger.warning(f"Exact duplicate detected: {new_topic}")
            return True

        # Check if one is substring of other (very similar)
        if new_lower in prev_lower or prev_lower in new_lower:
            if len(new_lower) > 20 and len(prev_lower) > 20:  # Only for substantial topics
                logger.warning(f"Near duplicate detected: {new_topic} ~ {prev['topic']}")
                return True

    return False


def get_topic_count() -> int:
    """
    Get the total number of topics in memory.

    Returns:
        Count of topics
    """
    return len(get_previous_topics())


def clear_memory() -> None:
    """Clear all topic memory (use with caution)."""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
        logger.info("Topic memory cleared")
    initialize_memory_file()
