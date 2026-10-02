# API Reference — threads-affiliate

> **Document type:** Reference (Diátaxis)
> **Audience:** Developers and AI agents calling `threads_poster` module functions directly.

---

## Module: `threads_poster`

### Public Exports

```python
from threads_poster import (
    ThreadsPoster,
    ContentGenerator,
    DedupChecker,
    AffiliateDatabase,
)
```

---

## Class: `ContentGenerator`

Generates 2–3 post chains from JSON templates.

### Constructor

```python
ContentGenerator(templates_dir: Path | str = "templates")
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `templates_dir` | `Path \| str` | No | `"templates"` | Directory containing `hooks_{category}.json`, `post2_templates.json`, and `post3_cta_templates.json`. |

---

### Method: `generate_hook`

```python
generate_hook(
    product: str,
    category: str,
    hook_style: str,
) -> tuple[str, str]
```

Generates a single hook post text.

**Parameters:**

| Parameter | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `product` | `str` | Yes | Non-empty | Product name substituted into `{product}` placeholder. |
| `category` | `str` | Yes | One of: `skincare`, `parfum`, `haircare`, `makeup` | Selects the hook template file. |
| `hook_style` | `str` | Yes | One of 9 canonical styles (see below) | Selects the hook style within the template. |

**Returns:** `tuple[str, str]` — `(hook_text, hook_style_used)`

**Raises:**
- `FileNotFoundError` — Template file `templates/hooks_{category}.json` does not exist.
- `KeyError` — `hook_style` not found in the template file.

**Example:**

```python
from threads_poster import ContentGenerator

gen = ContentGenerator(templates_dir="templates")
hook_text, style = gen.generate_hook(
    product="SKINTIFIC 5X Ceramide",
    category="skincare",
    hook_style="edukasi",
)
print(hook_text)
# Output: "Ceramide itu bukan sekadar hype. SKINTIFIC 5X Ceramide..."
print(style)
# Output: "edukasi"
```

---

### Method: `generate_chain`

```python
generate_chain(
    product: str,
    affiliate_link: str,
    category: str,
    hook_style: str,
    num_posts: int = 3,
) -> dict
```

Generates a complete 2–3 post chain.

**Parameters:**

| Parameter | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `product` | `str` | Yes | Non-empty | Product name. |
| `affiliate_link` | `str` | Yes | Must match `^https://s\.shopee\.co\.id/.+$` | Shopee affiliate short URL. |
| `category` | `str` | Yes | `skincare`, `parfum`, `haircare`, `makeup` | Product category. |
| `hook_style` | `str` | Yes | One of 9 canonical styles | Hook style for post 1. |
| `num_posts` | `int` | No | `2` or `3` | Number of posts in the chain. |

**Returns:** `dict` with the following keys:

| Key | Type | Description |
|---|---|---|
| `product_name` | `str` | Product name as provided. |
| `affiliate_link` | `str` | Affiliate URL as provided. |
| `post_1` | `str` | Hook post text. |
| `post_2` | `str` | Body / review post text. |
| `post_3` | `str` | CTA post text with affiliate link appended. Present only when `num_posts=3`. |
| `hook_category` | `str` | Hook style used. |
| `hook_text` | `str` | First 80 characters of `post_1` (used for dedup). |
| `num_posts` | `int` | Number of posts generated. |

**Raises:**
- `FileNotFoundError` — Missing template file.
- `ValueError` — `num_posts` is not 2 or 3.

**Example:**

```python
from threads_poster import ContentGenerator

gen = ContentGenerator(templates_dir="templates")
chain = gen.generate_chain(
    product="Azarine Hydrasoothe SPF 45",
    affiliate_link="https://s.shopee.co.id/ABCDE",
    category="skincare",
    hook_style="problem_solving",
    num_posts=3,
)

print(chain["post_1"])   # Hook text
print(chain["post_2"])   # Review body
print(chain["post_3"])   # CTA with link
print(chain["hook_text"])  # First 80 chars of post_1
```

---

## Class: `DedupChecker`

Reads and writes `post_history.json` to prevent duplicate posts.

### Constructor

