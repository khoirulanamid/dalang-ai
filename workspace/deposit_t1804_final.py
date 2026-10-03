"""
T-1804: Deposit Naskah & Bukti Live Posting ke Bagong Vault
============================================================
Artefak baru dari T-1803 (Zaki — Live Posting Celana Jeans Korea):
- Bukti screenshot Facebook & Threads yang belum ter-deposit
- Script posting tambahan (post_jeans_with_image.py, post_omg_threads.py)
- agent_error_logger.py (Zaki)
"""

import json
import shutil
import hashlib
import random
import string
from datetime import datetime, timezone
from pathlib import Path

# ─── Konstanta Path ────────────────────────────────────────────────────────────
VAULT_ROOT  = Path("/root/storage/projects/dalang-ai/vault")
VAULT_INDEX = VAULT_ROOT / "vault_index.json"
FRONTEND_VAULT = Path("/root/storage/projects/dalang-ai/frontend/public/vault")
WORKSPACE   = Path("/root/storage/projects/dalang-ai/workspace")
TIMESTAMP   = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _gen_id() -> str:
    return "VLT-" + "".join(random.choices(string.digits, k=5))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_index() -> list:
    if VAULT_INDEX.exists():
        return json.loads(VAULT_INDEX.read_text(encoding="utf-8"))
    return []


def _save_index(data: list) -> None:
    VAULT_INDEX.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    # Mirror ke frontend
    FRONTEND_VAULT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(VAULT_INDEX, FRONTEND_VAULT / "vault_index.json")
    print(f"  ✅ vault_index.json diperbarui ({len(data)} artefak total)")
    print(f"  ✅ Mirror frontend/public/vault/vault_index.json diperbarui")


def _already_indexed(index: list, original_name: str) -> bool:
    """Cek apakah file sudah ada di index (berdasarkan nama asli)."""
    for it in index:
        fname = it.get("filename", "")
        parts = fname.split("_", 2)
        if len(parts) >= 3 and parts[2] == original_name:
            return True
        if fname == original_name:
            return True
    return False


def deposit(
    src: Path,
    category: str,
    title: str,
    producer_agent: str,
    description: str = "",
    metadata: dict = None,
    index: list = None,
) -> dict:
    """Copy file ke vault + frontend mirror, update index, return entry dict."""
    if not src.exists():
        print(f"  ⚠️  SKIP (tidak ditemukan): {src.name}")
        return {}

    # Cek duplikat
    if index is not None and _already_indexed(index, src.name):
        print(f"  ⏭️  SKIP (sudah ter-deposit): {src.name}")
        return {}

    # Buat direktori kategori
    cat_dir = VAULT_ROOT / category
    cat_dir.mkdir(parents=True, exist_ok=True)
    frontend_cat_dir = FRONTEND_VAULT / category
    frontend_cat_dir.mkdir(parents=True, exist_ok=True)

    # Nama file di vault: timestamp_originalname
    dest_name = f"{TIMESTAMP}_{src.name}"
    dest_path = cat_dir / dest_name
    frontend_path = frontend_cat_dir / dest_name

    shutil.copy2(src, dest_path)
    shutil.copy2(src, frontend_path)
    size = dest_path.stat().st_size
    sha  = _sha256(dest_path)

    entry = {
        "id":             _gen_id(),
        "filename":       dest_name,
        "category":       category,
        "producer_agent": producer_agent,
        "title":          title,
        "description":    description,
        "file_path":      str(dest_path),
        "relative_url":   f"/vault/{category}/{dest_name}",
        "size_bytes":     size,
        "sha256":         sha,
        "created_at":     datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "task_id":        "T-1804",
        "sprint":         "Sprint-18",
        "metadata":       metadata or {},
    }

    print(f"  📦 [{category}] {title}")
    print(f"     → {dest_path.name}  ({size:,} bytes)")
    return entry


