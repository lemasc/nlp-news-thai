# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

Requires [uv](https://docs.astral.sh/uv/). Install dependencies and register the `scrape` entry point:

```bash
uv sync
```

## Running the scraper

```bash
# Phase 1 — collect article stubs into data/{category}/list.jsonl
uv run scrape list <category> [--pages N | --articles N] [--before DATE] [--rescrape]

# Phase 2 — download full article JSON into data/{category}/content/{id}.json
uv run scrape content <category> [--rescrape]
```

Valid categories: `politics` `social` `foreign` `economy` `crime` `disaster` `region` `environment` `sport` `royal` `entertainment` `lifestyle` `tech`

## Architecture

The project has two components:

**`scrape.py`** — single-module CLI. Calls two unauthenticated OneCMS JSON APIs:
- `section-loadmore?section={cat}&page={n}` → article stubs (24/page)
- `content?id={id}` → full article JSON including HTML body

Both phases are resumable: phase 1 deduplicates by article ID before appending to the `.jsonl`; phase 2 skips any `content/{id}.json` that already exists. `REQUEST_DELAY = 1.0` (seconds) controls the inter-request pause.

**`notebooks/build_dataset.ipynb`** — post-processing notebook that reads all `data/*/content/*.json` files, strips tracking pixels and non-paragraph HTML from the `content` field via BeautifulSoup, and writes a flat `data/dataset.jsonl` with fields: `id`, `title`, `categoryName`, `abstract`, `publishedTime`, `tags`, `content_text`.

## Data layout

```
data/
├── dataset.jsonl              ← built by notebook (all categories combined)
└── {category}/
    ├── list.jsonl             ← article stubs, one per line (phase 1 output)
    └── content/
        └── {id}.json          ← full article JSON (phase 2 output)
```

## Key notes

- The `content` HTML field always ends with a tracking pixel (`<img src="...stats/view?...">`) that must be excluded when extracting text.
- The `byAi` field is an empty string (not a boolean) when false; `"true"` when the article was AI-generated.
- `--pages` and `--articles` flags are mutually exclusive in the `list` subcommand.
- Run `uv sync` before first use — the `scrape` entry point is only available after package installation.
