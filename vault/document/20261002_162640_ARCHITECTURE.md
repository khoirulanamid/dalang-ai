# threads-affiliate — Architecture Overview

> **Document type:** Explanation (Diátaxis)
> **Audience:** Dalang-AI team members, backend engineers, AI agents integrating with this system.

---

## Definition

`threads-affiliate` is a Python automation toolkit that posts 2–3 chained text posts to Threads (Meta) using session cookies, rotating hook templates, and a Markdown-based affiliate link database. It runs without any official Threads API — authentication uses browser session cookies extracted from Chrome.

---

## System Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                        OPERATOR / DALANG-AI                     │
│  (dispatches post tasks via CLI or Python API)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ task payload
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    threads-affiliate toolkit                     │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐   │
│  │ AffiliateDB  │   │ContentGenerator│  │  DedupChecker    │   │
│  │ (Markdown)   │──▶│ (templates/) │──▶│ (post_history.   │   │
│  └──────────────┘   └──────────────┘   │  json)           │   │
│                                        └────────┬─────────┘   │
│                                                 │ approved     │
│                                                 ▼             │
│                                        ┌──────────────────┐   │
│                                        │  ThreadsPoster   │   │
│                                        │  (Playwright /   │   │
│                                        │   Chromium)      │   │
│                                        └────────┬─────────┘   │
└─────────────────────────────────────────────────┼─────────────┘
                                                  │ HTTPS
                                                  ▼
                                        ┌──────────────────┐
                                        │  Threads (Meta)  │
                                        │  www.threads.com │
                                        └──────────────────┘
```

---

## Component Inventory

| Component | Module | Responsibility |
|-----------|--------|----------------|
| `AffiliateDatabase` | `threads_poster/database.py` | Reads and writes the Markdown affiliate link database. Returns the next unused link for a given category. |
| `ContentGenerator` | `threads_poster/content_generator.py` | Loads hook templates from `templates/`, renders a 2–3 post chain with product name and affiliate link substituted. |
| `DedupChecker` | `threads_poster/dedup.py` | Reads and writes `post_history.json`. Rejects duplicate affiliate links and same-style hook bursts (≥ 2 consecutive same style). |
| `ThreadsPoster` | `threads_poster/poster.py` | Drives Playwright/Chromium to log in via session cookies and submit posts to Threads. |
| `CookieManager` | `threads_poster/cookie_manager.py` | Extracts Instagram/Threads session cookies from a Chrome profile and validates them against the Instagram API. |
| CLI | `threads_poster/cli.py` | `python -m threads_poster.cli` entry point. Subcommands: `setup`, `post`, `post-auto`, `batch`. |

---

## Data Flow — Full Posting Cycle

```
Step 1: RESOLVE LINK
  AffiliateDatabase.next_unused(category)
      reads data/affiliate_links.md
      returns (affiliate_link, product_name, category)

Step 2: GENERATE CONTENT
  ContentGenerator.generate_chain(
      product, affiliate_link, category, hook_style, num_posts
  )
      loads templates/hooks_{category}.json
      loads templates/post2_templates.json
      loads templates/post3_cta_templates.json
      returns PostChain dict {post_1, post_2, post_3?, hook_category, hook_text}

Step 3: DEDUP CHECK
  DedupChecker.check(affiliate_link, hook_category, hook_text, category)
      reads data/post_history.json
      REJECT if affiliate_link already in history
      REJECT if last 2 posts used same hook_category
      PASS → proceed

Step 4: POST
  ThreadsPoster.post(product, affiliate_link, hook_text, post_2, post_3, ...)
      launches Playwright Chromium (headless=True)
      loads cookies from ~/.threads_poster/cookies/session.json
      navigates to www.threads.com
      types post_1 → submits
      types post_2 as reply → submits
      types post_3 (CTA + link) as reply → submits
      waits 10 s → verifies on profile page
      returns PostResult

Step 5: RECORD
  DedupChecker.record(entry)
      appends to data/post_history.json
  AffiliateDatabase.mark_used(affiliate_link, note)
      updates data/affiliate_links.md row: ❌ UNUSED → ✅ USED (date)
