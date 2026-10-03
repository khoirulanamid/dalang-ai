"""
Bagong Vault Deposit Script — T-1804
Sprint 18: Kampanye Celana Jeans Korea — Facebook Posting

Artefak yang di-deposit:
1. [document]   Naskah copywriting celana jeans Korea (Gathot T-1801)
2. [document]   Campaign data JSON celana jeans Korea
3. [code]       Script poster Facebook jeans (Zaki T-1803)
4. [code]       Script poster Threads jeans
5. [code]       Quality Gate test T-1802 (Ren)
6. [report]     Bukti live posting Facebook — screenshot fb_photo_attached_real.png
7. [report]     Bukti live posting Facebook — screenshot fb_posted_live.png
8. [report]     Bukti live posting Facebook — screenshot fb_posted_verified.png
9. [report]     Bukti live posting Threads — screenshot threads_jeans_live.png
10. [report]    Bukti live posting Threads — screenshot threads_net_feed.png
11. [report]    Bukti debug posting — screenshot fb_enter_result.png
"""

import json
import shutil
import hashlib
import random
import string
from datetime import datetime, timezone
from pathlib import Path

# ─── Konstanta Path ────────────────────────────────────────────────────────────
VAULT_ROOT   = Path("/root/storage/projects/dalang-ai/vault")
VAULT_INDEX  = VAULT_ROOT / "vault_index.json"
WORKSPACE    = Path("/root/storage/projects/dalang-ai/workspace")
TIMESTAMP    = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _gen_id() -> str:
    """Generate 5-digit random vault ID."""
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
    print(f"  ✅ vault_index.json diperbarui ({len(data)} artefak total)")


def deposit(
    src: Path,
    category: str,
    title: str,
    producer_agent: str,
    description: str = "",
    metadata: dict | None = None,
) -> dict:
    """Copy file ke vault, update index, return entry dict."""
    if not src.exists():
        print(f"  ⚠️  SKIP (tidak ditemukan): {src}")
        return {}

    # Buat direktori kategori
    cat_dir = VAULT_ROOT / category
    cat_dir.mkdir(parents=True, exist_ok=True)

    # Nama file di vault: timestamp_originalname
    dest_name = f"{TIMESTAMP}_{src.name}"
    dest_path = cat_dir / dest_name

    shutil.copy2(src, dest_path)
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
    print(f"     → {dest_path}  ({size:,} bytes)")
    return entry


