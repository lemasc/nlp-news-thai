# nlp-news-thai

A two-phase scraper for [Thai PBS](https://www.thaipbs.or.th/) news articles. It collects article stubs from the category list API, then downloads full article content for each stub — no browser or authentication required.

---

## How it works

**Phase 1 — list:** Calls the `section-loadmore` JSON API to collect article metadata (title, publish time, ID, thumbnail, etc.) and appends each result as a line in a `.jsonl` file.

**Phase 2 — content:** For each stub collected in phase 1, calls the `content` JSON API to download the full article (body HTML, abstract, tags, related articles, etc.) and saves it as an individual `.json` file.

Both APIs are unauthenticated public endpoints on `onecms.thaipbs.or.th`.

---

## Data layout

```
data/
└── {category}/
    ├── list.jsonl           ← one article stub per line (phase 1)
    └── content/
        └── {id}.json        ← full article JSON (phase 2)
```

---

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

This installs all dependencies (`requests`, `tqdm`, `pandas`) and registers the `scrape` entry point.

---

## Usage

### Phase 1 — scrape article list

```
uv run scrape list <category> [options]
```

**Valid categories:**
`politics` `social` `foreign` `economy` `crime` `disaster` `region` `environment` `sport` `royal` `entertainment` `lifestyle` `tech`

**Options:**

| Flag | Description |
|------|-------------|
| `--pages N` | Stop after fetching N pages (24 articles/page) |
| `--articles N` | Stop after collecting N new articles |
| `--before DATE` | Only keep articles published before DATE (ISO 8601 or `YYYY-MM-DD`; treated as UTC if no timezone given) |
| `--rescrape` | Delete existing list file and start fresh |

`--pages` and `--articles` are mutually exclusive. Omitting both fetches all available pages.

**Examples:**

```bash
# Fetch all politics articles
uv run scrape list politics

# Fetch first 5 pages of economy (~120 articles)
uv run scrape list economy --pages 5

# Collect up to 50 articles from before 2026-01-01
uv run scrape list social --articles 50 --before 2026-01-01

# Re-scrape from scratch (deletes existing list first)
uv run scrape list politics --rescrape
```

### Phase 2 — download article content

```
uv run scrape content <category> [options]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--rescrape` | Delete all existing content files and re-download |

The command skips any article whose `content/{id}.json` already exists, so it is safe to re-run after interruption.

**Examples:**

```bash
# Download content for all collected politics articles
uv run scrape content politics

# Re-download everything
uv run scrape content politics --rescrape
```

---

## What to expect

- **Request delay:** 1 second between each API call (configurable via `REQUEST_DELAY` in `scrape.py`).
- **Article stubs** contain: `id`, `title`, `description`, `publishTime`, `categoryName`, `imgUrl`, `media`, `canonical`, `viewCount`, `isClip`, `isGallery`, `tags`.
- **Full content** adds: `abstract`, `content` (full body as HTML), `tags`, `voicePath`, `byAi`, `relatedNews`, `recommendedNews`, `gallery`.
- The `content` HTML field includes `<p>`, `<picture>`, `<iframe>` (YouTube), `<a>`, and `<blockquote>` elements, plus a tracking pixel `<img>` at the very end.
- Article counts per category (as of Feb 2026): politics ~2,200 · social ~700 · foreign ~670 · economy ~600 · crime ~580 · disaster ~440 · region ~350 · environment ~215 · sport ~180 · royal ~35 · entertainment ~40 · lifestyle ~30 · tech ~30.

---

## Troubleshooting

**`error: Failed to spawn: scrape` / command not found**
Run `uv sync` first. The entry point is only registered after the package is installed.

**Phase 2 says `list.jsonl not found`**
Run phase 1 for that category first: `uv run scrape list <category>`.

**HTTP errors (4xx/5xx)**
The script calls `raise_for_status()` and will exit immediately. Check your network connection. The API has no rate-limit headers, but sustained high-volume scraping may trigger temporary blocks — increase `REQUEST_DELAY` in `scrape.py` if needed.

**Re-running after interruption**
Both phases are safe to resume without `--rescrape`. Phase 1 deduplicates by article ID before appending; phase 2 skips any `content/{id}.json` that already exists.

**Thai text appears garbled**
All files are written as UTF-8 with `ensure_ascii=False`. Make sure your terminal or editor is set to UTF-8, and use `python3 -m json.tool` or `jq` to inspect content files rather than `cat` on a non-UTF-8 terminal.
