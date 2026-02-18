# Thai PBS News Website Analysis - Category Archive Pages

**Analysis Date:** 2026-02-18
**Target URL Format:** `https://www.thaipbs.or.th/news/categories/{section}/archive?page={page}&section={section}`
**Example:** `https://www.thaipbs.or.th/news/categories/politics/archive?page=1&section=politics`

---

## Executive Summary

Thai PBS category archive pages are rendered client-side via a React/Redux app. Article data is **not embedded in SSR HTML** — it is fetched from a dedicated OneCMS API endpoint. This API is directly accessible without authentication, making it the ideal and simplest scraping target.

---

## 1. Primary Data Source: `section-loadmore` API

### Endpoint

```
GET https://onecms.thaipbs.or.th/api/news/api-v/section-loadmore?section={section}&page={page}
```

### Access

- ✅ No authentication required
- ✅ No cookies or special headers needed
- ✅ Direct HTTP GET — no browser required
- ✅ Returns clean JSON

### Response Structure

```json
{
  "minTs": 1771408847,
  "currentTime": "2026-02-18T10:00:47+07:00",
  "total": 2198,
  "page": 1,
  "pageCount": 92,
  "totalPage": 92,
  "header": {
    "sectionName": "การเมือง",
    "sectionEn": "politics",
    "imgUrl": ""
  },
  "items": [ ... 24 articles per page ... ]
}
```

### Article Object Fields

Each object in `items` contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | number | Unique article ID (e.g., 502330) |
| `_id` | string | MongoDB ObjectID |
| `title` | string | Article headline |
| `categoryId` | string | Category UUID |
| `categoryName` | string | Category name in Thai (e.g., "การเมือง") |
| `categoryUrl` | string | Category URL path (e.g., "/news/categories/politics") |
| `description` | string | Article abstract/summary (may be empty) |
| `imgUrl` | string | Default thumbnail URL |
| `media` | object | Multiple image sizes (see below) |
| `voicePath` | string | Audio version URL (if available) |
| `restUrl` | string | API endpoint for full article content |
| `canonical` | string | Full article URL |
| `url` | string | Article URL path |
| `tags` | null/array | Tags array (often null) |
| `viewCount` | number | Article view count |
| `isClip` | boolean | True if article is a video clip |
| `isGallery` | boolean | True if article is a gallery |
| `publishTime` | string | ISO 8601 datetime (e.g., "2026-02-18T15:28:35+07:00") |
| `createTime` | string | ISO 8601 datetime |
| `lastUpdateTime` | string | ISO 8601 datetime |

### Media Object Structure

```json
"media": {
  "default": "https://onecms.thaipbs.or.th/media/...",
  "small": "https://onecms.thaipbs.or.th/media/...",
  "thumbnailHighQuality": "https://onecms.thaipbs.or.th/media/...",
  "thumbnailRatio16per9Clean": "https://onecms.thaipbs.or.th/media/...",
  "thumbnailRatio16per9CleanHighQuality": "https://onecms.thaipbs.or.th/media/..."
}
```

---

## 2. Available Categories

All 13 categories confirmed working with the API. Slugs are used in both the archive URL and the `section` parameter.

| Slug | Thai Name | Total Articles | Total Pages |
|------|-----------|---------------|-------------|
| `politics` | การเมือง | 2,198 | 92 |
| `social` | สังคม | 691 | 29 |
| `foreign` | ต่างประเทศ | 670 | 28 |
| `economy` | เศรษฐกิจ | 592 | 25 |
| `crime` | อาชญากรรม | 575 | 24 |
| `disaster` | ภัยพิบัติ | 438 | 19 |
| `region` | ภูมิภาค | 352 | 15 |
| `environment` | สิ่งแวดล้อม | 213 | 9 |
| `sport` | กีฬา | 176 | 8 |
| `royal` | พระราชสำนัก | 33 | 2 |
| `entertainment` | ศิลปะ-บันเทิง | 39 | 2 |
| `lifestyle` | ไลฟ์สไตล์ | 29 | 2 |
| `tech` | วิทยาศาสตร์เทคโนโลยี | 27 | 2 |

> **Note:** The slug `economics` is invalid. The correct slug is `economy`.

---

## 3. Pagination

