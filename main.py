from collectors.rss_collector import collect_rss_articles
from collectors.github_collector import collect_github_trends
from collectors.hn_collector import collect_hn_posts
from agents.image_generator import generate_image
from agents.topic_researcher import generate_research_topic
from agents.linkedin_writer import generate_linkedin_post

from storage.save_output import save_to_file
from agents.visual_agent import generate_visual_prompt
from agents.orchestrator_agent import orchestrate_final_output

def main():

    print("Collecting RSS articles...")
    rss_data = collect_rss_articles()

    print("Collecting GitHub trends...")
    github_data = collect_github_trends()

    print("Collecting HackerNews posts...")
    hn_data = collect_hn_posts()

    combined_data = f"""
RSS ARTICLES:
{rss_data}

GITHUB TRENDS:
{github_data}

HACKERNEWS:
{hn_data}
"""

    print("Generating research topic...")
    topic = generate_research_topic(combined_data)

    print("\nTOPIC JSON:\n")
    print(topic)

    print("\nFULL TOPIC RESPONSE:\n")
    print(topic)

    required_keys = ["top_topic", "summary", "key_insight", "recommended_angle"]
    missing_keys = [key for key in required_keys if key not in topic]
    if missing_keys:
        raise KeyError(
            f"Research topic response is missing required keys: {missing_keys}.\nResponse: {topic}"
        )

    top_topic = topic["top_topic"]
    summary = topic["summary"]
    key_insight = topic["key_insight"]
    recommended_angle = topic["recommended_angle"]

    print("\nGenerating LinkedIn post...\n")

    linkedin_post = generate_linkedin_post(
        f"""
    TOPIC:
    {top_topic}

    SUMMARY:
    {summary}

    KEY INSIGHT:
    {key_insight}

    RECOMMENDED ANGLE:
    {recommended_angle}
    """
    )

    print("\nGenerating visual concepts...\n")

    visual_prompt = generate_visual_prompt(
        f"""
    TOPIC:
    {top_topic}

    KEY INSIGHT:
    {key_insight}
    """
    )

    print(visual_prompt)

    print("\nGenerating AI image...\n")

    image_path = generate_image(visual_prompt)

    print(f"Image saved at: {image_path}")

    print(linkedin_post)

    print("\nOrchestrating final deliverable...\n")

    final_output = orchestrate_final_output(
        topic,
        linkedin_post,
        visual_prompt
    )

    print("\n" + "="*80)
    print("FINAL DELIVERABLE")
    print("="*80)
    print(final_output)
            
    filename = save_to_file(final_output)

    print(f"\nSaved to: {filename}")

if __name__ == "__main__":
    main()