import json
import os
import time

from openai import OpenAI
from dotenv import load_dotenv

from storage.prompt_loader import load_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_research_topic(data):

    prompt_template = load_prompt(
        "prompts/research_prompt.txt"
    )

    prompt = f"""
{prompt_template}

DATA:
{data}
"""

    for attempt in range(3):

        try:

            response = client.chat.completions.create(
                model="gpt-5",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.choices[0].message.content
            try:
                topic = json.loads(content)
            except json.JSONDecodeError as parse_error:
                raise ValueError(
                    f"Failed to parse model response as JSON.\nResponse content:\n{content}"
                ) from parse_error

            if not isinstance(topic, dict):
                raise ValueError(
                    f"Model returned JSON, but not an object. Response content:\n{content}"
                )

            return topic

        except Exception as e:

            print(f"\nAttempt {attempt + 1} failed:")
            print(e)

            time.sleep(2)

    raise Exception("Research Agent failed after 3 retries.")