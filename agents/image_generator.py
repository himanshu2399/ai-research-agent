import os
import base64

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image(image_prompt):

    response = client.images.generate(
        model="gpt-image-1",
        prompt=image_prompt,
        size="1024x1024"
    )

    image_base64 = response.data[0].b64_json

    image_bytes = base64.b64decode(image_base64)

    if not os.path.exists("outputs/images"):
        os.makedirs("outputs/images")

    image_path = "outputs/images/generated_image.png"

    with open(image_path, "wb") as f:
        f.write(image_bytes)

    return image_path