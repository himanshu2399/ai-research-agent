from datetime import datetime
import os

def save_to_file(content):

    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"outputs/post_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

    return filename