# AI Research Agent

AI Research Agent collects current technical topics from public sources and turns them into a LinkedIn content package. It uses OpenAI models to select a topic, draft and review the post, create an image prompt, and generate a companion image.

## What It Does

Running the application performs this workflow:

1. Collects up to five recent entries from each configured RSS feed.
2. Collects up to ten repositories from GitHub Trending.
3. Collects up to ten front-page stories from Hacker News through the Algolia Hacker News API.
4. Asks GPT-5 to select one evidence-supported topic and return a structured topic summary.
5. Asks GPT-5 to draft LinkedIn content and develop a visual concept using the prompt templates in `prompts/`.
6. Generates a 1024 x 1024 image with `gpt-image-1`.
7. Asks GPT-5 to review and assemble the research and draft into a final Markdown deliverable.
8. Prints the final deliverable and saves it under `outputs/`.

## Requirements

- Python 3.10 or newer
- An OpenAI API key with access to the models used by the application (`gpt-5` and `gpt-image-1`)
- Internet access to the configured RSS feeds, GitHub, Hacker News Algolia API, and OpenAI API

Python packages used by the application:

- `openai`
- `python-dotenv`
- `feedparser`
- `requests`
- `beautifulsoup4`

## Setup

Open a terminal in the `ai-research-agent` project directory. Create and activate a virtual environment:

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install openai python-dotenv feedparser requests beautifulsoup4
```

## Configuration

Set your OpenAI API key in a `.env` file in the project directory:

```dotenv
OPENAI_API_KEY=your_openai_api_key
```

Keep the key private. Do not commit a `.env` file containing a real API key or paste the key into source code.

## Run

From the project directory, with the virtual environment activated, run:

```bash
python main.py
```

The program uses paths relative to the current working directory to load prompt files and save results, so run it from the project directory. It prints progress and the final deliverable to the terminal. OpenAI API usage and image generation may incur charges according to your account's pricing and limits.

## Data Sources

The collectors are configured in `collectors/`:

| Source | What is collected |
| --- | --- |
| AWS DevOps Blog | Up to five feed entries |
| Google Cloud Developers & Practitioners Blog | Up to five feed entries |
| Kubernetes Blog | Up to five feed entries |
| Cloud Native Computing Foundation (CNCF) | Up to five feed entries |
| GitHub Trending | Up to ten repositories from the trending page |
| Hacker News | Up to ten front-page stories from the Algolia API |

These sources and collection limits are currently hard-coded in the collector modules. The topic-selection prompt instructs the model to treat collected text as reference material, avoid unsupported claims, and return only the specified JSON fields.

## Project Layout

```text
ai-research-agent/
├── agents/
│   ├── image_generator.py       # Generates and writes the companion image
│   ├── linkedin_writer.py       # Drafts LinkedIn copy
│   ├── orchestrator_agent.py    # Reviews and assembles the final deliverable
│   ├── topic_researcher.py      # Selects a topic and returns structured JSON
│   └── visual_agent.py          # Develops the visual concept and image prompt
├── collectors/
│   ├── github_collector.py      # Reads GitHub Trending
│   ├── hn_collector.py          # Reads Hacker News via Algolia
│   └── rss_collector.py         # Reads configured RSS feeds
├── outputs/
│   └── images/                  # Generated companion image
├── prompts/                    # Editable prompts for each content stage
├── storage/
│   ├── prompt_loader.py         # Loads prompt text from disk
│   └── save_output.py           # Saves timestamped Markdown deliverables
└── main.py                      # Application entry point
```

## Outputs

- Final Markdown deliverables are written to `outputs/post_YYYYMMDD_HHMMSS.md`.
- The generated image is written to `outputs/images/generated_image.png`.
- The image path is printed in the terminal. The image is not versioned by run; a subsequent run overwrites `generated_image.png`.

## Customization

- Edit the RSS feed list and per-source collection limits in `collectors/rss_collector.py`, `collectors/github_collector.py`, and `collectors/hn_collector.py`.
- Adjust topic selection, LinkedIn style, visual direction, and final assembly in the corresponding files under `prompts/`.
- Change model names, image dimensions, and generation behavior in the relevant modules under `agents/`.
- Change where and how deliverables are stored in `storage/save_output.py` and `agents/image_generator.py`.

## Current Limitations

- Feed and web-page content can change or become unavailable, and the amount of returned data depends on each upstream service.
- GitHub Trending is parsed from its HTML page, so markup changes may require updates to the collector.
- Collector requests currently have no explicit timeout or retry policy; a network or upstream error can interrupt a run.
- The generated image uses a fixed filename and is overwritten on each successful image generation.
- No automated test suite or dependency lock file is currently included.
