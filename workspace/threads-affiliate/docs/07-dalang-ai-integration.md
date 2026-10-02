# Dalang-AI Integration Guide — threads-affiliate

> **Document type:** How-To Guide / Reference (Diátaxis)
> **Audience:** Dalang-AI core developers, orchestrator agents, and automated worker runners.

---

## Overview

This guide explains how Dalang-AI integrates with `threads-affiliate` to dispatch, execute, and monitor automated affiliate posts on Meta Threads.

`threads-affiliate` provides two integration surfaces:
1. **Python API** — Direct module imports for in-process execution inside Dalang-AI workers.
2. **CLI / Subprocess Interface** — Shell invocation with exit codes and structured JSON output for decoupled job dispatch.

---

## 1. Prerequisites and Environment Setup

### System Requirements

- Python 3.10+
- Chromium browser binaries installed via Playwright
- Valid session cookies at `~/.threads_poster/cookies/session.json`
- Permissions on `session.json` set to `600` (read/write by owner only)

### Dependency Installation

Install dependencies from the repository root:

```bash
cd /root/storage/projects/dalang-ai/workspace/threads-affiliate
pip install -r requirements.txt
playwright install chromium
```

### Pre-Flight Cookie Verification

Before dispatching any post task, Dalang-AI must verify that the session cookies remain valid.

Run the CLI check:

```bash
python -m threads_poster.cli setup --validate-cookies --cookies ~/.threads_poster/cookies/session.json
```

Or verify programmatically in Python:

```python
from pathlib import Path
from threads_poster.cookie_manager import validate_cookies

cookies_path = Path.home() / ".threads_poster/cookies/session.json"
is_valid, details = validate_cookies(cookies_path)

if not is_valid:
    error_message = details.get("error", "Unknown validation error")
    raise RuntimeError(f"Session cookies invalid: {error_message}")

print(f"Session authenticated. ds_user_id: {details.get('session_user_id')}")
```

---

## 2. Architecture and Data Flow

The following text diagram details how Dalang-AI coordinates a posting task from product selection to post verification.

```
+-------------------------------------------------------------------------------+
|                             DALANG-AI ORCHESTRATOR                            |
|                                                                               |
|  1. Select Category / Campaign Target                                         |
|  2. Dispatch Post Job to Worker Pool                                          |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       DALANG-AI WORKER / CANTRIK POOL                         |
|                                                                               |
|   Step A: Affiliate Link Resolution                                           |
|   +------------------------------------------------------------------------+  |
|   | AffiliateDatabase.next_unused(category="skincare")                     |  |
|   | Input:  data/affiliate_links.md                                        |  |
|   | Output: link="https://s.shopee.co.id/XYZ", product="Brand Gel", cat    |  |
|   +------------------------------------------------------------------------+  |
|                                       |                                       |
|                                       v                                       |
|   Step B: Content Generation & Validation                                     |
|   +------------------------------------------------------------------------+  |
|   | ContentGenerator.generate_chain(product, link, cat, hook_style, 3)     |  |
|   | - Load template: templates/hooks_skincare.json                         |  |
|   | - Enforce Hook Constraints: <= 80 chars, Gen-Z casual ('gw'/'lo')      |  |
|   | - Render Post 1 (Hook), Post 2 (Review body), Post 3 (CTA + Link)      |  |
|   +------------------------------------------------------------------------+  |
|                                       |                                       |
|                                       v                                       |
|   Step C: Deduplication & Burst Prevention Gate                               |
|   +------------------------------------------------------------------------+  |
|   | DedupChecker.check(link, hook_category, hook_text, category)           |  |
|   | - Rejects if link already exists in data/post_history.json             |  |
|   | - Rejects if hook_category used in last 2 consecutive posts            |  |
|   | If REJECTED -> pick alternative hook_style or abort task               |  |
|   +------------------------------------------------------------------------+  |
|                                       | PASS                                  |
|                                       v                                       |
|   Step D: Browser Automation & Dispatch                                       |
|   +------------------------------------------------------------------------+  |
|   | ThreadsPoster.post(product, link, hook_text, post_2, post_3, ...)      |  |
|   | - Headless Chromium launches with ~/.threads_poster/cookies/           |  |
|   | - Types and submits Post 1 -> Wait 3s                                  |  |
|   | - Types and submits Post 2 as reply -> Wait 3s                         |  |
|   | - Types and submits Post 3 with link -> Wait 10s                       |  |
|   | - Navigates to user profile to verify publication                      |  |
|   | - Returns PostResult object                                            |  |
|   +------------------------------------------------------------------------+  |
|                                       |                                       |
|                                       v                                       |
|   Step E: State Finalization                                                  |
|   +------------------------------------------------------------------------+  |
|   | DedupChecker.record(post_result_dict) -> updates post_history.json     |  |
|   | AffiliateDatabase.mark_used(link, note) -> updates links.md row        |  |
|   +------------------------------------------------------------------------+  |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                             META THREADS PLATFORM                             |
|                               www.threads.com                                 |
+-------------------------------------------------------------------------------+
```