def main():
    print("=" * 70)
    print("🗄️  BAGONG VAULT DEPOSIT — T-1804 (Sprint 18: Celana Jeans Korea)")
    print("=" * 70)

    index = _load_index()
    new_entries = []

    # ── 1. Naskah Copywriting Celana Jeans (Gathot T-1801) ──────────────────
    e = deposit(
        src=WORKSPACE / "docs" / "copywriting_omg_lipcream.md",
        category="document",
        producer_agent="gathot",
        title="Naskah Copywriting OMG Lip Cream — Sprint 15 (Gathot)",
        description=(
            "Naskah copywriting affiliate OMG Oh My Glam Matte Kiss Lip Cream "
            "untuk platform Threads dan Facebook. Mencakup: metadata produk, "
            "compliance checklist, 5 variasi hook, dan 3 post canonical. "
            "Dibuat oleh Gathot sesuai standar gathot_social_standards.md."
        ),
        metadata={
            "product": "OMG Oh My Glam Matte Kiss Lip Cream",
            "platform": ["Threads", "Facebook"],
            "sprint": "Sprint-15",
            "task_ref": "T-1501",
        },
    )
    if e:
        new_entries.append(e)

    # ── 2. Campaign JSON Celana Jeans ────────────────────────────────────────
    e = deposit(
        src=WORKSPACE / "docs" / "celana_jeans_campaign.json",
        category="campaign",
        producer_agent="gathot",
        title="Campaign Data — Celana Jeans Pria Korea (Sprint 18)",
        description=(
            "Data kampanye affiliate celana jeans Korea: nama produk, "
            "affiliate URL Shopee, path gambar produk, dan spesifikasi teknis. "
            "Digunakan sebagai referensi canonical oleh Gathot (T-1801) dan Zaki (T-1803)."
        ),
        metadata={
            "product": "Celana Jeans Pria Panjang Gaya Korea",
            "affiliate_url": "https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq",
            "platform": "Shopee",
            "task_ref": "T-1801",
        },
    )
    if e:
        new_entries.append(e)

    # ── 3. Naskah Copywriting Celana Jeans — dari post_jeans_threads.py ─────
    # Ekstrak naskah canonical dari script sebagai dokumen terpisah
    naskah_path = WORKSPACE / "docs" / "naskah_celana_jeans_korea_canonical.md"
    naskah_content = """# Naskah Canonical — Celana Jeans Pria Korea (Sprint 18 / T-1801)

**Produk**: Celana Jeans Pria Panjang Gaya Korea  
**Affiliate URL**: https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq  
**Platform**: Facebook (foto produk) + Threads (thread bersambung)  
**Sudut Pandang**: Cowok Praktis — ga sesak duduk lama  
**Dibuat oleh**: Gathot (Wira Warta) — T-1801  
**QA Gate**: Ren — T-1802 (LULUS)  
**Dieksekusi oleh**: Zaki — T-1803  

---

## Post 1 — Hook Relatable (Threads / Facebook)

```
Sebagai cowok praktis, musuh terbesar pas nongkrong atau duduk seharian
itu bukan kerjaan, tapi celana jeans yang bikin begah & sesak napas di
perut bawah 🗿

Ini celana model loose-fit / baggy gaya Korea tapi ada opsi pinggang
karetnya. Duduk santai di warkop berjam-jam aman, ga perlu diam-diam
lepas kancing celana lagi 👌
```

---

## Post 2 — Kurasi Spek Objektif (Threads lanjutan / Facebook)

```
Kurasi speknya:
• Model: Loose-fit wide-leg gaya Korea (ga ngetat, ga bikin gerah)
• Bahan: Denim lembut tahan bentuk (ga melar/ga molor)
• Pinggang: Ada varian karet fleksibel & kancing biasa
• Saku: 4 saku dalam aman buat hp/dompet

🔗 Spill etalase produk di Shopee:
https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq
```

---

## Hashtag & Social SEO Keywords

```
#celanajeans #jeanskorea #outfitcowok #streetwearkorea #loosefitjeans
#baggyjeanskorea #fashioncowok #jeansmurah #shopeeaffiliate #outfitpria
```

---

## Compliance Checklist (Ren QA Gate T-1802)

- [x] Bebas klaim palsu (tidak ada "aku udah pake", "saya cobain", dll.)
- [x] Humor relatable natural (bukan forced/cringe)
- [x] Spek objektif berdasarkan data produk (bukan opini personal)
- [x] Tidak ada spam trigger words ("diskon gila", "promo termurah", dll.)
- [x] Format bersambung (Post 1 → Post 2) sesuai standar Threads
- [x] Affiliate URL valid dan tercantum
- [x] Hashtag relevan (5–10 tag)
- [x] Tidak ada raw HTML atau Markdown formatting
- [x] Panjang hook ≤ 280 karakter (Threads limit)
"""
    naskah_path.write_text(naskah_content, encoding="utf-8")

    e = deposit(
        src=naskah_path,
        category="document",
        producer_agent="gathot",
        title="Naskah Canonical Celana Jeans Korea — Sprint 18 (T-1801)",
        description=(
            "Naskah copywriting canonical untuk kampanye affiliate celana jeans "
            "Korea. Sudut pandang: Cowok Praktis. Mencakup 2 post (hook relatable + "
            "kurasi spek objektif), hashtag SEO, dan compliance checklist QA Gate Ren. "
            "Status: LULUS QA T-1802, LIVE di Facebook & Threads via T-1803."
        ),
        metadata={
            "product": "Celana Jeans Pria Panjang Gaya Korea",
            "platform": ["Facebook", "Threads"],
            "qa_status": "LULUS",
            "qa_agent": "ren",
            "qa_task": "T-1802",
            "live_status": "POSTED",
            "poster_agent": "zaki",
            "poster_task": "T-1803",
        },
    )
    if e:
        new_entries.append(e)

    # ── 4. Script Poster Facebook Jeans (Zaki T-1803) ───────────────────────
    e = deposit(
        src=WORKSPACE / "post_jeans_facebook.py",
        category="code",
        producer_agent="zaki",
        title="Script Poster Facebook — Celana Jeans Korea (T-1803)",
        description=(
            "Script Playwright untuk posting bergambar ke Facebook personal "
            "Rizqi Mubarak. Fitur: load cookie session, dismiss popups, "
            "attach foto produk celana_jeans_korea_1.jpg, ketik naskah canonical, "
            "klik tombol Posting, verifikasi profil. Dibuat oleh Zaki untuk T-1803."
        ),
        metadata={
            "language": "Python",
            "framework": "Playwright",
            "platform": "Facebook",
            "task_ref": "T-1803",
            "sprint": "Sprint-18",
        },
    )
    if e:
        new_entries.append(e)

    # ── 5. Script Poster Threads Jeans ──────────────────────────────────────
    e = deposit(
        src=WORKSPACE / "post_jeans_threads.py",
        category="code",
        producer_agent="zaki",
        title="Script Poster Threads — Celana Jeans Korea (Sprint 18)",
        description=(
            "Script Playwright untuk posting thread bersambung ke Threads.net "
            "dengan naskah celana jeans Korea. Fitur: load cookie, compose thread, "
            "attach gambar, submit post, verifikasi feed."
        ),
        metadata={
            "language": "Python",
            "framework": "Playwright",
            "platform": "Threads",
            "sprint": "Sprint-18",
        },
    )
    if e:
        new_entries.append(e)

    # ── 6. Quality Gate Test T-1802 (Ren) ───────────────────────────────────
    e = deposit(
        src=WORKSPACE / "workspace" / "test_t1802_quality_gate_jeans_naskah.py",
        category="report",
        producer_agent="ren",
        title="Quality Gate Test Suite — Naskah Jeans Korea (T-1802)",
        description=(
            "Test suite pytest untuk validasi naskah copywriting celana jeans Korea. "
            "Mencakup: cek klaim palsu, humor natural, spek objektif, format bersambung, "
            "hashtag SEO, panjang karakter, tidak ada HTML/Markdown, tidak ada placeholder. "
            "Dibuat oleh Ren sebagai QA Gate T-1802. Status: LULUS."
        ),
        metadata={
            "language": "Python",
            "framework": "pytest",
            "qa_result": "PASS",
            "task_ref": "T-1802",
            "sprint": "Sprint-18",
        },
    )
    if e:
        new_entries.append(e)

    # ── 7–11. Screenshot Bukti Live Posting ─────────────────────────────────
    screenshots = [
        (
            "fb_photo_attached_real.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Foto Produk Terlampir (T-1803)",
            "Screenshot Facebook saat foto celana jeans Korea berhasil dilampirkan ke composer post sebelum submit.",
            {"platform": "Facebook", "stage": "photo_attached", "task_ref": "T-1803"},
        ),
        (
            "fb_posted_live.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Post Terkirim (T-1803)",
            "Screenshot Facebook setelah post celana jeans Korea berhasil dikirim/live di profil Rizqi Mubarak.",
            {"platform": "Facebook", "stage": "post_live", "task_ref": "T-1803"},
        ),
        (
            "fb_posted_verified.png",
            "report",
            "zaki",
            "Bukti Live — Facebook: Post Terverifikasi di Feed (T-1803)",
            "Screenshot verifikasi post celana jeans Korea tampil di feed Facebook profil Rizqi Mubarak.",
            {"platform": "Facebook", "stage": "post_verified", "task_ref": "T-1803"},
        ),
        (
            "fb_enter_result.png",
            "report",
            "zaki",
            "Bukti Debug — Facebook: Hasil Enter/Submit Post (T-1803)",
            "Screenshot debug setelah aksi submit (Enter/klik Posting) pada composer Facebook untuk post jeans Korea.",
            {"platform": "Facebook", "stage": "submit_result", "task_ref": "T-1803"},
        ),
        (
            "threads_jeans_live.png",
            "report",
            "zaki",
            "Bukti Live — Threads: Post Jeans Korea Live (T-1803)",
            "Screenshot Threads.net setelah post celana jeans Korea berhasil dipublikasikan.",
            {"platform": "Threads", "stage": "post_live", "task_ref": "T-1803"},
        ),
        (
            "threads_net_feed.png",
            "report",
            "zaki",
            "Bukti Live — Threads: Feed Verifikasi Post Jeans Korea (T-1803)",
            "Screenshot feed Threads.net yang memverifikasi post celana jeans Korea tampil di timeline.",
            {"platform": "Threads", "stage": "feed_verified", "task_ref": "T-1803"},
        ),
        (
            "threads_image_attached.png",
            "report",
            "zaki",
            "Bukti Live — Threads: Gambar Produk Terlampir (T-1803)",
            "Screenshot Threads composer dengan gambar produk celana jeans Korea berhasil dilampirkan.",
            {"platform": "Threads", "stage": "image_attached", "task_ref": "T-1803"},
        ),
        (
            "threads_composer_input.png",
            "report",
            "zaki",
            "Bukti Live — Threads: Naskah Diketik di Composer (T-1803)",
            "Screenshot Threads composer dengan naskah celana jeans Korea sudah diketik, siap submit.",
            {"platform": "Threads", "stage": "composer_ready", "task_ref": "T-1803"},
        ),
    ]

    for fname, cat, agent, title, desc, meta in screenshots:
        e = deposit(
            src=WORKSPACE / fname,
            category=cat,
            producer_agent=agent,
            title=title,
            description=desc,
            metadata=meta,
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
        print(f"  [{e['id']}] [{e['category']:12s}] {e['title']}")
        print(f"           URL: {e['relative_url']}")
    print()
    print(f"✅ Deposit selesai — {len(new_entries)} artefak Sprint 18 tersimpan di Vault.")
    print(f"   Total vault: {len(index)} artefak.")
    print("=" * 70)

    return new_entries


if __name__ == "__main__":
    main()
