"""
Script Pengarsipan T-1706: Akta Kelahiran & Spesifikasi Wayang Gathot
Dieksekusi oleh: Bagong (Asset & Release Custodian)
Task ID: T-1706
"""

import sys
import os
import json
import time
import shutil
from pathlib import Path

# Tambahkan path project ke sys.path
sys.path.insert(0, "/root/storage/projects/dalang-ai")

VAULT_DIR = Path("/root/storage/projects/dalang-ai/vault")
VAULT_INDEX_FILE = VAULT_DIR / "vault_index.json"
FRONTEND_PUBLIC = Path("/root/storage/projects/dalang-ai/frontend/public/vault")

def load_index():
    if not VAULT_INDEX_FILE.exists():
        return []
    with open(VAULT_INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_index(items):
    with open(VAULT_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"✅ vault_index.json diperbarui — total {len(items)} entri")

def deposit_artifact(source_path: str, category: str, producer_agent: str,
                     title: str, description: str = "", metadata: dict = None):
    """Deposit artefak ke vault tanpa QA gate (Bagong internal deposit)."""
    src = Path(source_path)
    if not src.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {source_path}")

    # Buat direktori vault kategori
    cat_dir = VAULT_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)

    # Buat nama file dengan timestamp
    timestamp_str = time.strftime("%Y%m%d_%H%M%S")
    dest_filename = f"{timestamp_str}_{src.name}"
    dest_path = cat_dir / dest_filename

    # Copy ke vault
    shutil.copy2(src, dest_path)

    # Mirror ke frontend/public
    public_dir = FRONTEND_PUBLIC / category
    public_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, public_dir / dest_filename)

    # Buat entry index
    item_id = f"VLT-{abs(hash(dest_filename)) % 100000:05d}"
    item = {
        "id": item_id,
        "filename": dest_filename,
        "category": category,
        "producer_agent": producer_agent,
        "title": title,
        "description": description,
        "file_path": str(dest_path),
        "relative_url": f"/vault/{category}/{dest_filename}",
        "size_bytes": os.path.getsize(dest_path),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": metadata or {},
    }

    # Update index
    index = load_index()
    index.insert(0, item)
    save_index(index)

    print(f"📦 DEPOSITED: [{item_id}] {title}")
    print(f"   Category  : {category}")
    print(f"   Agent     : {producer_agent}")
    print(f"   Vault Path: {dest_path}")
    print(f"   Public URL: /vault/{category}/{dest_filename}")
    print(f"   Size      : {item['size_bytes']:,} bytes")
    print()
    return item


def main():
    print("=" * 65)
    print("📋 BAGONG VAULT — PENGARSIPAN T-1706")
    print("   Akta Kelahiran & Spesifikasi Wayang Gathot")
    print("=" * 65)
    print()

    # ── ARTEFAK 1: Akta Kelahiran Gathot ─────────────────────────────
    akta_src = "/root/storage/projects/dalang-ai/workspace/standards/gathot_akta_kelahiran.md"
    item1 = deposit_artifact(
        source_path=akta_src,
        category="document",
        producer_agent="bagong",
        title="Akta Kelahiran Wayang Gathot — DALANG-WAYANG-007",
        description=(
            "Dokumen resmi identitas Wayang Gathot (Social Media Automation & Content Operations Agent). "
            "Berisi nomor akta, peran, tanggung jawab, relasi antar-Wayang, kapabilitas, dan deklarasi resmi. "
            "Diterbitkan oleh Bagong sebagai Juru Simpan Vault pada Sprint-16."
        ),
        metadata={
            "nomor_akta": "DALANG-WAYANG-007",
            "wayang_name": "Gathot",
            "wayang_version": "v1.0.0",
            "task_id": "T-1706",
            "sprint": "Sprint-16",
            "doc_type": "Akta Kelahiran",
            "diataxis_class": "Reference",
        }
    )

    # ── ARTEFAK 2: Spesifikasi / Standar Engineering Gathot ──────────
    spec_src = "/root/storage/projects/dalang-ai/workspace/standards/gathot_social_standards.md"
    item2 = deposit_artifact(
        source_path=spec_src,
        category="document",
        producer_agent="gathot",
        title="Gathot Social Media Engineering Standards v1.0.0",
        description=(
            "Dokumen standar engineering lengkap yang mengatur semua konten yang diproduksi, "
            "dijadwalkan, atau dipublikasikan oleh Gathot. Mencakup: Copywriting SOP Viral Content, "
            "Hook Psychology Framework, Ethical Curation (No False Claims), Social SEO & Keyword Research, "
            "Posting Management & Scheduling, Platform-Specific Rules, Quality Gate Checklist, "
            "dan Prohibited Patterns Reference. Compliance: Diátaxis · Google Dev Docs · Meta Guidelines."
        ),
        metadata={
            "version": "1.0.0",
            "last_updated": "2026-10-02",
            "wayang_name": "Gathot",
            "task_id": "T-1706",
            "sprint": "Sprint-16",
            "doc_type": "Engineering Standards",
            "diataxis_class": "Reference + Explanation",
            "compliance": [
                "Diátaxis Framework",
                "Google Developer Documentation Style Guide",
                "Meta Content Guidelines",
                "Anti-AI-Slop Directives",
                "mika_docs_standards.md"
            ],
            "sections": 10,
            "platforms_covered": ["Threads", "Facebook", "Instagram", "TikTok"],
        }
    )

    # ── RINGKASAN AKHIR ───────────────────────────────────────────────
    print("=" * 65)
    print("✅ PENGARSIPAN T-1706 SELESAI")
    print("=" * 65)
    print(f"  📄 Artefak 1: {item1['id']} — {item1['title'][:50]}...")
    print(f"     URL: {item1['relative_url']}")
    print(f"  📄 Artefak 2: {item2['id']} — {item2['title'][:50]}...")
    print(f"     URL: {item2['relative_url']}")
    print()

    # Verifikasi index
    index = load_index()
    gathot_entries = [x for x in index if "gathot" in x.get("filename", "").lower()
                      or "gathot" in x.get("title", "").lower()]
    print(f"  📊 Total entri vault_index.json: {len(index)}")
    print(f"  🎭 Entri terkait Gathot: {len(gathot_entries)}")
    print()
    print("  Vault paths:")
    print(f"    {item1['file_path']}")
    print(f"    {item2['file_path']}")
    print()
    print("  Frontend public URLs:")
    print(f"    /vault/document/{item1['filename']}")
    print(f"    /vault/document/{item2['filename']}")
    print("=" * 65)

    return item1, item2


if __name__ == "__main__":
    main()