---

## 3. Dispatch Methods for Dalang-AI

### Method A: In-Process Python Dispatch (Recommended for Dalang-AI Workers)

Use this method when running directly inside Dalang-AI agent scripts.

```python
"""Dalang-AI worker posting runner."""
from pathlib import Path
from threads_poster import (
    AffiliateDatabase,
    ContentGenerator,
    DedupChecker,
    ThreadsPoster,
)

def dispatch_threads_task(
    category: str,
    db_path: str = "data/affiliate_links.md",
    history_path: str = "data/post_history.json",
    templates_dir: str = "templates",
    cookies_path: str = "~/.threads_poster/cookies/session.json",
    hook_style: str = "edukasi",
    num_posts: int = 3,
    image_path: str | None = None,
    username: str = "",
) -> dict:
    """Execute a single affiliate posting task from start to finish.

    Parameters:
        category: Product category ('skincare', 'parfum', 'haircare', 'makeup').
        db_path: Path to Markdown affiliate link database.
        history_path: Path to post history JSON file.
        templates_dir: Path to directory containing hook JSON templates.
        cookies_path: Path to Instagram/Threads session JSON file.
        hook_style: Target hook style (e.g. 'edukasi', 'problem_solving').
        num_posts: Number of posts in thread chain (2 or 3).
        image_path: Optional path to product image for post 1.
        username: Threads handle without '@' for post verification.

    Returns:
        dict: Execution summary with status, post URL, and error message if any.
    """
    # 1. Resolve unused affiliate link from database
    db = AffiliateDatabase(db_path)
    try:
        affiliate_link, product, resolved_category = db.next_unused(category)
    except StopIteration:
        return {
            "status": "aborted",
            "reason": f"No unused links found for category '{category}' in {db_path}",
        }

    # 2. Generate content chain from templates
    generator = ContentGenerator(templates_dir=templates_dir)
    chain = generator.generate_chain(
        product=product,
        affiliate_link=affiliate_link,
        category=resolved_category,
        hook_style=hook_style,
        num_posts=num_posts,
    )

    # 3. Deduplication and burst check
    dedup = DedupChecker(history_path)
    ok, reason = dedup.check(
        affiliate_link=affiliate_link,
        hook_category=chain["hook_category"],
        hook_text=chain["hook_text"],
        category=resolved_category,
    )
    if not ok:
        return {
            "status": "rejected_dedup",
            "reason": reason,
            "affiliate_link": affiliate_link,
        }

    # 4. Post chain via Playwright browser
    poster = ThreadsPoster(cookies_path=cookies_path, headless=True)
    result = poster.post(
        product=chain["product_name"],
        affiliate_link=chain["affiliate_link"],
        hook_text=chain["post_1"],
        post_2=chain.get("post_2"),
        post_3=chain.get("post_3"),
        hook_category=chain["hook_category"],
        category=resolved_category,
        image_path=image_path,
        username=username,
    )

    # 5. Handle post result and update persistence stores
    if result.success:
        dedup.record({
            "date": result.timestamp,
            "hook_category": result.hook_category,
            "hook_text": result.hook_text,
            "category": resolved_category,
            "product": result.product,
            "affiliate_link": result.affiliate_link,
            "num_posts": result.num_posts,
            "status": "posted",
            "post_url": result.post_url,
        })
        db.mark_used(
            affiliate_link,
            note=f"{result.hook_category} ({result.timestamp[:10]})",
        )
        return {
            "status": "posted",
            "product": result.product,
            "affiliate_link": result.affiliate_link,
            "post_url": result.post_url,
            "timestamp": result.timestamp,
        }

    return {
        "status": "failed",
        "product": result.product,
        "affiliate_link": result.affiliate_link,
        "error": result.error,
    }
```

---

### Method B: CLI Subprocess Dispatch (For Asynchronous Cantrik Tasks)

Use this method when Dalang-AI spawns a separate worker process or Cantrik shell command:

```bash
python -m threads_poster.cli post-auto \
  --category skincare \
  --db data/affiliate_links.md \
  --history data/post_history.json \
  --templates templates \
  --cookies ~/.threads_poster/cookies/session.json \
  --hook-style edukasi \
  --posts 3 \
  --headless
```

#### Exit Codes from CLI

