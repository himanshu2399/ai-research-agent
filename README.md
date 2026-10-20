# AI Research Agent

AI Research Agent collects current technical topics from public sources and turns them into a LinkedIn content package. It focuses on **DevOps, cloud engineering (especially GCP), platform engineering, SRE, Kubernetes, and infrastructure topics** — not generic AI/LLM content. It uses OpenAI models to select a topic, draft and review the post, create an image prompt, and generate a companion image.

## What It Does

Running the application performs this workflow:

1. **Cleans up previous outputs** — deletes all previous `post_*.md` files and `images/` from `outputs/` to ensure only the most recent run remains.
2. Collects up to five recent entries from each configured RSS feed.
3. Collects up to ten repositories from GitHub Trending.
4. Collects up to ten front-page stories from Hacker News through the Algolia Hacker News API.
5. Asks GPT-5 to select one evidence-supported topic focused on **DevOps, cloud (GCP), Kubernetes, platform engineering, or infrastructure**. Previous topics from `outputs/topic_memory.md` are injected into the prompt so duplicates are avoided.
6. Asks GPT-5 to draft LinkedIn content and develop a visual concept using the prompt templates in `prompts/`. The memory of past topics is included here too.
7. Generates a 1024 x 1024 image with `gpt-image-1` (with retry + timeout protection).
8. Asks GPT-5 to review and assemble the research and draft into a final Markdown deliverable.
9. Saves the output, then writes the new topic into `outputs/topic_memory.md` so future runs avoid duplicates.
10. Prints the final deliverable and saves it under `outputs/`.

> **Note on duplicates:** If the selected topic is too similar to a previously generated one (tracked in `outputs/topic_memory.md`), the pipeline stops with a warning instead of producing a duplicate post. To force a fresh topic, delete `outputs/topic_memory.md`.

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

### Topic Focus (Updated)

The agent is tuned for a **DevOps / GCP engineer audience**. The research prompt prioritizes:

- DevOps practices (CI/CD, automation, tooling)
- GCP content (GKE, Cloud Run, BigQuery, Compute Engine, networking)
- Kubernetes operations
- Platform engineering and SRE topics
- Infrastructure-as-code, cost optimization, security, observability

Topics about LLM internals, generic AI hype, or unrelated research are explicitly excluded from selection.

### Memory and Duplicate Prevention

- `outputs/topic_memory.md` tracks every generated topic with a timestamp, summary, and file reference.
- Each run injects previous topics into the LLM prompts so new posts are meaningfully different.
- If a duplicate is detected, the pipeline stops with a clear message.
- To reset memory (force a new topic even if similar to a past one): `rm outputs/topic_memory.md`

### Output Cleanup

Every fresh run automatically deletes previous `post_*.md` and `image_*.png` files in `outputs/` before generating anything new. Only the most recent post and image remain after a successful run.

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
│   ├── image_generator.py       # Generates images (with retry + timeout)
│   ├── linkedin_writer.py       # Drafts LinkedIn copy with memory context
│   ├── orchestrator_agent.py    # Reviews and assembles the final deliverable
│   ├── topic_researcher.py      # Selects a topic with memory-aware prompts
│   └── visual_agent.py          # Develops the visual concept and image prompt
├── collectors/
│   ├── github_collector.py      # Reads GitHub Trending
│   ├── hn_collector.py          # Reads Hacker News via Algolia
│   └── rss_collector.py         # Reads configured RSS feeds
├── outputs/
│   ├── images/                   # Generated companion image (cleaned each run)
│   └── topic_memory.md           # Previous topics (persists between runs)
├── prompts/                     # Editable prompts for each content stage
├── storage/
│   ├── prompt_loader.py          # Loads prompt text from disk
│   ├── save_output.py            # Saves timestamped Markdown deliverables
│   └── topic_memory.py           # Tracks and checks previous topics
└── main.py                       # Application entry point
```

## Outputs

- Final Markdown deliverables are written to `outputs/post_YYYYMMDD_HHMMSS.md`.
- The generated image is written to `outputs/images/image_YYYYMMDD_HHMMSS.png`.
- `outputs/topic_memory.md` persists previous topics across runs.
- On each fresh run, previous `post_*.md` and `image_*.png` files are deleted automatically.

## Customization

- Edit the RSS feed list and per-source collection limits in `collectors/rss_collector.py`, `collectors/github_collector.py`, and `collectors/hn_collector.py`.
- Adjust topic selection, LinkedIn style, visual direction, and final assembly in the corresponding files under `prompts/`. The `research_prompt.txt` defines the audience and excluded topics (e.g., no generic LLM/AI hype).
- Change model names, image dimensions, and generation behavior in the relevant modules under `agents/`.
- Change where and how deliverables are stored in `storage/save_output.py` and `agents/image_generator.py`.
- To disable duplicate checking or change memory behavior, edit `storage/topic_memory.py`.

## Current Limitations

- Feed and web-page content can change or become unavailable, and the amount of returned data depends on each upstream service.
- GitHub Trending is parsed from its HTML page, so markup changes may require updates to the collector.
- Collector requests currently have no explicit timeout or retry policy (though the image generator has both); a network or upstream error can interrupt a run.
- The image generation uses `gpt-image-1`, which can be slow; retries with backoff are included but long hangs may still occur.
- No automated test suite or dependency lock file is currently included.
