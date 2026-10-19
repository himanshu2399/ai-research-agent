"""Shared configuration and client initialization for AI Research Agent."""
from pathlib import Path
from functools import lru_cache

import os
from dotenv import load_dotenv
from openai import OpenAI

# Base directory of the project
BASE_DIR = Path(__file__).parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")


def get_api_key() -> str:
    """Get and validate OpenAI API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not set. Please create a .env file with your API key.\n"
            "See README.md for setup instructions."
        )
    if api_key == "your_openai_api_key" or api_key == "y":
        raise ValueError(
            "OPENAI_API_KEY is set to a placeholder value. "
            "Please update your .env file with a valid API key."
        )
    return api_key


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Get a cached OpenAI client instance."""
    return OpenAI(api_key=get_api_key())


def get_project_path(*parts: str) -> Path:
    """Get a path relative to project root."""
    return BASE_DIR.joinpath(*parts)