| Code | Label | Meaning | Action for Dalang-AI |
|---|---|---|---|
| `0` | Success | Post chain published and verified | Mark task complete, log post URL |
| `1` | Error | Exception, invalid args, or selector failure | Log traceback, do not retry automatically |
| `2` | Dedup Rejection | Link already posted or hook style burst | Try alternative hook style or category |
| `3` | Rate Cap Reached | 5 posts already made today | Pause posting until next calendar day |
| `4` | Cookie Expired | Session invalid on Instagram API | Alert human operator to refresh cookies |
| `5` | Playwright Error | Network timeout or button unclickable | Retry once after 60 seconds |

---

## 4. Hook Copywriting Constraints (Indonesian Market)

All generated hooks adhere to the following standards:

1. **Language Register**: Casual Indonesian Gen-Z (`gw`/`gue` and `lo`, not `aku`/`kamu`).
2. **Hook Sentence Length**: First sentence must be $\le 80$ characters to stay visible before the "more" truncation point in mobile feeds.
3. **Emoji Limit**: Maximum 2 emojis at the end of the first sentence. Never use emojis as bullet points.
4. **Anti-Spam Tone**: Prohibit hard-selling terms (`diskon gila`, `promo termurah`, `beli sekarang juga`). Focus on personal testing, ingredient breakdown, and realistic problem-solving.

Example valid hook (length: 64 characters, 2 emojis):
```text
Kulit lo kering tapi jerawatan terus? Formula ini benerin barrier. 💧🛡️
```

---

## 5. Schema Reference

### Post Chain Schema (Generated by `ContentGenerator`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PostChain",
  "type": "object",
  "required": ["product_name", "affiliate_link", "post_1", "hook_category", "hook_text", "num_posts"],
  "properties": {
    "product_name": {
      "type": "string",
      "description": "Product display name"
    },
    "affiliate_link": {
      "type": "string",
      "format": "uri",
      "pattern": "^https://s\\.shopee\\.co\\.id/.+$",
      "description": "Shopee affiliate short URL"
    },
    "post_1": {
      "type": "string",
      "description": "Hook post text (under 500 characters, first sentence <= 80 characters)"
    },
    "post_2": {
      "type": "string",
      "description": "Review and value elaboration text"
    },
    "post_3": {
      "type": "string",
      "description": "CTA text ending with affiliate URL"
    },
    "hook_category": {
      "type": "string",
      "enum": [
        "edukasi",
        "validasi_mental",
        "storytelling",
        "problem_solving",
        "hook_pancingan",
        "transformasi",
        "social_proof",
        "urgency",
        "controversy"
      ]
    },
    "hook_text": {
      "type": "string",
      "maxLength": 80,
      "description": "Normalized hook prefix used for similarity checks"
    },
    "num_posts": {
      "type": "integer",
      "minimum": 2,
      "maximum": 3
    }
  }
}
```

### Post Result Schema (Returned by `ThreadsPoster.post()`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PostResult",
  "type": "object",
  "required": ["success", "product", "affiliate_link", "timestamp"],
  "properties": {
    "success": {
      "type": "boolean",
      "description": "True if all posts in chain were submitted and verified"
    },
    "product": {
      "type": "string",
      "description": "Product name posted"
    },
    "affiliate_link": {
      "type": "string",
      "description": "Shopee affiliate short URL"
    },
    "hook_category": {
      "type": "string",
      "description": "Hook category used"
    },
    "hook_text": {
      "type": "string",
      "maxLength": 80,
      "description": "First 80 characters of hook"
    },
    "num_posts": {
      "type": "integer",
      "minimum": 1,
      "maximum": 3
    },
    "post_url": {
      "type": "string",
      "description": "Direct URL or profile URL where post was verified"
    },
    "error": {
      "type": "string",
      "description": "Error description if success is false"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of execution"
    }
  }
}
```

---

## 6. Error Handling and Recovery Guide

| Error Case | Root Cause | Recovery Procedure |
|---|---|---|
| `Session invalid: HTTP 401 / 403` | Instagram session expired or revoked | Re-extract cookies via Chrome on operator machine: `python -m threads_poster.cli setup --extract-cookies` |
| `Link already used: ...` | Link marked used in `post_history.json` | Select next unused link via `AffiliateDatabase.next_unused(category)` |
| `Hook style burst: ...` | Style repeated $\ge 2$ times consecutively | Rotate to another style (e.g. switch from `edukasi` to `problem_solving`) |
| `Daily rate limit: >= 5 posts today` | Rate limit threshold reached | Stop scheduling for the current day. Resume after midnight. |
| `Submit button (Post/Kirim) not clickable` | Threads UI changed or modal obscured | Inspect DOM elements or run non-headless mode (`headless=False`) to debug UI state |

---

## 7. Verifying Dalang-AI Integration

Run the integration test suite using pytest to verify that all modules operate as expected:

```bash
/root/storage/projects/dalang-ai/.venv/bin/pytest /root/storage/projects/dalang-ai/workspace/threads-affiliate/tests/
```
