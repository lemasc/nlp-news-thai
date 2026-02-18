import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dateutil import parser as dateutil_parser
from tqdm import tqdm

API_BASE = "https://onecms.thaipbs.or.th/api/news/api-v"
REQUEST_DELAY = 1.0

VALID_CATEGORIES = [
    "politics", "social", "foreign", "economy", "crime",
    "disaster", "region", "environment", "sport", "royal",
    "entertainment", "lifestyle", "tech",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
    )
}


def api_get(endpoint: str, params: dict) -> dict:
    url = f"{API_BASE}/{endpoint}"
    resp = requests.get(url, params=params, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def load_existing_ids(list_file: Path) -> set:
    ids = set()
    if not list_file.exists():
        return ids
    with list_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                article = json.loads(line)
                ids.add(int(article["id"]))
            except (json.JSONDecodeError, KeyError, ValueError):
                pass
    return ids


def parse_date(date_str: str) -> datetime:
    """Parse a date string; treat timezone-naive result as UTC."""
    dt = dateutil_parser.parse(date_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def cmd_list(args):
    category = args.category
    list_file = Path("data") / category / "list.jsonl"
    list_file.parent.mkdir(parents=True, exist_ok=True)

    if args.rescrape and list_file.exists():
        list_file.unlink()
        print(f"Deleted existing {list_file}")

    existing_ids = load_existing_ids(list_file)

    before_dt = parse_date(args.before) if args.before else None

    # Fetch page 1 to learn totalPage
    print(f"Fetching page 1 for category '{category}'...")
    first_data = api_get("section-loadmore", {"section": category, "page": 1})
    total_page = first_data["totalPage"]
    total_articles = first_data.get("total", 0)
    print(f"Category '{category}': {total_articles} articles across {total_page} pages")

    pages_limit = args.pages      # None if not specified
    articles_limit = args.articles  # None if not specified

    new_count = 0
    done = False

    with list_file.open("a", encoding="utf-8") as f:
        for page in range(1, total_page + 1):
            if page == 1:
                data = first_data
            else:
                time.sleep(REQUEST_DELAY)
                data = api_get("section-loadmore", {"section": category, "page": page})

            for article in data["items"]:
                article_id = int(article["id"])

                # Date filter: skip articles published on or after before_dt
                if before_dt is not None:
                    pub_str = article.get("publishTime", "")
                    if pub_str:
                        pub_dt = parse_date(pub_str)
                        if pub_dt >= before_dt:
                            continue

                # Deduplication
                if article_id in existing_ids:
                    continue

                f.write(json.dumps(article, ensure_ascii=False) + "\n")
                existing_ids.add(article_id)
                new_count += 1

                if articles_limit is not None and new_count >= articles_limit:
                    print(f"Reached article limit ({articles_limit}). Stopping.")
                    done = True
                    break

            if done:
                break

            if pages_limit is not None and page >= pages_limit:
                print(f"Reached page limit ({pages_limit}). Stopping.")
                break

    print(f"Done. Collected {new_count} new articles for '{category}'.")


def cmd_content(args):
    category = args.category
    list_file = Path("data") / category / "list.jsonl"

    if not list_file.exists():
        print(f"Error: {list_file} not found. Run 'scrape list {category}' first.")
        return

    content_dir = Path("data") / category / "content"
    content_dir.mkdir(parents=True, exist_ok=True)

    if args.rescrape:
        deleted = 0
        for json_file in content_dir.glob("*.json"):
            json_file.unlink()
            deleted += 1
        print(f"Deleted {deleted} existing content files in {content_dir}")

    # Load all stubs from the list
    stubs = []
    with list_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                stubs.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    total = len(stubs)
    pending = [s for s in stubs if not (content_dir / f"{s['id']}.json").exists()]
    print(f"Content: {len(pending)}/{total} articles pending download")

    for stub in tqdm(pending, desc="Downloading content"):
        article_id = stub["id"]
        out_file = content_dir / f"{article_id}.json"
        try:
            content = api_get("content", {"id": article_id})
            with out_file.open("w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"\nError fetching article {article_id}: {e}")
        time.sleep(REQUEST_DELAY)

    print(f"Done. Content saved to {content_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Thai PBS news scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  scrape list politics --pages 2\n"
            "  scrape list economy --articles 10 --before 2026-01-01\n"
            "  scrape content politics\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- list subcommand ---
    list_parser = subparsers.add_parser("list", help="Scrape article list for a category")
    list_parser.add_argument("category", choices=VALID_CATEGORIES, help="Category slug")
    limit_group = list_parser.add_mutually_exclusive_group()
    limit_group.add_argument("--pages", type=int, metavar="N", help="Max pages to fetch")
    limit_group.add_argument("--articles", type=int, metavar="N", help="Max articles to collect")
    list_parser.add_argument(
        "--before",
        metavar="DATE",
        help="Only include articles published before DATE (ISO 8601 or YYYY-MM-DD, treated as UTC if no timezone)",
    )
    list_parser.add_argument(
        "--rescrape",
        action="store_true",
        help="Delete existing list and re-scrape from scratch",
    )
    list_parser.set_defaults(func=cmd_list)

    # --- content subcommand ---
    content_parser = subparsers.add_parser(
        "content", help="Download full article content for a category"
    )
    content_parser.add_argument("category", choices=VALID_CATEGORIES, help="Category slug")
    content_parser.add_argument(
        "--rescrape",
        action="store_true",
        help="Delete existing content and re-download everything",
    )
    content_parser.set_defaults(func=cmd_content)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