```python
DedupChecker(history_path: Path | str)
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `history_path` | `Path \| str` | Yes | Path to `post_history.json`. Created automatically if it does not exist. |

---

### Method: `check`

```python
check(
    affiliate_link: str,
    hook_category: str,
    hook_text: str,
    category: str = "",
) -> tuple[bool, str]
```

Checks whether a proposed post passes dedup rules.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `affiliate_link` | `str` | Yes | Shopee affiliate URL to check. |
| `hook_category` | `str` | Yes | Hook style to check for burst. |
| `hook_text` | `str` | Yes | First 80 characters of hook (for similarity check). |
| `category` | `str` | No | Product category (informational, not used in dedup logic). |

**Returns:** `tuple[bool, str]` — `(passed, reason)`

- `passed=True` — Post is safe to proceed.
- `passed=False` — `reason` contains a human-readable rejection message.

**Rejection reasons:**

| Condition | Reason string |
|---|---|
| `affiliate_link` already in history | `"Link already used: {affiliate_link}"` |
| `hook_category` used in last 2 consecutive posts | `"Hook style burst: '{hook_category}' used in last 2 posts"` |

**Example:**

```python
from threads_poster import DedupChecker

dedup = DedupChecker("data/post_history.json")
ok, reason = dedup.check(
    affiliate_link="https://s.shopee.co.id/ABCDE",
    hook_category="edukasi",
    hook_text="Ceramide itu bukan sekadar hype.",
)
if not ok:
    print(f"Rejected: {reason}")
```

---

### Method: `record`

```python
record(entry: dict) -> None
```

Appends a post record to `post_history.json`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `entry` | `dict` | Yes | Post record conforming to `post-history.schema.json`. |

**Required keys in `entry`:**

| Key | Type | Constraints | Description |
|---|---|---|---|
| `date` | `str` | ISO 8601 datetime | Timestamp of the post. |
| `hook_category` | `str` | One of 9 canonical styles | Hook style used. |
| `hook_text` | `str` | Max 80 characters | First 80 chars of hook. |
| `affiliate_link` | `str` | Shopee URL pattern | Affiliate link posted. |

**Optional keys in `entry`:**

| Key | Type | Description |
|---|---|---|
| `category` | `str` | Product category. |
| `product` | `str` | Product name. |
| `num_posts` | `int` | Number of posts in chain. |
| `status` | `str` | `posted`, `failed`, `rejected_dedup`, `rejected_cookies`. |
| `post_url` | `str` | URL to the published post. |

**Example:**

```python
dedup.record({
    "date": "2026-10-02T09:00:00",
    "hook_category": "edukasi",
    "hook_text": "Ceramide itu bukan sekadar hype.",
    "affiliate_link": "https://s.shopee.co.id/ABCDE",
    "category": "skincare",
    "product": "SKINTIFIC 5X Ceramide",
    "num_posts": 3,
    "status": "posted",
    "post_url": "https://www.threads.com/@yourusername",
})
```

---

## Class: `AffiliateDatabase`

Reads and writes the Markdown affiliate link database.

### Constructor

```python
AffiliateDatabase(db_path: Path | str)
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `db_path` | `Path \| str` | Yes | Path to `affiliate_links.md`. |

---

### Method: `next_unused`

```python
next_unused(category: str) -> tuple[str, str, str]
```

Returns the first unused affiliate link for the given category.

**Parameters:**

| Parameter | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `category` | `str` | Yes | `skincare`, `parfum`, `haircare`, `makeup` | Product category to search. |

**Returns:** `tuple[str, str, str]` — `(affiliate_link, product_name, category)`

**Raises:**
- `StopIteration` — No unused links remain for the given category.

**Example:**

```python
from threads_poster import AffiliateDatabase

db = AffiliateDatabase("data/affiliate_links.md")
link, product, category = db.next_unused("skincare")
print(link)     # "https://s.shopee.co.id/ABCDE"
print(product)  # "SKINTIFIC 5X Ceramide"
```

---

### Method: `mark_used`

```python
mark_used(affiliate_link: str, note: str = "") -> None
```

Updates the Markdown database row for the given link from `❌ UNUSED` to `✅ USED (date)`.

**Parameters:**

| Parameter | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `affiliate_link` | `str` | Yes | Must exist in database | Shopee affiliate URL to mark. |
| `note` | `str` | No | Max 100 characters | Optional note appended to the status cell (e.g. hook style and date). |

**Raises:**
- `ValueError` — `affiliate_link` not found in the database.

**Example:**

```python
db.mark_used(
    "https://s.shopee.co.id/ABCDE",
    note="edukasi (2026-10-02)",
)
```

---

## Class: `ThreadsPoster`

Drives Playwright/Chromium to post content to Threads.

### Constructor

```python
ThreadsPoster(
    cookies_path: Path | str = "~/.threads_poster/cookies/session.json",
    headless: bool = True,
    timeout_ms: int = 30000,
)
```

| Parameter | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| `cookies_path` | `Path \| str` | No | `~/.threads_poster/cookies/session.json` | File must exist with permissions `600` | Path to session cookie JSON file. |
| `headless` | `bool` | No | `True` | — | Run Chromium without a visible window. Set to `False` for debugging. |
| `timeout_ms` | `int` | No | `30000` | Min: `5000`, Max: `120000` | Playwright navigation timeout in milliseconds. |