- **24 items per page** (consistent across all categories)
- Total pages available from `totalPage` in the API response
- Pagination is **zero-risk**: simply iterate `page` from `1` to `totalPage`

---

## 4. Recommended Scraping Strategy

Directly call the `section-loadmore` API. No browser or Next.js build ID needed.

```python
import requests

CATEGORIES = [
    "politics", "social", "foreign", "economy", "crime",
    "disaster", "region", "environment", "sport", "royal",
    "entertainment", "lifestyle", "tech"
]

def scrape_category(section: str):
    base_url = "https://onecms.thaipbs.or.th/api/news/api-v/section-loadmore"
    page = 1
    while True:
        resp = requests.get(base_url, params={"section": section, "page": page})
        data = resp.json()
        for article in data["items"]:
            yield article
        if page >= data["totalPage"]:
            break
        page += 1
```

---

## 5. Fallback: HTML Scraping

If the API becomes unavailable, the page can be scraped via browser automation. The articles are rendered client-side, so a full browser render is required — plain `requests` + HTML parsing will not work (page is empty without JS execution).

### Page Load Behavior

On initial load, the page fires:
1. `GET section-loadmore?section={section}&page=1` — fetches article data
2. On pagination click (soft navigation): `GET _next/data/.../archive.json` (Redux shell, no article data) then `GET section-loadmore?section={section}&page={N}`

### Article Card HTML Structure

```
article
├── div.cover-image-wrapper
│   └── img[src="https://onecms.thaipbs.or.th/media/..."]
└── div.information-container
    ├── a[href="/news/content/{id}"]
    │   └── h3  ← article title
    └── div.content-information-footer
        ├── time[datetime="ISO8601"]
        │   └── span  ← human-readable: "1 ชั่วโมงที่แล้ว" / "17 ก.พ. 69"
        └── a[href="/news/categories/{slug}"]  ← category label
```

> **Note:** No description/abstract is rendered in the card HTML. Only title, timestamp, and category are present.

### Stable CSS Selectors

| Data | Selector |
|------|----------|
| All article cards | `article` |
| Title | `article h3` |
| Article URL | `article a[href*="/news/content/"]` |
| Publish datetime (ISO) | `article time[datetime]` → `datetime` attribute |
| Publish time (display text) | `article time span:last-child` |
| Category label | `article a[href*="/news/categories/"]` |
| Thumbnail image | `article img[src*="onecms.thaipbs.or.th"]` |
| Is video clip | `article .play-icon-wrapper svg` (present if clip) |
| Pagination wrapper | `[data-section-name="pagination"]` |
| All page links | `[data-section-name="pagination"] a[href*="?page="]` |
| Last page number | last `a[href*="?page="]` in pagination → parse `?page=N` |

> **Class name stability:** Styled-components generates hashes (e.g., `ContentCardstyle__Container-sc-odesfa-0 ihdLFg`). The semantic prefix is stable but the hash suffix changes on site rebuild. Use semantic selectors (`article`, `h3`, `time`, `a[href*=...]`) instead of class names.

---

## 6. Rate Limiting Recommendations

- **Delay between requests:** 1–2 seconds
- **Concurrent requests:** Maximum 2–3
- **User-Agent:** Use a real browser user agent

---

## 7. Data Quality Notes

- ✅ All articles have complete metadata
- ✅ Timestamps in ISO 8601 format with timezone offset
- ✅ Images available in multiple sizes
- ✅ `description` field present but may be empty string for some articles (especially clips)
- ✅ `canonical` field provides the full absolute URL

---

## 8. Article Content API (`content` endpoint)

**Analysis Date:** 2026-02-18 (articles 502330, 502326, 502331 tested across politics & economy sections)

### Endpoint

```
GET https://onecms.thaipbs.or.th/api/news/api-v/content?id={article_id}
```

- ✅ No authentication required
- ✅ Returns full article content — **no HTML scraping needed**
- ✅ Consistent structure across all categories and article types

