import os
from openai import OpenAI
from dotenv import load_dotenv

from storage.prompt_loader import load_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt_template = load_prompt(
    "prompts/visual_agent.txt"
)

def generate_visual_prompt(topic):

    final_prompt = f"""
{prompt_template}

TOPIC:
{topic}
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