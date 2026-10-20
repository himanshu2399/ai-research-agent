"""Main entry point for AI Research Agent."""
import logging
import sys
from typing import Dict, Any

from collectors.rss_collector import collect_rss_articles
from collectors.github_collector import collect_github_trends
from collectors.hn_collector import collect_hn_posts
from agents.image_generator import generate_image, extract_image_prompt
from agents.topic_researcher import generate_research_topic
from agents.linkedin_writer import generate_linkedin_post
from agents.visual_agent import generate_visual_prompt
from agents.orchestrator_agent import orchestrate_final_output
from storage.save_output import save_to_file
from storage.topic_memory import get_topic_count, is_topic_duplicate, add_topic_to_memory
from utils import validate_topic_response, format_collected_data

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline() -> str:
    """
    Execute the full AI Research Agent pipeline.

    Returns:
        Path to the saved output file

    Raises:
        Exception: If any critical step fails
    """
    logger.info("=" * 60)
    logger.info("Starting AI Research Agent Pipeline")
    logger.info("=" * 60)

    # Step 1: Collect data from all sources
    logger.info("Step 1: Collecting data from sources...")

    try:
        logger.info("  Collecting RSS articles...")
        rss_data = collect_rss_articles()
        logger.info(f"  ✓ Collected {len(rss_data)} RSS articles")
    except Exception as e:
        logger.error(f"  ✗ RSS collection failed: {e}")
        rss_data = []

    try:
        logger.info("  Collecting GitHub trends...")
        github_data = collect_github_trends()
        logger.info(f"  ✓ Collected {len(github_data)} GitHub repos")
    except Exception as e:
        logger.error(f"  ✗ GitHub collection failed: {e}")
        github_data = []

    try:
        logger.info("  Collecting Hacker News posts...")
        hn_data = collect_hn_posts()
        logger.info(f"  ✓ Collected {len(hn_data)} HN posts")
    except Exception as e:
        logger.error(f"  ✗ Hacker News collection failed: {e}")
        hn_data = []

    # Validate we have at least some data
    total_items = len(rss_data) + len(github_data) + len(hn_data)
    if total_items == 0:
        raise Exception("No data collected from any source. Cannot proceed.")

    logger.info(f"Total items collected: {total_items}")

    # Step 2: Combine data
    combined_data = format_collected_data(rss_data, github_data, hn_data)

    # Step 3: Generate research topic
    logger.info("Step 2: Generating research topic...")
    topic = generate_research_topic(combined_data)

    logger.info("Topic selected:")
    logger.info(f"  Topic: {topic.get('top_topic', 'N/A')}")
    logger.info(f"  Key Insight: {topic.get('key_insight', 'N/A')[:100]}...")

    # Check for duplicate topics before proceeding
    logger.info("Checking for topic duplicates...")
    if is_topic_duplicate(topic.get('top_topic', '')):
        logger.warning("Duplicate topic detected, skipping to next iteration...")
        logger.warning("To force a new topic, clear the memory file at: outputs/topic_memory.md")
        raise Exception("Duplicate topic detected - stopping pipeline to avoid duplicate LinkedIn posts")

    # Step 4: Generate LinkedIn post
    logger.info("Step 3: Generating LinkedIn post...")

    topic_input = f"""
TOPIC:
{topic.get('top_topic', '')}

SUMMARY:
{topic.get('summary', '')}

KEY INSIGHT:
{topic.get('key_insight', '')}

RECOMMENDED ANGLE:
{topic.get('recommended_angle', '')}
"""

    linkedin_post = generate_linkedin_post(topic_input)
    logger.info(f"✓ LinkedIn post generated ({len(linkedin_post)} chars)")

    # Step 5: Generate visual concepts
    logger.info("Step 4: Generating visual concepts...")

    visual_input = f"""
TOPIC:
{topic.get('top_topic', '')}

KEY INSIGHT:
{topic.get('key_insight', '')}
"""

    visual_prompt = generate_visual_prompt(visual_input)
    logger.info(f"✓ Visual concepts generated ({len(visual_prompt)} chars)")

    # Step 6: Generate AI image
    logger.info("Step 5: Generating AI image...")

    image_prompt_text = extract_image_prompt(visual_prompt)

    try:
        image_path = generate_image(image_prompt_text)
        logger.info(f"✓ Image saved at: {image_path}")
    except Exception as e:
        logger.error(f"✗ Image generation failed: {e}")
        image_path = None

    # Step 7: Orchestrate final deliverable
    logger.info("Step 6: Orchestrating final deliverable...")

    final_output = orchestrate_final_output(
        topic=topic,
        linkedin_post=linkedin_post,
        visual_prompt=visual_prompt
    )

    # Step 8: Save output
    logger.info("Step 7: Saving output...")

    filename = save_to_file(final_output)
    logger.info(f"✓ Output saved to: {filename}")

    # Step 9: Save topic to memory
    logger.info("Step 8: Saving topic to memory...")
    add_topic_to_memory(
        topic=topic.get('top_topic', ''),
        summary=topic.get('key_insight', ''),
        post_file=filename
    )
    logger.info(f"✓ Topic saved to memory (total topics: {get_topic_count()})")

    # Summary
    logger.info("=" * 60)
    logger.info("Pipeline Complete")
    logger.info("=" * 60)
    logger.info(f"Output file: {filename}")
    if image_path:
        logger.info(f"Image file: {image_path}")

    return filename


def main():
    """Main entry point with error handling."""
    try:
        output_file = run_pipeline()
        print(f"\n✓ Success! Output saved to: {output_file}")
        return 0
    except KeyboardInterrupt:
        logger.info("\nPipeline interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\n✗ Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())