### Response Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Article ID (as string, matches numeric `id` from list API) |
| `title` | string | Full headline |
| `categoryName` | string | Thai category name (e.g., "การเมือง", "เศรษฐกิจ") |
| `categoryUrl` | string | Category URL path (e.g., "/news/categories/politics") |
| `image` / `imgUrl` | string | Primary thumbnail URL |
| `media` | object | Multiple thumbnail variants (same keys as list API, plus `thumbnailFacebook`, `thumbnailInstagram`, `thumbnailRatio1per1`, `thumbnailRatio2per3`) |
| `abstract` | string | Summary/lead paragraph. **Empty for clip articles**, filled for regular text articles. |
| `content` | string | Full article body as HTML (see below) |
| `voicePath` | string | Audio version URL (empty string if none) |
| `voiceUpdatedAt` | string | ISO 8601 (zero value `"0001-01-01T00:00:00Z"` if no audio) |
| `tags` | array | `[{"title": "...", "url": "/tags?q=..."}]` |
| `publishTime` | string | ISO 8601 with +07:00 offset (e.g., "2026-02-18T15:28:35+07:00") |
| `publishTimeTh` | string | Thai format (e.g., "18 ก.พ. 2569, 15:28 น.") |
| `lastUpdateTime` | string | ISO 8601 last edit timestamp |
| `viewCount` | number | Live view count |
| `credit` | null/string | Image/source credit |
| `byAi` | string | AI-generated flag (empty string = no, "true" = yes) |
| `relatedNews` | array | Related article stubs (often empty) |
| `recommendedNews` | array | 9 recommended articles (stubs with same list-API fields) |
| `gallery` | null/array | Gallery images (null for non-gallery articles) |

### `content` HTML Structure

The `content` field is raw HTML with these element types:

| Element | Description |
|---------|-------------|
| `<p>` | Main text paragraphs (may be empty `<p></p>` spacers) |
| `<picture>/<source>/<img>` | Inline article images |
| `<iframe>` | Embedded video (YouTube: `https://www.youtube.com/embed/...`) |
| `<a>` | Hyperlinks (inline references and "read also" links at bottom) |
| `<blockquote>` | Quoted text |
| `<img src="https://onecms.thaipbs.or.th/api/web/stats/view?...">` | **Tracking pixel — always at the very end, must be excluded** |

**Extracting clean body text:**
```python
from bs4 import BeautifulSoup

def extract_text(content_html: str) -> str:
    soup = BeautifulSoup(content_html, "html.parser")
    # Remove tracking pixel
    for img in soup.find_all("img", src=lambda s: s and "stats/view" in s):
        img.decompose()
    # Remove iframes (video embeds)
    for el in soup.find_all("iframe"):
        el.decompose()
    # Get text from paragraphs only
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    return "\n\n".join(p for p in paragraphs if p)
```

### Recommended Full Scraping Strategy

```python
import requests, time

def scrape_all():
    base = "https://onecms.thaipbs.or.th/api/news/api-v"
    for section in CATEGORIES:
        page = 1
        while True:
            resp = requests.get(f"{base}/section-loadmore", params={"section": section, "page": page})
            data = resp.json()
            for item in data["items"]:
                time.sleep(1)
                article = requests.get(f"{base}/content", params={"id": item["id"]}).json()
                yield article   # has title, abstract, content HTML, tags, publishTime, etc.
            if page >= data["totalPage"]:
                break
            page += 1
            time.sleep(1)
```

---

## 9. Article HTML Page Structure (for reference / fallback)

**Confirmed selectors** (tested on articles 502330, 502326 — consistent):

| Data | Selector | Notes |
|------|----------|-------|
| Title | `h1` | Full headline |
| Publish datetime (ISO) | `header time[datetime]` → `datetime` attr | e.g., "2026-02-18T15:28:35+07:00" |
| Category | `header a[href*="/news/categories/"]` | text = Thai name, `href` = slug path |
| View count | `header [data-icon="eye"]` parent element | Display text like "1,062" (no machine-readable attr) |
| Article body | `#item-description` | Same HTML as API `content` field |
| Tags | `[data-section-name="กลุ่มแท็ก"] a` | Text only |

**Header meta items structure** (in `[class*="MetaContainer"]`):
1. `<time datetime="ISO8601">` with `data-icon="calendar-days"` → publish date
2. `<div>` with `data-icon="clock"` → display time (e.g., "15:28") — no machine-readable datetime
3. `<div>` with `data-icon="eye"` → view count

**`#item-description` content child tags:** `P`, `PICTURE`, `IFRAME`, `BLOCKQUOTE`, `DIV` (tracking pixel wrapper)

> **Note:** The `#item-description` content is identical to the API `content` field. Prefer the API.

---

**End of Analysis**
