# Gathot Social Media Engineering Standards

**Document Type:** Reference + Explanation  
**Audience:** Social Media Specialists, Affiliate Content Creators, Copywriters, Automation Engineers  
**Standard Compliance:** Diátaxis Framework · Google Developer Documentation Style Guide · Meta Content Guidelines · Anti-AI-Slop Directives · mika_docs_standards.md  
**Version:** 1.0.0  
**Last Updated:** 2026-10-02

---

## Definition Block

> **Gathot** is the social media automation and content operations agent within the Dalang-AI studio. This document defines the engineering standards that govern every piece of content Gathot produces, schedules, or publishes — from hook psychology to ethical curation, keyword research, and posting management.

---

## Table of Contents

1. [Scope and Applicability](#1-scope-and-applicability)
2. [Copywriting SOP: Viral Content](#2-copywriting-sop-viral-content)
3. [Hook Psychology Framework](#3-hook-psychology-framework)
4. [Ethical Curation: No False Claims](#4-ethical-curation-no-false-claims)
5. [Social SEO and Keyword Research](#5-social-seo-and-keyword-research)
6. [Posting Management and Scheduling](#6-posting-management-and-scheduling)
7. [Platform-Specific Rules](#7-platform-specific-rules)
8. [Quality Gate Checklist](#8-quality-gate-checklist)
9. [Prohibited Patterns Reference](#9-prohibited-patterns-reference)
10. [Glossary](#10-glossary)

---

## 1. Scope and Applicability

This standard applies to **all content** produced by or under the supervision of the Gathot agent, including:

- Affiliate product posts (Threads, Facebook, Instagram, TikTok)
- Organic brand awareness content
- Automated caption generation pipelines
- Keyword research outputs fed into content briefs
- Scheduling configurations and posting queues

Any agent, human operator, or automated pipeline that generates social media content for Bos Muda's studio **must comply** with every section of this document.

---

## 2. Copywriting SOP: Viral Content

### 2.1 Content Classification

Before writing any post, classify it into one of four content types:

| Type | Purpose | Engagement Goal |
|---|---|---|
| **Problem-Solution** | Identifies a pain point the audience has; presents the product as the answer | Comments, saves |
| **Social Proof Relay** | Relays verifiable third-party reviews or product specifications | Shares, link clicks |
| **Educational** | Teaches a technique, tip, or fact related to the product category | Saves, follows |
| **Narrative** | Tells a short story or scenario the audience recognizes | Comments, shares |

### 2.2 Post Structure

Every post follows this exact structure:

```
[HOOK]          ← Line 1. Max 80 characters. Max 2 emojis at end.
[BODY]          ← Lines 2–N. Problem → context → product detail → benefit.
[CTA]           ← Final line. One clear action. No hard-sell language.
[HASHTAGS]      ← Separate block. 3–10 tags. Platform-specific rules apply.
```

### 2.3 Hook Writing Rules

1. **Character limit:** The hook (line 1) must be ≤ 80 characters including spaces and emojis.
2. **Emoji count:** Maximum 2 emojis. Place them at the **end** of the hook sentence, never mid-sentence.
3. **Register:** Indonesian Gen-Z casual. Use `gw`/`gue` and `lo`. Never use `aku`/`kamu`.
4. **Verb-first or question-first:** Start with an action verb or a direct question. Never start with "Halo" or "Hai teman-teman".
5. **No brand name in hook:** The hook must create curiosity before revealing the product.

**Compliant hook examples:**

```
Bibir gw pecah-pecah parah sampai nemu ini. 🫦
```
```
Lo pernah nggak pakai lipstik tapi malah bikin bibir makin kering?
```
```
Ternyata lipstik Rp 20 ribuan bisa transferproof seharian. 👀
```

**Non-compliant hook examples (do not use):**

```
❌ Halo teman-teman! Kali ini gw mau review produk keren banget!
   → Reason: Starts with "Halo", uses "keren banget" (vague), no tension.

❌ 🚀 OMG Matte Kiss Lip Cream yang amazing dan seamless banget!
   → Reason: Emoji at start, "amazing", "seamless" are prohibited AI-fluff words.

❌ Elevate your lip game dengan produk next-gen ini!
   → Reason: "Elevate", "next-gen" are prohibited. English in Indonesian-register post.
```

### 2.4 Body Writing Rules

1. **Plain sentences:** Subject + Predicate + Object. No nested clauses that loop back on themselves.
2. **Fact-first:** Every claim must be traceable to a product specification, BPOM data, or a verifiable source. See [Section 4](#4-ethical-curation-no-false-claims).
3. **Cut ruthlessly:** Every line that does not add a new technical fact or narrative beat gets deleted.
4. **Paragraph length:** Maximum 3 lines per paragraph on mobile. Use line breaks generously.
5. **No emoji bullets:** Use `-` or numbered lists. Never `🚀 Feature 1`, `⚡ Feature 2`.

**Compliant body example:**

```
Gw udah coba banyak lip cream matte di bawah Rp 25 ribu, dan kebanyakan
bikin bibir gw makin kering setelah 3 jam.

Yang ini beda. Formulanya ada Jojoba Oil sama Vitamin E — dua bahan yang
emang dikenal bantu jaga kelembapan. Jadi matte-nya nggak bikin bibir
terasa ketarik.

Udah BPOM dan halal MUI juga, jadi gw nggak perlu khawatir soal keamanannya.
```

### 2.5 CTA (Call-to-Action) Rules

1. **One CTA per post.** Never stack two actions ("Like dan share dan komen dan klik link").
2. **Soft CTA only.** No hard-sell language. See prohibited words in [Section 9](#9-prohibited-patterns-reference).
3. **CTA must match the platform's primary conversion action:**

| Platform | Primary CTA |
|---|---|
| Threads | "Link di bio kalau lo mau cek." |
| Facebook | "Cek di kolom komentar, gw taruh linknya." |
| Instagram | "Link di bio." |
| TikTok | "Cek profil gw buat linknya." |

4. **Never fabricate urgency.** Do not write "Stok terbatas!" unless you have real-time inventory data confirming scarcity.

---

## 3. Hook Psychology Framework

### 3.1 The Six Psychological Triggers

Gathot uses six evidence-based psychological triggers. Each post must activate **at least one**. Document which trigger you use in the content brief.

| Trigger | Mechanism | Example Application |
|---|---|---|
| **Curiosity Gap** | Opens an information gap the reader must close | "Ternyata lipstik Rp 20 ribuan bisa transferproof seharian." |
| **Pain Identification** | Names a specific, relatable frustration | "Bibir gw pecah-pecah parah sampai nemu ini." |
| **Social Proof Signal** | References verifiable external validation | "Udah BPOM dan halal MUI." |
| **Specificity** | Uses precise numbers instead of vague superlatives | "Tahan 6 jam tanpa touch-up" (only if spec-verified) |
| **Contrast** | Before vs. after, cheap vs. effective | "Harga Rp 20 ribu, tapi hasilnya nggak murahan." |
| **Relatability** | Mirrors the audience's exact lived experience | "Lo pernah nggak pakai lipstik tapi malah bikin bibir makin kering?" |

### 3.2 Trigger Selection by Content Type

| Content Type | Primary Trigger | Secondary Trigger |
|---|---|---|
| Problem-Solution | Pain Identification | Contrast |
| Social Proof Relay | Social Proof Signal | Specificity |
| Educational | Curiosity Gap | Specificity |
| Narrative | Relatability | Pain Identification |

### 3.3 Trigger Validation Test

Before publishing, run this internal check:

```
Q1: Can I point to the exact word/phrase in line 1 that activates the trigger?
Q2: Would a 22-year-old Indonesian woman stop scrolling at this line?
Q3: Does the hook create a question in the reader's mind that the body answers?
```

If any answer is "No", rewrite the hook.

### 3.4 Prohibited Psychological Manipulation

The following tactics are **banned** regardless of conversion potential:

- **False scarcity:** "Stok tinggal 3!" without verified inventory data.
- **False urgency:** "Promo berakhir hari ini!" without a real deadline.
- **Fear-mongering:** Implying harm from NOT using the product.
- **Fake testimonials:** Writing first-person reviews for products not personally used. Use third-person relay format instead (see [Section 4.3](#43-relay-format-for-unverified-personal-experience)).

---

## 4. Ethical Curation: No False Claims

### 4.1 The Claim Verification Hierarchy

Every factual claim in a post must be sourced from one of these tiers, in order of preference:

| Tier | Source | Example |
|---|---|---|
| **T1 — Official** | BPOM database, brand official site, product packaging | "Mengandung Jojoba Oil (Simmondsia Chinensis Seed Oil)" |
| **T2 — Verifiable Third-Party** | Peer-reviewed ingredient studies, certified lab results | "Jojoba Oil dikenal sebagai emollient yang membantu retensi kelembapan kulit" |
| **T3 — Aggregated User Signal** | Publicly visible review aggregates (e.g., Shopee rating with review count) | "Rating 4.8 dari 2.300+ ulasan di Shopee" (screenshot required) |
| **T4 — Personal Experience** | Only if the operator has personally used the product | Must use first-person and disclose affiliate status |

**Claims without a T1–T4 source are prohibited.**

### 4.2 Prohibited Claim Patterns

| Pattern | Example | Why Prohibited |
|---|---|---|
| Fabricated statistics | "99% pengguna puas" | No data source |
| Superlative without basis | "Lipstik terbaik di Indonesia" | Unverifiable |
| Medical claim | "Menyembuhkan bibir pecah-pecah" | Requires clinical evidence; violates BPOM advertising rules |
| Competitor disparagement | "Lebih bagus dari merek X" | Legal risk; unverifiable |
| Fake social proof | "Viral di TikTok!" without a verifiable viral metric | Misleading |

### 4.3 Relay Format for Unverified Personal Experience

When the operator has **not** personally used the product, use the relay format:

```
Format: "Banyak yang bilang [claim]. Berdasarkan formulanya yang mengandung
[ingredient], ini masuk akal karena [mechanism]."
```

**Example:**

```
Banyak yang bilang lip cream ini tahan seharian. Berdasarkan formulanya
yang mengandung Jojoba Oil dan Vitamin E, ini masuk akal — dua bahan itu
emang dikenal bantu jaga kelembapan dan bikin formula nggak cepat pudar.
```

### 4.4 Affiliate Disclosure Requirement

Every post that contains an affiliate link **must** include a disclosure. Place it at the end of the post, before hashtags.

**Compliant disclosure formats:**

```
#ad
```
```
*Konten ini mengandung tautan afiliasi.
```
```
[Afiliasi] Gw dapat komisi kalau lo beli lewat link ini.
```

**Non-compliant:** Hiding the disclosure inside a wall of hashtags or omitting it entirely.

---

## 5. Social SEO and Keyword Research

### 5.1 Keyword Research Methodology

Gathot uses a four-step keyword research process for every product category:

**Step 1 — Seed Keyword Extraction**

Extract seed keywords from:
- Product name and category
- BPOM-registered ingredient names
- Common pain points in the product category

```
Product: OMG Matte Kiss Lip Cream
Seeds: ["lip cream matte", "lipstik tahan lama", "lipstik murah bagus",
        "lip cream BPOM", "lipstik nggak bikin kering", "ombre lips tutorial"]
```

**Step 2 — Platform-Native Search Validation**

Validate seeds by searching them natively on each target platform and recording:
- Autocomplete suggestions (indicates search volume)
- Top post engagement (likes + comments on top 5 results)
- Hashtag post count (for Instagram/TikTok)

```
Validation log format (JSON):
{
  "keyword": "lip cream matte",
  "platform": "threads",
  "autocomplete_rank": 1,
  "top_post_likes": 1240,
  "top_post_comments": 87,
  "validated_at": "2026-10-02T09:00:00Z"
}
```

**Step 3 — Keyword Tiering**

Tier validated keywords by competition and relevance:

| Tier | Criteria | Strategy |
|---|---|---|
| **Primary** | High relevance, moderate competition | Use in hook and first 2 body lines |
| **Secondary** | High relevance, high competition | Use in body and hashtags |
| **Long-tail** | Specific, low competition | Use in hashtags and CTA area |

**Step 4 — Keyword Integration Rules**

- Integrate keywords **naturally**. Never keyword-stuff.
- Primary keyword appears in the hook or first body line.
- Do not repeat the same keyword more than twice in one post.
- Hashtags are a separate keyword layer — do not duplicate body keywords verbatim in hashtags if the body already contains them.

### 5.2 Hashtag Strategy

#### 5.2.1 Hashtag Count by Platform

| Platform | Minimum | Maximum | Optimal |
|---|---|---|---|
| Threads | 0 | 5 | 3 |
| Facebook | 0 | 3 | 2 |
| Instagram | 5 | 30 | 15–20 |
| TikTok | 3 | 10 | 5–7 |

#### 5.2.2 Hashtag Composition Formula

For every post, use this composition:

```
1 × Brand/Product hashtag    (e.g., #OMGMatteLipCream)
1 × Category hashtag         (e.g., #LipCreamMatte)
1 × Pain-point hashtag       (e.g., #LipstikTahanLama)
1 × Trend/Discovery hashtag  (e.g., #RecomendasiLipstik)
N × Long-tail hashtags       (e.g., #LipstikMurahBagus, #LipCreamBPOM)
```

#### 5.2.3 Hashtag Validation Rules

- Never use a hashtag with zero posts on the platform.
- Never use a hashtag that has been flagged or shadowbanned on the target platform.
- Validate hashtag health monthly. Remove any hashtag that drops below 100 posts.

### 5.3 Keyword Research Output Format

Every keyword research session produces a structured brief:

```json
{
  "product": "OMG Matte Kiss Lip Cream",
  "campaign_date": "2026-10-02",
  "platform": "threads",
  "primary_keywords": [
    "lip cream matte",
    "lipstik nggak bikin kering"
  ],
  "secondary_keywords": [
    "lipstik tahan lama",
    "lipstik murah bagus"
  ],
  "long_tail_keywords": [
    "lip cream BPOM halal murah",
    "lipstik matte untuk bibir gelap"
  ],
  "hashtags": [
    "#OMGMatteLipCream",
    "#LipCreamMatte",
    "#LipstikTahanLama",
    "#RecomendasiLipstik",
    "#LipstikMurahBagus"
  ],
  "validated_by": "gathot",
  "validation_method": "platform_native_search"
}
```

---

## 6. Posting Management and Scheduling

### 6.1 Optimal Posting Windows

Post during these windows for maximum organic reach. Times are in WIB (UTC+7).

| Platform | Primary Window | Secondary Window | Avoid |
|---|---|---|---|
| Threads | 07:00–09:00 | 19:00–21:00 | 13:00–15:00 |
| Facebook | 08:00–10:00 | 20:00–22:00 | 14:00–16:00 |
| Instagram | 07:00–09:00 | 18:00–20:00 | 12:00–14:00 |
| TikTok | 06:00–08:00 | 19:00–22:00 | 10:00–14:00 |

> **Note:** These windows are derived from general Indonesian social media usage patterns. Validate against your own account analytics after 30 days of posting and adjust accordingly.

### 6.2 Posting Frequency Limits

Exceeding these limits triggers platform spam filters:

| Platform | Max Posts/Day | Max Posts/Week | Min Gap Between Posts |
|---|---|---|---|
| Threads | 5 | 20 | 2 hours |
| Facebook (Page) | 3 | 15 | 3 hours |
| Instagram | 2 | 10 | 6 hours |
| TikTok | 3 | 15 | 4 hours |

### 6.3 Content Calendar Structure

Maintain a weekly content calendar with this schema:

```json
{
  "week_start": "2026-10-06",
  "posts": [
    {
      "id": "POST-001",
      "platform": "threads",
      "content_type": "problem_solution",
      "product": "OMG Matte Kiss Lip Cream",
      "primary_trigger": "pain_identification",
      "scheduled_at": "2026-10-06T07:30:00+07:00",
      "status": "draft",
      "keyword_brief_ref": "brief_omg_lipcream_oct06.json",
      "affiliate_link": "https://shopee.co.id/...",
      "disclosure_included": true,
      "reviewed_by": null,
      "published_at": null
    }
  ]
}
```

### 6.4 Post Lifecycle States

Every post moves through these states in order:

```
DRAFT → REVIEW → APPROVED → SCHEDULED → PUBLISHED → ARCHIVED
                     ↓
                  REJECTED → DRAFT (revision cycle)
```

| State | Definition | Who Acts |
|---|---|---|
| `DRAFT` | Content written, not yet reviewed | Gathot / Copywriter |
| `REVIEW` | Submitted for quality gate check | Gathot → Bos Muda |
| `APPROVED` | Passed all quality gate checks | Bos Muda |
| `REJECTED` | Failed quality gate; returned with notes | Bos Muda → Gathot |
| `SCHEDULED` | Queued in posting tool at target time | Automation pipeline |
| `PUBLISHED` | Live on platform | Platform |
| `ARCHIVED` | Engagement data recorded; post retired from active tracking | Gathot |

### 6.5 Engagement Monitoring Protocol

After every post reaches `PUBLISHED` state, monitor at these intervals:

| Interval | Metrics to Record |
|---|---|
| 1 hour | Impressions, likes, comments, shares |
| 6 hours | All above + profile visits, link clicks |
| 24 hours | All above + saves, follows attributed |
| 7 days | Final engagement rate calculation |

**Engagement Rate Formula:**

```
Engagement Rate = (Likes + Comments + Shares + Saves) / Impressions × 100
```

A post with ER < 1% on Threads or Facebook triggers a content review. Identify which quality gate the post failed and update the content brief.

### 6.6 Automation Script Requirements

Any automation script that publishes posts must:

1. Read the post from the content calendar JSON (see [Section 6.3](#63-content-calendar-structure)).
2. Verify `status == "APPROVED"` before publishing. Abort if status is any other value.
3. Verify `disclosure_included == true` for all affiliate posts. Abort if false.
4. Log the publish attempt with timestamp and platform response code.
5. Update `published_at` and `status` to `PUBLISHED` on success.
6. On failure, set `status` back to `SCHEDULED` and log the error with full traceback.

**Example publish guard (Python):**

```python
import json
from datetime import datetime, timezone

def publish_post(post: dict, platform_client) -> dict:
    """
    Publishes a single post after validating its state and compliance fields.

    Args:
        post: Post dict conforming to content calendar schema (Section 6.3).
        platform_client: Authenticated platform API client instance.

    Returns:
        Updated post dict with published_at and status set.

    Raises:
        ValueError: If post status is not APPROVED or disclosure is missing.
        RuntimeError: If the platform API returns a non-2xx response.
    """
    if post.get("status") != "APPROVED":
        raise ValueError(
            f"Post {post['id']} has status '{post.get('status')}'. "
            "Only APPROVED posts can be published."
        )

    if post.get("affiliate_link") and not post.get("disclosure_included"):
        raise ValueError(
            f"Post {post['id']} contains an affiliate link but "
            "'disclosure_included' is False. Add disclosure before publishing."
        )

    response = platform_client.publish(
        text=post["body"],
        scheduled_at=post["scheduled_at"],
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Platform API error for post {post['id']}: "
            f"HTTP {response.status_code} — {response.text}"
        )

    post["status"] = "PUBLISHED"
    post["published_at"] = datetime.now(timezone.utc).isoformat()
    return post
```

---

## 7. Platform-Specific Rules

### 7.1 Threads

- **Character limit:** 500 characters per post.
- **Link behavior:** Links in post body are not clickable. Direct users to bio link.
- **Image:** Single image or carousel (up to 10 images). Always include alt text.
- **Hashtag placement:** Place hashtags at the end of the post, separated by a blank line.
- **Thread chains:** For long-form content, use a thread chain. First post = hook only. Second post = body. Third post = CTA + hashtags.

### 7.2 Facebook

- **Character limit:** 63,206 characters (use max 300 for feed posts; longer posts get truncated in feed).
- **Link behavior:** Links in post body are clickable. Place affiliate link in the first comment to avoid reach penalty from Facebook's algorithm.
- **Image:** Single image or album. Recommended ratio: 1:1 (1080×1080px) or 4:5 (1080×1350px).
- **Hashtag placement:** 2–3 hashtags maximum. Place inline or at end.
- **Boosting:** Never boost a post that contains an affiliate link without Meta's explicit affiliate disclosure compliance review.

### 7.3 Instagram

- **Character limit:** 2,200 characters. First 125 characters appear before "more" — treat as hook.
- **Link behavior:** No clickable links in captions. Use bio link or Link Sticker in Stories.
- **Image:** Minimum 1080px on shortest side. Ratio: 1:1, 4:5, or 1.91:1.
- **Alt text:** Always set custom alt text on every image for accessibility and SEO.
- **Hashtag placement:** Place hashtags in the first comment, not the caption, to keep caption clean.

### 7.4 TikTok

- **Character limit:** 2,200 characters for caption.
- **Hook:** The first 3 seconds of video must mirror the text hook. Caption hook reinforces video hook.
- **Link behavior:** Link in bio only (unless TikTok Shop is active).
- **Hashtag placement:** 5–7 hashtags inline in caption.
- **Duet/Stitch:** If using Duet or Stitch of another creator's content, always credit the original creator explicitly in the caption.

---

## 8. Quality Gate Checklist

Run this checklist on every post before changing status from `DRAFT` to `REVIEW`.

### 8.1 Hook Gate

- [ ] Hook is ≤ 80 characters (count including spaces and emojis).
- [ ] Hook contains ≤ 2 emojis, placed at the end.
- [ ] Hook uses Gen-Z Indonesian register (`gw`/`lo`).
- [ ] Hook does not start with "Halo", "Hai", or any greeting.
- [ ] Hook activates at least one psychological trigger from [Section 3.1](#31-the-six-psychological-triggers).
- [ ] Hook does not contain any prohibited AI-fluff words from [Section 9](#9-prohibited-patterns-reference).

### 8.2 Body Gate

- [ ] Every factual claim has a T1–T4 source (see [Section 4.1](#41-the-claim-verification-hierarchy)).
- [ ] No fabricated statistics or superlatives without data.
- [ ] No medical claims.
- [ ] No competitor disparagement.
- [ ] Paragraphs are ≤ 3 lines each.
- [ ] No emoji bullet points.
- [ ] Plain sentences: Subject + Predicate + Object.

### 8.3 CTA Gate

- [ ] Exactly one CTA.
- [ ] CTA uses soft language (no "beli sekarang", "jangan sampai ketinggalan").
- [ ] CTA matches platform convention from [Section 2.5](#25-cta-call-to-action-rules).
- [ ] No fabricated urgency or scarcity.

### 8.4 Compliance Gate

- [ ] Affiliate disclosure is present if an affiliate link exists.
- [ ] Hashtag count is within platform limits from [Section 5.2.1](#521-hashtag-count-by-platform).
- [ ] All hashtags are validated (non-zero posts, not flagged).
- [ ] Post status is `DRAFT` before submission to `REVIEW`.
- [ ] `disclosure_included` field is set to `true` in the content calendar entry.

### 8.5 Platform Gate

- [ ] Post length is within platform character limit.
- [ ] Image dimensions meet platform requirements.
- [ ] Alt text is set on all images.
- [ ] Link placement follows platform convention (bio vs. comment vs. caption).

---

## 9. Prohibited Patterns Reference

### 9.1 Prohibited Words and Phrases

The following words and phrases are **banned** in all Gathot-produced content:

| Prohibited | Replace With |
|---|---|
| Seamlessly / Seamless | Describe the actual behavior ("API calls return in 5ms") |
| Elevate your workflow | Describe the actual function |
| Leverage | Use |
| Next-generation / Next-gen | State the actual specification |
| Empower | Enable, or describe the capability |
| Delve into / Dive deep | See, Read |
| In today's fast-paced world | Delete. Start with the fact. |
| Amazing / Incredible / Luar biasa | State the specific attribute |
| Seamless integration | Describe what actually integrates and how |
| Viral banget | State the verifiable metric (e.g., "2 juta views") |
| Terbaik di Indonesia | Only use if backed by a verifiable ranking source |
| Diskon gila | State the actual discount amount and end date |
| Promo termurah | State the actual price |
| Beli sekarang juga | Use soft CTA ("Cek di bio kalau lo penasaran") |
| Jangan sampai ketinggalan | Delete. No fabricated urgency. |
| Stok terbatas | Only use with verified real-time inventory data |
| Promo berakhir hari ini | Only use with a real, verifiable deadline |
| 99% pengguna puas | Only use with a verifiable data source |
| Trusted by X+ teams | Only use with a verifiable data source |

### 9.2 Prohibited Content Formats

- Emoji as bullet points (`🚀 Feature 1`, `⚡ Feature 2`). Use `-` or `1.` instead.
- All-caps sentences for emphasis. Use **bold** in platforms that support it.
- Fake review screenshots (fabricated or edited).
- Reposting competitor content without explicit permission and credit.
- Posting the same caption verbatim across platforms on the same day (triggers spam filters).

### 9.3 Prohibited Automation Behaviors

- Publishing a post with `status != "APPROVED"`.
- Publishing an affiliate post with `disclosure_included == false`.
- Posting more frequently than the limits in [Section 6.2](#62-posting-frequency-limits).
- Using automated comment bots to inflate engagement metrics.
- Auto-following/unfollowing accounts to game follower counts.

---

## 10. Glossary

| Term | Definition |
|---|---|
| **AEO** | Answer Engine Optimization. Structuring content so AI search engines (Perplexity, ChatGPT Search) can parse and surface it accurately. |
| **Affiliate Link** | A tracked URL that attributes a sale to the content creator and triggers a commission payment. |
| **BPOM** | Badan Pengawas Obat dan Makanan. Indonesia's National Agency of Drug and Food Control. The regulatory body that certifies cosmetic product safety. |
| **Content Calendar** | A structured schedule of planned posts, including metadata, status, and scheduling information. |
| **CTA** | Call-to-Action. The single instruction at the end of a post that tells the reader what to do next. |
| **Engagement Rate (ER)** | `(Likes + Comments + Shares + Saves) / Impressions × 100`. The primary metric for measuring content effectiveness. |
| **Gathot** | The social media automation and content operations agent in the Dalang-AI studio. |
| **Hook** | The first line of a post. Its sole job is to stop the scroll and create enough curiosity to make the reader tap "more". |
| **Keyword Brief** | A structured JSON document containing validated primary, secondary, and long-tail keywords for a specific product and platform. |
| **Long-tail Keyword** | A specific, multi-word search phrase with lower competition and higher conversion intent than a broad keyword. |
| **Psychological Trigger** | A cognitive mechanism that influences a reader's decision to engage with content. |
| **Relay Format** | A writing format that attributes claims to third parties rather than the author's personal experience, used when the author has not personally used the product. |
| **Social Proof Signal** | A reference to verifiable external validation (ratings, certifications, review counts) that increases audience trust. |
| **T1–T4 Source** | The claim verification hierarchy defined in [Section 4.1](#41-the-claim-verification-hierarchy). T1 is the most authoritative; T4 is personal experience. |
| **WIB** | Waktu Indonesia Barat. Western Indonesian Time. UTC+7. |

---

*This document is classified as **Reference + Explanation** under the [Diátaxis Framework](https://diataxis.fr/). For tutorial content on writing your first Gathot post, see `docs/QUICKSTART.md`. For campaign-specific copywriting assets, see `docs/copywriting_omg_lipcream.md`.*
