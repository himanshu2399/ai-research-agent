import os
from openai import OpenAI
from dotenv import load_dotenv

from storage.prompt_loader import load_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt_template = load_prompt(
    "prompts/orchestrator.txt"
)

def orchestrate_final_output(
    topic,
    linkedin_post,
    visual_prompt
):

    final_prompt = f"""
{prompt_template}

RESEARCH TOPIC:
{topic}

LINKEDIN POST:
{linkedin_post}

VISUAL CONCEPTS:
{visual_prompt}
"""

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {
                "role": "user",
                "content": final_prompt
            }
        ]
    )

    return response.choices[0].message.content