```

---

## Template System

### Hook templates (`templates/hooks_{category}.json`)

Each file covers one product category (`skincare`, `parfum`, `haircare`, `makeup`). The file contains a `hooks` object keyed by hook style. Each style maps to a list of template strings with `{product}` as the only substitution variable.

**Hook styles (9 canonical):**

| Style | Indonesian intent |
|-------|-------------------|
| `edukasi` | Educational fact about the product |
| `validasi_mental` | Empathy / emotional validation |
| `storytelling` | Personal experience narrative |
| `problem_solving` | Problem → solution framing |
| `hook_pancingan` | Curiosity trigger |
| `transformasi` | Before/after transformation |
| `social_proof` | Popularity / trending signal |
| `urgency` | Scarcity / time pressure |
| `controversy` | Contrarian hot-take |

### Post 2 templates (`templates/post2_templates.json`)

Category-keyed body text. Substitution variable: `{product}`. Selected randomly from the matching category list, or from `default` if the category key is absent.

### Post 3 CTA templates (`templates/post3_cta_templates.json`)

Closing post with affiliate link. Substitution variables: `{product}`. The affiliate link is appended as a bare URL on a new line after the template text.

---

## Anti-Spam Architecture

The system uses three independent layers to avoid Threads spam detection:

1. **Link dedup** — `DedupChecker` rejects any affiliate link that appears in `post_history.json`. Each Shopee link is used exactly once.

2. **Hook style rotation** — `DedupChecker` rejects a hook style if the last 2 consecutive posts used the same style. This prevents repetitive content patterns.

3. **Rate cap** — The CLI enforces a maximum of 5 posts per day per account. The `batch` subcommand respects this limit and exits with code `3` when the cap is reached.

---

## File Layout

```
threads-affiliate/
├── threads_poster/          # Python package (importable)
│   ├── __init__.py          # Exports: ThreadsPoster, ContentGenerator, DedupChecker, AffiliateDatabase
│   ├── cli.py               # CLI entry point
│   ├── content_generator.py # Template rendering
│   ├── cookie_manager.py    # Cookie extraction + validation
│   ├── database.py          # Markdown affiliate link DB
│   ├── dedup.py             # Dedup + history
│   └── poster.py            # Playwright browser automation
├── templates/               # Content templates (JSON)
│   ├── hooks_skincare.json
│   ├── hooks_parfum.json
│   ├── hooks_haircare.json
│   ├── hooks_makeup.json
│   ├── post2_templates.json
│   └── post3_cta_templates.json
├── schemas/                 # JSON Schema validation files
│   ├── hooks.schema.json
│   ├── post-result.schema.json
│   └── post-history.schema.json
├── docs/                    # Documentation (this directory)
├── examples/                # Runnable example scripts
│   ├── single_post.py
│   ├── batch_schedule.py
│   └── cron_integration.sh
├── data/                    # Runtime data (gitignored)
│   ├── affiliate_links.md   # Affiliate link database
│   └── post_history.json    # Post history (dedup source)
└── AGENTS.md                # Canonical guide for AI agents
```

---

## Authentication Model

`threads-affiliate` does **not** use the official Threads API. Authentication works through Instagram session cookies shared via Meta SSO:

1. The operator logs into Instagram in Chrome.
2. `CookieManager.extract_cookies()` reads the Chrome profile's cookie store and writes a `session.json` file containing Instagram and Threads cookies.
3. `ThreadsPoster` loads `session.json` and injects the cookies into a Playwright browser context before navigating to `www.threads.com`.
4. The session remains valid until Instagram invalidates it (typically 30–90 days of inactivity).

**Cookie file location:** `~/.threads_poster/cookies/session.json`
**File permissions:** `600` (owner read/write only — enforced by `CookieManager`)

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error (exception, missing file, invalid args) |
| `2` | Dedup rejection (link already used or hook style burst) |
| `3` | Daily rate cap reached (≥ 5 posts today) |
| `4` | Cookie validation failed (session expired) |
| `5` | Playwright / browser error during post |

---

## Design Decisions

### Why Markdown for the affiliate database?

The affiliate link database (`data/affiliate_links.md`) uses a Markdown table format. This makes it editable by humans in any text editor or GitHub web UI without needing a database client. The `AffiliateDatabase` class parses the table rows with a regex and writes updates in-place.

### Why session cookies instead of the official API?

The official Threads API (as of 2026) does not support automated posting for affiliate content at the required volume. Session cookie automation is the only viable path. The system is designed to stay within Threads' observable rate limits (≤ 5 posts/day/account) to reduce ban risk.

### Why 2–3 post chains instead of single posts?

Threads' algorithm favors reply chains. A 3-post chain (hook → body → CTA) keeps the affiliate link in the third post, which reduces the chance of the first post being flagged as spam. The hook post reads as organic content.

### Why JSON-based templates instead of a database?

Templates are static content that changes infrequently. JSON files in `templates/` are version-controlled, diff-readable, and require no runtime database dependency. Adding a new hook style or category requires only a new JSON file.
