"""
Field Journal — Self-Evolving Knowledge Base & Pitfall Memory untuk Dalang-AI
Terinspirasi dari arsitektur zhaoxuya520/reverse-skill

Menyimpan pengalaman empiris, kegagalan/error, solusi, dan pola kode yang dapat
dipakai ulang oleh para Wayang sehingga sub-agent tidak mengulangi kesalahan yang sama.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).parent
JOURNAL_DIR = BASE_DIR / "field_journal"
JOURNAL_INDEX_FILE = JOURNAL_DIR / "journal_index.json"


def ensure_journal_dirs():
    """Memastikan direktori field journal dan index siap."""
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    if not JOURNAL_INDEX_FILE.exists():
        JOURNAL_INDEX_FILE.write_text(json.dumps({"entries": []}, indent=2), encoding="utf-8")


def record_journal_entry(
    title: str,
    category: str,
    agent_id: str,
    summary: str,
    pitfalls: List[str],
    solution: str,
    tags: Optional[List[str]] = None,
    reusable_pattern: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Mencatat pelajaran baru / temuan empiris ke field journal.
    Setiap entri disimpan sebagai file markdown dan diindeks ke journal_index.json.
    """
    ensure_journal_dirs()
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    timestamp_slug = now.strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^a-zA-Z0-9_\-]+", "_", title.lower()).strip("_")
    filename = f"{date_str}_{agent_id}_{slug}_{timestamp_slug}.md"
    filepath = JOURNAL_DIR / filename

    entry_id = f"JRN-{timestamp_slug}"
    tags = tags or []

    # Format Markdown dokumen jurnal
    pitfall_items = "\n".join(f"- {p}" for p in pitfalls) if pitfalls else "- Tidak ada jebakan khusus tercatat."
    pattern_block = f"\n```\n{reusable_pattern.strip()}\n```\n" if reusable_pattern else "Tidak ada pattern khusus."

    content = f"""# [{entry_id}] {title}

- **Tanggal**: {date_str}
- **Wayang**: {agent_id.upper()}
- **Kategori**: {category}
- **Tags**: {", ".join(tags) if tags else "none"}

## 1. Ringkasan Kasus / Konteks
{summary.strip()}

## 2. Pitfalls & Jebakan yang Ditemui (What Went Wrong)
{pitfall_items}

## 3. Solusi & Resolusi Terbaik (What Actually Worked)
{solution.strip()}

## 4. Pola yang Dapat Dipakai Ulang (Reusable Pattern)
{pattern_block}
"""
    filepath.write_text(content, encoding="utf-8")

    # Update index JSON
    index_data = {"entries": []}
    try:
        index_data = json.loads(JOURNAL_INDEX_FILE.read_text(encoding="utf-8"))
    except Exception:
        index_data = {"entries": []}

    new_meta = {
        "id": entry_id,
        "title": title,
        "filename": filename,
        "agent_id": agent_id.lower(),
        "category": category.lower(),
        "tags": [t.lower() for t in tags],
        "pitfalls": pitfalls,
        "date": date_str,
    }
    index_data["entries"].append(new_meta)
    JOURNAL_INDEX_FILE.write_text(json.dumps(index_data, indent=2), encoding="utf-8")

    return new_meta


def list_journal_entries(agent_id: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Mendaftar seluruh entri jurnal dengan filter opsional."""
    ensure_journal_dirs()
    try:
        index_data = json.loads(JOURNAL_INDEX_FILE.read_text(encoding="utf-8"))
        entries = index_data.get("entries", [])
    except Exception:
        return []

    if agent_id:
        agent_lower = agent_id.lower()
        entries = [e for e in entries if e.get("agent_id") == agent_lower]
    if category:
        cat_lower = category.lower()
        entries = [e for e in entries if e.get("category") == cat_lower]

    return entries


def query_journal_learnings(context_text: str, agent_id: Optional[str] = None, limit: int = 3) -> str:
    """
    Mencari catatan jurnal yang paling relevan dengan konteks tugas saat ini,
    dan memformatnya sebagai peringatan/panduan empiris sebelum agen bertindak.
    """
    entries = list_journal_entries(agent_id=agent_id)
    if not entries:
        return ""

    tokens = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", context_text.lower()))
    scored_entries = []

    for entry in entries:
        score = 0
        title_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", entry.get("title", "").lower()))
        tag_tokens = set(entry.get("tags", []))
        pitfall_text = " ".join(entry.get("pitfalls", [])).lower()

        score += len(tokens.intersection(title_tokens)) * 3
        score += len(tokens.intersection(tag_tokens)) * 2
        for t in tokens:
            if t in pitfall_text:
                score += 1

        if score > 0:
            scored_entries.append((score, entry))

    scored_entries.sort(key=lambda x: x[0], reverse=True)
    top_entries = [e for _, e in scored_entries[:limit]]

    if not top_entries:
        return ""

    lines = ["\n## 🧠 PRECEDENT & FIELD JOURNAL LEARNINGS (Pelajaran dari Pengalaman Sebelumnya):"]
    for item in top_entries:
        lines.append(f"### 📌 [{item['id']}] {item['title']} (by {item['agent_id'].upper()})")
        if item.get("pitfalls"):
            lines.append("  *Jebakan/Peringatan yang Harus Dihindari:*")
            for pf in item["pitfalls"]:
                lines.append(f"  - ⚠️ {pf}")
        
        # Baca solusi singkat dari file jika ada
        entry_file = JOURNAL_DIR / item["filename"]
        if entry_file.exists():
            try:
                full_text = entry_file.read_text(encoding="utf-8")
                sol_match = re.search(r"## 3\. Solusi & Resolusi Terbaik.*?\n(.*?)(?=\n## 4|\Z)", full_text, re.DOTALL)
                if sol_match:
                    sol_preview = sol_match.group(1).strip().splitlines()[0]
                    lines.append(f"  *Rekomendasi:* {sol_preview}")
            except Exception:
                pass

    return "\n".join(lines) + "\n"