def main():
    print("=" * 70)
    print("🗄️  BAGONG VAULT DEPOSIT — T-1804 (Sprint 18: Celana Jeans Korea)")
    print("    Deposit Naskah & Bukti Live Posting")
    print("=" * 70)

    index = _load_index()
    new_entries = []

    # ── 1. Bukti Live Facebook (belum ter-deposit) ───────────────────────────
    print("\n📸 [1/4] Bukti Live Facebook (artefak baru)...")
    fb_screenshots = [
        (
            "fb_scrolled_feed.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Feed Discroll Setelah Post (T-1803)",
            "Screenshot Facebook feed setelah discroll, memverifikasi post celana jeans Korea tampil di timeline.",
            {"platform": "Facebook", "stage": "feed_scrolled", "task_ref": "T-1803"},
        ),
        (
            "fb_kirim_live.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Tombol Kirim Diklik (T-1803)",
            "Screenshot Facebook composer saat tombol Kirim/Posting diklik untuk post celana jeans Korea.",
            {"platform": "Facebook", "stage": "submit_clicked", "task_ref": "T-1803"},
        ),
        (
            "fb_image_attached.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Foto Produk Terlampir (T-1803)",
            "Screenshot Facebook composer dengan foto produk celana jeans Korea berhasil dilampirkan.",
            {"platform": "Facebook", "stage": "image_attached", "task_ref": "T-1803"},
        ),
        (
            "fb_user_feed_verified.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Feed User Terverifikasi (T-1803)",
            "Screenshot feed Facebook user yang memverifikasi post celana jeans Korea tampil di profil.",
            {"platform": "Facebook", "stage": "user_feed_verified", "task_ref": "T-1803"},
        ),
        (
            "fb_omg_profile.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Profil OMG Terverifikasi (T-1803)",
            "Screenshot profil Facebook OMG yang digunakan untuk posting kampanye celana jeans Korea.",
            {"platform": "Facebook", "stage": "profile_verified", "task_ref": "T-1803"},
        ),
        (
            "fb_draft_ready.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Draft Post Siap Kirim (T-1803)",
            "Screenshot Facebook composer dengan draft post celana jeans Korea siap dikirim.",
            {"platform": "Facebook", "stage": "draft_ready", "task_ref": "T-1803"},
        ),
        (
            "fb_feed_ready.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Feed Siap Posting (T-1803)",
            "Screenshot Facebook feed dalam kondisi siap untuk posting celana jeans Korea.",
            {"platform": "Facebook", "stage": "feed_ready", "task_ref": "T-1803"},
        ),
        (
            "fb_check.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Pengecekan Awal (T-1803)",
            "Screenshot pengecekan awal Facebook sebelum proses posting celana jeans Korea dimulai.",
            {"platform": "Facebook", "stage": "pre_check", "task_ref": "T-1803"},
        ),
    ]

    for fname, cat, agent, title, desc, meta in fb_screenshots:
        e = deposit(
            src=WORKSPACE / fname,
            category=cat,
            producer_agent=agent,
            title=title,
            description=desc,
            metadata=meta,
            index=index,
        )
        if e:
            new_entries.append(e)

    # ── 2. Bukti Live Threads (belum ter-deposit) ────────────────────────────
    print("\n📸 [2/4] Bukti Live Threads (artefak baru)...")
    threads_screenshots = [
        (
            "threads_feed_real.png",
            "report",
            "zaki",
            "Bukti Live — Threads: Feed Real Setelah Post (T-1803)",
            "Screenshot feed Threads.net real setelah post celana jeans Korea berhasil dipublikasikan.",
            {"platform": "Threads", "stage": "feed_real", "task_ref": "T-1803"},
        ),
        (
            "threads_omg_live_feed.png",
            "report",
            "zaki",
            "Bukti Live — Threads: OMG Live Feed (T-1803)",
            "Screenshot feed Threads OMG yang menampilkan post celana jeans Korea live.",
            {"platform": "Threads", "stage": "omg_live_feed", "task_ref": "T-1803"},
        ),
        (
            "threads_omg_live.png",
            "report",
            "zaki",
            "Bukti Live — Threads: OMG Post Live (T-1803)",
            "Screenshot post OMG di Threads yang sudah live untuk kampanye celana jeans Korea.",
            {"platform": "Threads", "stage": "omg_post_live", "task_ref": "T-1803"},
        ),
        (
            "threads_omg_profile_actual.png",
            "report",
            "zaki",
            "Bukti Live — Threads: Profil OMG Aktual (T-1803)",
            "Screenshot profil Threads OMG aktual yang digunakan untuk posting kampanye.",
            {"platform": "Threads", "stage": "omg_profile_actual", "task_ref": "T-1803"},
        ),
        (
            "profile_verified.png",
            "report",
            "zaki",
            "Bukti Live — Profil Terverifikasi (T-1803)",
            "Screenshot profil akun yang terverifikasi untuk kampanye celana jeans Korea.",
            {"platform": "Threads/Facebook", "stage": "profile_verified", "task_ref": "T-1803"},
        ),
        (
            "ready_post_2thread.png",
            "report",
            "zaki",
            "Bukti Live — Threads: 2 Thread Siap Post (T-1803)",
            "Screenshot Threads composer dengan 2 thread celana jeans Korea siap dipublikasikan.",
            {"platform": "Threads", "stage": "2thread_ready", "task_ref": "T-1803"},
        ),
        (
            "shopee_product_page.png",
            "report",
            "zaki",
            "Bukti Produk — Halaman Shopee Celana Jeans Korea (T-1803)",
            "Screenshot halaman produk Shopee celana jeans Korea yang menjadi target kampanye affiliate.",
            {"platform": "Shopee", "stage": "product_page", "task_ref": "T-1803"},
        ),
    ]

    for fname, cat, agent, title, desc, meta in threads_screenshots:
        e = deposit(
            src=WORKSPACE / fname,
            category=cat,
            producer_agent=agent,
            title=title,
            description=desc,
            metadata=meta,
            index=index,
        )
        if e:
            new_entries.append(e)

    # ── 3. Script Posting Tambahan ───────────────────────────────────────────
    print("\n💻 [3/4] Script Posting Tambahan (Zaki)...")
    scripts = [
        (
            "post_jeans_with_image.py",
            "code",
            "zaki",
            "Script Poster Facebook — Jeans dengan Gambar (T-1803)",
            "Script Python untuk posting celana jeans Korea ke Facebook dengan lampiran gambar produk.",
            {"platform": "Facebook", "feature": "image_post", "task_ref": "T-1803"},
        ),
        (
            "post_omg_threads.py",
            "code",
            "zaki",
            "Script Poster Threads — OMG Campaign (T-1803)",
            "Script Python untuk posting kampanye OMG ke Threads.net.",
            {"platform": "Threads", "campaign": "OMG", "task_ref": "T-1803"},
        ),
        (
            "agent_error_logger.py",
            "code",
            "zaki",
            "Agent Error Logger — Modul Logging Error (T-1803)",
            "Modul Python untuk mencatat error agent selama proses live posting kampanye.",
            {"type": "utility", "feature": "error_logging", "task_ref": "T-1803"},
        ),
    ]

    for fname, cat, agent, title, desc, meta in scripts:
        e = deposit(
            src=WORKSPACE / fname,
            category=cat,
            producer_agent=agent,
            title=title,
            description=desc,
            metadata=meta,
            index=index,
        )
        if e:
            new_entries.append(e)

    # ── 4. Buat post_history.json sebagai audit trail ────────────────────────
    print("\n📋 [4/4] Membuat Post History Audit Trail...")
    post_history = {
        "sprint": "Sprint-18",
        "task_posting": "T-1803",
        "task_deposit": "T-1804",
        "campaign": "Celana Jeans Pria Korea",
        "affiliate_url": "https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "posts": [
            {
                "platform": "Facebook",
                "status": "LIVE",
                "post_type": "foto_produk",
                "evidence_files": [
                    "fb_photo_attached_real.png",
                    "fb_posted_live.png",
                    "fb_posted_verified.png",
                    "fb_enter_result.png",
                    "fb_scrolled_feed.png",
                    "fb_kirim_live.png",
                    "fb_image_attached.png",
                    "fb_user_feed_verified.png",
                    "fb_draft_ready.png",
                    "fb_feed_ready.png",
                    "fb_check.png",
                ],
                "scripts_used": [
                    "post_jeans_facebook.py",
                    "post_jeans_with_image.py",
                ],
                "notes": "Post Facebook dengan foto produk celana jeans Korea berhasil live dan terverifikasi di feed.",
            },
            {
                "platform": "Threads",
                "status": "LIVE",
                "post_type": "thread_bersambung",
                "evidence_files": [
                    "threads_jeans_live.png",
                    "threads_net_feed.png",
                    "threads_image_attached.png",
                    "threads_composer_input.png",
                    "threads_feed_real.png",
                    "threads_omg_live_feed.png",
                    "threads_omg_live.png",
                    "threads_omg_profile_actual.png",
                    "ready_post_2thread.png",
                ],
                "scripts_used": [
                    "post_jeans_threads.py",
                    "post_omg_threads.py",
                ],
                "notes": "Thread bersambung 2 post celana jeans Korea berhasil live di Threads.net.",
            },
        ],
        "qa_gate": {
            "agent": "ren",
            "task_ref": "T-1802",
            "status": "LULUS",
            "test_file": "test_t1802_quality_gate_jeans_naskah.py",
        },
        "naskah_canonical": "docs/naskah_celana_jeans_korea_canonical.md",
        "campaign_data": "docs/celana_jeans_campaign.json",
    }

    history_path = WORKSPACE / "post_history_sprint18.json"
    history_path.write_text(
        json.dumps(post_history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  ✅ post_history_sprint18.json dibuat di workspace")

    e = deposit(
        src=history_path,
        category="campaign",
        producer_agent="bagong",
        title="Post History Audit Trail — Sprint 18 Celana Jeans Korea (T-1804)",
        description="Riwayat lengkap posting kampanye celana jeans Korea Sprint 18: platform, status, bukti, dan referensi artefak.",
        metadata={"type": "audit_trail", "sprint": "Sprint-18", "campaign": "celana_jeans_korea"},
        index=index,
    )
    if e:
        new_entries.append(e)

    # ── Simpan ke vault_index.json ───────────────────────────────────────────
    print()
    print(f"📊 Total artefak baru: {len(new_entries)}")
    index.extend(new_entries)
    _save_index(index)

    # ── Ringkasan ────────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("📋 RINGKASAN DEPOSIT T-1804")
    print("=" * 70)
    for e in new_entries:
        cat = e["category"]
        title = e["title"]
        url = e["relative_url"]
        print(f"  [{e['id']}] [{cat:12s}] {title}")
        print(f"           URL: {url}")
    print()
    print(f"✅ Deposit selesai — {len(new_entries)} artefak baru Sprint 18 tersimpan di Vault.")
    print(f"   Total vault: {len(index)} artefak.")
    print("=" * 70)

    return new_entries


if __name__ == "__main__":
    main()