---

### Method: `post`

```python
post(
    product: str,
    affiliate_link: str,
    hook_text: str,
    post_2: str | None = None,
    post_3: str | None = None,
    hook_category: str = "",
    category: str = "",
    image_path: str | None = None,
    username: str = "",
) -> PostResult
```

Submits a 2–3 post chain to Threads.

**Parameters:**

| Parameter | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `product` | `str` | Yes | Non-empty | Product name (used for verification). |
| `affiliate_link` | `str` | Yes | Shopee URL pattern | Affiliate URL included in post 3. |
| `hook_text` | `str` | Yes | Max 500 characters | Text for post 1 (the hook). |
| `post_2` | `str \| None` | No | Max 500 characters | Text for post 2 (review body). |
| `post_3` | `str \| None` | No | Max 500 characters | Text for post 3 (CTA). Affiliate link is appended automatically. |
| `hook_category` | `str` | No | One of 9 canonical styles | Hook style (stored in result for dedup recording). |
| `category` | `str` | No | Product category | Product category (stored in result). |
| `image_path` | `str \| None` | No | Valid file path, JPEG or PNG | Optional product image attached to post 1. |
| `username` | `str` | No | Threads handle with or without `@` | Used to navigate to profile for post verification. |

**Returns:** `PostResult` dataclass with the following attributes:

| Attribute | Type | Description |
|---|---|---|
| `success` | `bool` | `True` if all posts submitted and verified. |
| `product` | `str` | Product name. |
| `affiliate_link` | `str` | Affiliate URL. |
| `hook_category` | `str` | Hook style used. |
| `hook_text` | `str` | First 80 characters of hook. |
| `num_posts` | `int` | Number of posts submitted. |
| `post_url` | `str` | Profile URL or direct post URL (empty if verification failed). |
| `error` | `str` | Error description if `success=False`. |
| `timestamp` | `str` | ISO 8601 timestamp of execution. |

**Raises:**
- `FileNotFoundError` — Cookie file does not exist.
- `PermissionError` — Cookie file permissions are not `600`.

**Example:**

```python
from threads_poster import ThreadsPoster

poster = ThreadsPoster(
    cookies_path="~/.threads_poster/cookies/session.json",
    headless=True,
)
result = poster.post(
    product="SKINTIFIC 5X Ceramide",
    affiliate_link="https://s.shopee.co.id/ABCDE",
    hook_text="Ceramide itu bukan sekadar hype. Ini yang bikin kulit gw recover.",
    post_2="Gw udah 3 minggu pakai SKINTIFIC 5X Ceramide. Barrier kulit gw yang tadinya rusak...",
    post_3="Yang mau coba, link di bawah ya.",
    hook_category="edukasi",
    category="skincare",
    username="@yourusername",
)

if result.success:
    print(f"Posted: {result.post_url}")
else:
    print(f"Failed: {result.error}")
```

---

## Module: `threads_poster.cookie_manager`

### Function: `validate_cookies`

```python
validate_cookies(cookies_path: Path | str) -> tuple[bool, dict]
```

Tests whether the session cookies grant authenticated access to Instagram.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `cookies_path` | `Path \| str` | Yes | Path to `session.json`. |

**Returns:** `tuple[bool, dict]` — `(is_valid, details)`

- `is_valid=True`: `details` contains `session_user_id` and `verified_via`.
- `is_valid=False`: `details` contains `error` string.

**Example:**

```python
from threads_poster.cookie_manager import validate_cookies

is_valid, details = validate_cookies("~/.threads_poster/cookies/session.json")
if not is_valid:
    raise RuntimeError(f"Cookies expired: {details['error']}")
print(f"Authenticated as user ID: {details['session_user_id']}")
```

---

## CLI Reference

### Entry Point

```bash
python -m threads_poster.cli [subcommand] [options]
```

### Subcommand: `setup`

Manage cookies and session validation.

```bash
python -m threads_poster.cli setup [options]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--extract-cookies` | flag | — | Extract cookies from Chrome profile. |
| `--validate-cookies` | flag | — | Validate existing cookie file. |
| `--list-chrome-profiles` | flag | — | List available Chrome profiles. |
| `--chrome-profile` | `str` | `"Default"` | Chrome profile name to extract from. |
| `--output` | `str` | `~/.threads_poster/cookies/session.json` | Output path for extracted cookies. |
| `--cookies` | `str` | `~/.threads_poster/cookies/session.json` | Cookie file to validate. |

---

### Subcommand: `post`

Post a specific product with explicit parameters.

```bash
python -m threads_poster.cli post [options]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--product` | `str` | Yes | — | Product name. |
| `--link` | `str` | Yes | — | Shopee affiliate URL. |
| `--category` | `str` | Yes | — | Product category. |
| `--hook-style` | `str` | No | `"edukasi"` | Hook style. |
| `--posts` | `int` | No | `3` | Number of posts (2 or 3). |
| `--cookies` | `str` | No | `~/.threads_poster/cookies/session.json` | Cookie file path. |
| `--templates` | `str` | No | `"templates"` | Templates directory. |
| `--history` | `str` | No | `"data/post_history.json"` | History file path. |
| `--image` | `str` | No | — | Product image path. |
| `--username` | `str` | No | — | Threads handle for verification. |
| `--headless` | flag | No | — | Run browser headless. |

---

### Subcommand: `post-auto`

Auto-select the next unused link from the database and post.

```bash
python -m threads_poster.cli post-auto [options]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--category` | `str` | Yes | — | Product category. |
| `--db` | `str` | No | `"data/affiliate_links.md"` | Affiliate link database path. |
| `--hook-style` | `str` | No | `"edukasi"` | Hook style. |
| `--posts` | `int` | No | `3` | Number of posts (2 or 3). |
| `--cookies` | `str` | No | `~/.threads_poster/cookies/session.json` | Cookie file path. |
| `--templates` | `str` | No | `"templates"` | Templates directory. |
| `--history` | `str` | No | `"data/post_history.json"` | History file path. |
| `--username` | `str` | No | — | Threads handle for verification. |
| `--headless` | flag | No | — | Run browser headless. |

---

### Subcommand: `batch`

Run multiple posts in sequence with configurable delay.

```bash
python -m threads_poster.cli batch [options]
```

| Option | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| `--count` | `int` | No | `1` | Max: `5` | Number of posts to run. |
| `--delay` | `int` | No | `300` | Min: `60` (seconds) | Delay between posts in seconds. |
| `--categories` | `str` | No | All 4 categories | Comma-separated list | Categories to rotate through. |
| `--db` | `str` | No | `"data/affiliate_links.md"` | — | Affiliate link database path. |
| `--cookies` | `str` | No | `~/.threads_poster/cookies/session.json` | — | Cookie file path. |
| `--headless` | flag | No | — | — | Run browser headless. |

---

## Hook Style Reference

| Style | Description | Typical first sentence pattern |
|---|---|---|
| `edukasi` | Educational fact about ingredient or product | "Ceramide itu bukan sekadar hype." |
| `validasi_mental` | Emotional validation of a common skin concern | "Gw ngerti banget rasanya punya kulit sensitif." |
| `storytelling` | Personal experience narrative | "3 bulan lalu kulit gw lagi di titik paling parah." |
| `problem_solving` | Problem → solution framing | "Kulit lo kering tapi jerawatan terus?" |
| `hook_pancingan` | Curiosity trigger / open loop | "Ada satu bahan yang gw skip selama 2 tahun." |
| `transformasi` | Before/after transformation | "Sebelum: kulit kusam, pori keliatan. Sesudah: beda banget." |
| `social_proof` | Popularity or trending signal | "Ini produk yang lagi dipakai 4 dari 5 orang di FYP gw." |
| `urgency` | Scarcity or time pressure | "Stok ini biasanya habis dalam 3 hari." |
| `controversy` | Contrarian hot-take | "Gw berhenti pakai toner mahal. Ini alasannya." |

---

## Supported Categories

| Category | Template file | Description |
|---|---|---|
| `skincare` | `hooks_skincare.json` | Moisturizers, serums, sunscreen, toners |
| `parfum` | `hooks_parfum.json` | Fragrances and body mists |
| `haircare` | `hooks_haircare.json` | Shampoo, conditioner, hair treatments |
| `makeup` | `hooks_makeup.json` | Foundation, lipstick, eyeshadow, blush |

---

## Hard Constraints

| Constraint | Limit | Enforcement |
|---|---|---|
| Posts per day per account | Max 5 | CLI `batch` subcommand exits with code `3` |
| Affiliate link reuse | Never | `DedupChecker.check()` rejects with code `2` |
| Same hook style consecutive | Max 1 | `DedupChecker.check()` rejects burst |
| Cookie file permissions | `600` | `ThreadsPoster` raises `PermissionError` |
| Auto-follow / auto-DM | Prohibited | Not implemented; violates Threads ToS |
| Scraping other users | Prohibited | Not implemented; violates Threads ToS |
