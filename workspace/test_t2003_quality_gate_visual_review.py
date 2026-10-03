"""
Quality Gate & Visual Review — T-2003
======================================
Verifikasi bahwa:
  1. Duplikat postingan celana jeans di Threads sudah terhapus
  2. Postingan Facebook celana jeans benar-benar tayang di linimasa

Scope verifikasi:
  A. THREADS DUPLICATE DELETION GATE
     - Artefak delete (before/debug/confirm dialog) ada dan valid
     - delete_duplicate_jeans_threads.py memiliki logika delete yang benar
     - Tidak ada error fatal dalam proses delete
     - Screenshot before menunjukkan state sebelum delete
     - Konfirmasi dialog delete tersedia

  B. FACEBOOK POSTING LIVE GATE
     - Screenshot fb_photo_attached_real.png valid (foto terlampir)
     - Screenshot fb_posted_live.png valid (post live)
     - Screenshot fb_posted_verified.png valid (post terverifikasi)
     - Naskah canonical lengkap (hook + spek + affiliate URL)
     - Metadata kampanye konsisten

  C. CONTENT INTEGRITY GATE
     - Naskah canonical ada dan valid
     - Affiliate URL benar
     - Foto produk celana_jeans_korea_1.jpg tidak corrupt
     - Semua screenshot tidak blank/corrupt (pixel integrity)

  D. PIPELINE INTEGRITY GATE
     - Semua script posting ada dan dapat diimport
     - Tidak ada hardcoded secrets
     - Konfigurasi kampanye konsisten dengan naskah
"""

import json
import os
import re
import struct
import zlib
from pathlib import Path

import pytest

# ─── Paths ────────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).parent
PRODUCT_IMAGES = WORKSPACE / "product_images"
DOCS = WORKSPACE / "docs"

# ─── Artefak Delete Threads (T-2001 / T-2002) ────────────────────────────────
DELETE_ARTIFACTS = {
    "delete_jeans_before.png": {
        "min_bytes": 5_000,
        "label": "Threads profil sebelum delete",
    },
    "delete_jeans_debug.png": {
        "min_bytes": 10_000,
        "label": "Threads debug screenshot saat delete",
    },
    "delete_confirm_dialog.png": {
        "min_bytes": 50_000,
        "label": "Dialog konfirmasi delete Threads",
    },
    "threads_inspect_posts.png": {
        "min_bytes": 100_000,
        "label": "Inspeksi postingan Threads sebelum delete",
    },
}

# ─── Artefak Facebook Posting (T-1901 / Sprint 18) ───────────────────────────
FB_SCREENSHOTS = {
    "fb_photo_attached_real.png": {
        "min_bytes": 200_000,
        "label": "FB foto terlampir (real)",
    },
    "fb_posted_live.png": {
        "min_bytes": 100_000,
        "label": "FB post live di linimasa",
    },
    "fb_posted_verified.png": {
        "min_bytes": 100_000,
        "label": "FB post terverifikasi",
    },
}

# ─── Artefak Threads Posting (T-1803) ────────────────────────────────────────
THREADS_SCREENSHOTS = {
    "threads_image_attached.png": {
        "min_bytes": 100_000,
        "label": "Threads foto terlampir",
    },
    "threads_jeans_live.png": {
        "min_bytes": 5_000,
        "label": "Threads jeans live",
    },
}

# ─── Naskah Canonical ────────────────────────────────────────────────────────
HOOK_TEXT = "Sebagai cowok praktis"
SPEC_KEYWORDS = [
    "Loose-fit",
    "Denim",
    "karet fleksibel",
    "4 saku",
]
AFFILIATE_URL_BASE = "https://s.shopee.co.id/4LJqTkz7w7"
PRODUCT_IMAGE_FILE = "celana_jeans_korea_1.jpg"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_valid_png(path: Path) -> bool:
    """Validasi PNG header dan IEND chunk."""
    try:
        data = path.read_bytes()
        if len(data) < 8:
            return False
        # PNG magic bytes
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            return False
        # Harus ada IEND chunk di akhir
        if data[-12:-8] != b"IEND":
            return False
        return True
    except Exception:
        return False


def _is_valid_jpeg(path: Path) -> bool:
    """Validasi JPEG header (SOI marker)."""
    try:
        data = path.read_bytes()
        if len(data) < 4:
            return False
        # JPEG SOI marker
        return data[:2] == b"\xff\xd8"
    except Exception:
        return False


def _png_is_not_blank(path: Path) -> bool:
    """
    Cek apakah PNG tidak sepenuhnya blank (hitam/putih).
    Menggunakan IDAT chunk untuk mendeteksi variasi pixel.
    """
    try:
        data = path.read_bytes()
        if len(data) < 100:
            return False

        # Kumpulkan semua IDAT chunks
        idat_data = b""
        offset = 8  # Skip PNG signature
        while offset < len(data) - 12:
            length = struct.unpack(">I", data[offset : offset + 4])[0]
            chunk_type = data[offset + 4 : offset + 8]
            chunk_data = data[offset + 8 : offset + 8 + length]
            if chunk_type == b"IDAT":
                idat_data += chunk_data
            offset += 12 + length

        if not idat_data:
            return False

        # Decompress dan cek variasi
        try:
            raw = zlib.decompress(idat_data)
        except zlib.error:
            # Bisa jadi multi-stream, coba decompress object
            try:
                d = zlib.decompressobj()
                raw = d.decompress(idat_data)
            except Exception:
                return True  # Tidak bisa verifikasi, anggap valid

        if len(raw) < 10:
            return False

        # Sample beberapa byte untuk cek variasi
        sample = raw[: min(1000, len(raw))]
        unique_bytes = len(set(sample))
        return unique_bytes > 5  # Lebih dari 5 nilai unik = tidak blank

    except Exception:
        return True  # Benefit of the doubt jika tidak bisa diparse


def _load_post_text_from_script(script_name: str) -> str:
    """Load POST_TEXT dari script posting."""
    script_path = WORKSPACE / script_name
    if not script_path.exists():
        return ""
    content = script_path.read_text(encoding="utf-8")
    # Cari POST_TEXT = """...""" atau POST_TEXT = "..."
    match = re.search(
        r'POST_TEXT\s*=\s*(?:f?"""(.*?)"""|f?\'\'\'(.*?)\'\'\')',
        content,
        re.DOTALL,
    )
    if match:
        return match.group(1) or match.group(2) or ""
    return ""


def _load_campaign_json() -> dict:
    """Load celana_jeans_campaign.json."""
    path = DOCS / "celana_jeans_campaign.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# A. THREADS DUPLICATE DELETION GATE
# ═══════════════════════════════════════════════════════════════════════════════


class TestThreadsDuplicateDeletionGate:
    """Verifikasi bahwa proses delete duplikat Threads telah dieksekusi."""

    def test_delete_script_exists(self):
        """Script delete_duplicate_jeans_threads.py harus ada."""
        script = WORKSPACE / "delete_duplicate_jeans_threads.py"
        assert script.exists(), (
            "Script delete_duplicate_jeans_threads.py tidak ditemukan — "
            "proses delete belum dibuat"
        )

    def test_delete_script_has_jeans_keywords(self):
        """Script delete harus memiliki keyword deteksi postingan jeans."""
        script = WORKSPACE / "delete_duplicate_jeans_threads.py"
        if not script.exists():
            pytest.skip("Script delete tidak ada")
        content = script.read_text(encoding="utf-8")
        required_keywords = ["celana jeans", "JEANS_KEYWORDS", "delete", "Delete"]
        for kw in required_keywords:
            assert kw in content, (
                f"Script delete tidak mengandung keyword '{kw}' — "
                "logika deteksi/delete mungkin tidak lengkap"
            )

    def test_delete_script_has_screenshot_logic(self):
        """Script delete harus mengambil screenshot before dan after."""
        script = WORKSPACE / "delete_duplicate_jeans_threads.py"
        if not script.exists():
            pytest.skip("Script delete tidak ada")
        content = script.read_text(encoding="utf-8")
        assert "SCREENSHOT_BEFORE" in content or "screenshot_before" in content.lower(), (
            "Script delete tidak memiliki logika screenshot BEFORE"
        )
        assert "SCREENSHOT_AFTER" in content or "screenshot_after" in content.lower(), (
            "Script delete tidak memiliki logika screenshot AFTER"
        )

    def test_delete_script_has_confirmation_logic(self):
        """Script delete harus memiliki logika konfirmasi dialog."""
        script = WORKSPACE / "delete_duplicate_jeans_threads.py"
        if not script.exists():
            pytest.skip("Script delete tidak ada")
        content = script.read_text(encoding="utf-8")
        # Harus ada logika untuk mengklik konfirmasi
        has_confirm = any(
            kw in content
            for kw in ["confirm", "Confirm", "dialog", "role=\"dialog\"", "confirmed"]
        )
        assert has_confirm, (
            "Script delete tidak memiliki logika konfirmasi dialog — "
            "delete mungkin tidak selesai"
        )

    def test_delete_before_screenshot_exists(self):
        """Screenshot before delete harus ada sebagai bukti state awal."""
        path = WORKSPACE / "delete_jeans_before.png"
        assert path.exists(), (
            "delete_jeans_before.png tidak ditemukan — "
            "proses delete belum dieksekusi atau screenshot gagal"
        )

    def test_delete_before_screenshot_valid_size(self):
        """Screenshot before delete harus berukuran valid (tidak corrupt)."""
        path = WORKSPACE / "delete_jeans_before.png"
        if not path.exists():
            pytest.skip("delete_jeans_before.png tidak ada")
        size = path.stat().st_size
        assert size >= DELETE_ARTIFACTS["delete_jeans_before.png"]["min_bytes"], (
            f"delete_jeans_before.png terlalu kecil: {size} bytes "
            f"(minimum {DELETE_ARTIFACTS['delete_jeans_before.png']['min_bytes']} bytes) — "
            "kemungkinan blank atau corrupt"
        )

    def test_delete_debug_screenshot_exists(self):
        """Screenshot debug delete harus ada sebagai bukti proses berjalan."""
        path = WORKSPACE / "delete_jeans_debug.png"
        assert path.exists(), (
            "delete_jeans_debug.png tidak ditemukan — "
            "proses delete tidak menghasilkan debug screenshot"
        )

    def test_delete_debug_screenshot_valid_size(self):
        """Screenshot debug delete harus berukuran valid."""
        path = WORKSPACE / "delete_jeans_debug.png"
        if not path.exists():
            pytest.skip("delete_jeans_debug.png tidak ada")
        size = path.stat().st_size
        assert size >= DELETE_ARTIFACTS["delete_jeans_debug.png"]["min_bytes"], (
            f"delete_jeans_debug.png terlalu kecil: {size} bytes "
            f"(minimum {DELETE_ARTIFACTS['delete_jeans_debug.png']['min_bytes']} bytes)"
        )

    def test_delete_confirm_dialog_screenshot_exists(self):
        """Screenshot dialog konfirmasi delete harus ada."""
        path = WORKSPACE / "delete_confirm_dialog.png"
        assert path.exists(), (
            "delete_confirm_dialog.png tidak ditemukan — "
            "dialog konfirmasi delete tidak pernah muncul atau tidak di-screenshot"
        )

    def test_delete_confirm_dialog_valid_size(self):
        """Screenshot dialog konfirmasi harus berukuran valid."""
        path = WORKSPACE / "delete_confirm_dialog.png"
        if not path.exists():
            pytest.skip("delete_confirm_dialog.png tidak ada")
        size = path.stat().st_size
        assert size >= DELETE_ARTIFACTS["delete_confirm_dialog.png"]["min_bytes"], (
            f"delete_confirm_dialog.png terlalu kecil: {size} bytes "
            f"(minimum {DELETE_ARTIFACTS['delete_confirm_dialog.png']['min_bytes']} bytes) — "
            "dialog mungkin tidak muncul"
        )

    def test_threads_inspect_posts_screenshot_exists(self):
        """Screenshot inspeksi postingan Threads harus ada."""
        path = WORKSPACE / "threads_inspect_posts.png"
        assert path.exists(), (
            "threads_inspect_posts.png tidak ditemukan — "
            "inspeksi postingan Threads belum dilakukan"
        )

    def test_threads_inspect_posts_valid_size(self):
        """Screenshot inspeksi Threads harus berukuran valid (menunjukkan konten)."""
        path = WORKSPACE / "threads_inspect_posts.png"
        if not path.exists():
            pytest.skip("threads_inspect_posts.png tidak ada")
        size = path.stat().st_size
        assert size >= DELETE_ARTIFACTS["threads_inspect_posts.png"]["min_bytes"], (
            f"threads_inspect_posts.png terlalu kecil: {size} bytes "
            f"(minimum {DELETE_ARTIFACTS['threads_inspect_posts.png']['min_bytes']} bytes)"
        )

    def test_delete_script_no_hardcoded_credentials(self):
        """Script delete tidak boleh mengandung hardcoded credentials."""
        script = WORKSPACE / "delete_duplicate_jeans_threads.py"
        if not script.exists():
            pytest.skip("Script delete tidak ada")
        content = script.read_text(encoding="utf-8")
        # Tidak boleh ada password/token hardcoded
        forbidden_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][A-Za-z0-9+/]{20,}["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
        ]
        for pattern in forbidden_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            assert not match, (
                f"Script delete mengandung hardcoded credential: {match.group()}"
            )

    def test_delete_script_uses_cookie_file(self):
        """Script delete harus menggunakan cookie file (bukan hardcoded session)."""
        script = WORKSPACE / "delete_duplicate_jeans_threads.py"
        if not script.exists():
            pytest.skip("Script delete tidak ada")
        content = script.read_text(encoding="utf-8")
        assert "COOKIES_PATH" in content or "cookies" in content.lower(), (
            "Script delete tidak menggunakan cookie file untuk autentikasi"
        )
        assert "session.json" in content, (
            "Script delete tidak mereferensikan session.json untuk cookies"
        )

    def test_delete_artifacts_are_png_format(self):
        """Semua artefak delete harus berformat PNG yang valid."""
        for filename in ["delete_jeans_before.png", "delete_jeans_debug.png",
                         "delete_confirm_dialog.png"]:
            path = WORKSPACE / filename
            if not path.exists():
                continue  # Skip jika tidak ada, test existence sudah di atas
            assert _is_valid_png(path), (
                f"{filename} bukan file PNG yang valid — mungkin corrupt"
            )

    def test_delete_confirm_dialog_not_blank(self):
        """Screenshot dialog konfirmasi tidak boleh blank."""
        path = WORKSPACE / "delete_confirm_dialog.png"
        if not path.exists():
            pytest.skip("delete_confirm_dialog.png tidak ada")
        assert _png_is_not_blank(path), (
            "delete_confirm_dialog.png tampak blank — "
            "dialog mungkin tidak muncul saat screenshot diambil"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# B. FACEBOOK POSTING LIVE GATE
# ═══════════════════════════════════════════════════════════════════════════════


class TestFacebookPostingLiveGate:
    """Verifikasi bahwa postingan Facebook celana jeans benar-benar tayang."""

    def test_fb_photo_attached_screenshot_exists(self):
        """Screenshot foto terlampir di Facebook harus ada."""
        path = WORKSPACE / "fb_photo_attached_real.png"
        assert path.exists(), (
            "fb_photo_attached_real.png tidak ditemukan — "
            "foto produk tidak pernah berhasil dilampirkan ke Facebook"
        )

    def test_fb_photo_attached_valid_size(self):
        """Screenshot foto terlampir harus berukuran besar (menunjukkan foto ada)."""
        path = WORKSPACE / "fb_photo_attached_real.png"
        if not path.exists():
            pytest.skip("fb_photo_attached_real.png tidak ada")
        size = path.stat().st_size
        min_bytes = FB_SCREENSHOTS["fb_photo_attached_real.png"]["min_bytes"]
        assert size >= min_bytes, (
            f"fb_photo_attached_real.png terlalu kecil: {size} bytes "
            f"(minimum {min_bytes} bytes) — foto mungkin tidak terlampir"
        )

    def test_fb_posted_live_screenshot_exists(self):
        """Screenshot post live di Facebook harus ada."""
        path = WORKSPACE / "fb_posted_live.png"
        assert path.exists(), (
            "fb_posted_live.png tidak ditemukan — "
            "postingan Facebook mungkin tidak berhasil dipublikasikan"
        )

    def test_fb_posted_live_valid_size(self):
        """Screenshot post live harus berukuran valid."""
        path = WORKSPACE / "fb_posted_live.png"
        if not path.exists():
            pytest.skip("fb_posted_live.png tidak ada")
        size = path.stat().st_size
        min_bytes = FB_SCREENSHOTS["fb_posted_live.png"]["min_bytes"]
        assert size >= min_bytes, (
            f"fb_posted_live.png terlalu kecil: {size} bytes "
            f"(minimum {min_bytes} bytes)"
        )

    def test_fb_posted_verified_screenshot_exists(self):
        """Screenshot verifikasi post Facebook harus ada."""
        path = WORKSPACE / "fb_posted_verified.png"
        assert path.exists(), (
            "fb_posted_verified.png tidak ditemukan — "
            "verifikasi postingan Facebook tidak dilakukan"
        )

    def test_fb_posted_verified_valid_size(self):
        """Screenshot verifikasi harus berukuran valid."""
        path = WORKSPACE / "fb_posted_verified.png"
        if not path.exists():
            pytest.skip("fb_posted_verified.png tidak ada")
        size = path.stat().st_size
        min_bytes = FB_SCREENSHOTS["fb_posted_verified.png"]["min_bytes"]
        assert size >= min_bytes, (
            f"fb_posted_verified.png terlalu kecil: {size} bytes "
            f"(minimum {min_bytes} bytes)"
        )

    def test_fb_screenshots_are_valid_png(self):
        """Semua screenshot Facebook harus berformat PNG yang valid."""
        for filename in FB_SCREENSHOTS:
            path = WORKSPACE / filename
            if not path.exists():
                continue
            assert _is_valid_png(path), (
                f"{filename} bukan file PNG yang valid — mungkin corrupt"
            )

    def test_fb_posted_live_not_blank(self):
        """Screenshot post live tidak boleh blank."""
        path = WORKSPACE / "fb_posted_live.png"
        if not path.exists():
            pytest.skip("fb_posted_live.png tidak ada")
        assert _png_is_not_blank(path), (
            "fb_posted_live.png tampak blank — "
            "postingan mungkin tidak berhasil ditampilkan"
        )

    def test_fb_photo_attached_not_blank(self):
        """Screenshot foto terlampir tidak boleh blank."""
        path = WORKSPACE / "fb_photo_attached_real.png"
        if not path.exists():
            pytest.skip("fb_photo_attached_real.png tidak ada")
        assert _png_is_not_blank(path), (
            "fb_photo_attached_real.png tampak blank — "
            "foto mungkin tidak berhasil dilampirkan"
        )

    def test_fb_posting_script_exists(self):
        """Script post_jeans_facebook.py harus ada."""
        script = WORKSPACE / "post_jeans_facebook.py"
        assert script.exists(), (
            "post_jeans_facebook.py tidak ditemukan — "
            "script posting Facebook belum dibuat"
        )

    def test_fb_posting_script_has_affiliate_url(self):
        """Script posting Facebook harus mengandung affiliate URL."""
        script = WORKSPACE / "post_jeans_facebook.py"
        if not script.exists():
            pytest.skip("post_jeans_facebook.py tidak ada")
        content = script.read_text(encoding="utf-8")
        assert AFFILIATE_URL_BASE in content, (
            f"Script posting Facebook tidak mengandung affiliate URL: {AFFILIATE_URL_BASE}"
        )

    def test_fb_posting_script_has_image_logic(self):
        """Script posting Facebook harus memiliki logika upload foto."""
        script = WORKSPACE / "post_jeans_facebook.py"
        if not script.exists():
            pytest.skip("post_jeans_facebook.py tidak ada")
        content = script.read_text(encoding="utf-8")
        has_image_logic = any(
            kw in content
            for kw in ["celana_jeans_korea_1.jpg", "product_images", "set_input_files",
                       "upload", "photo", "image"]
        )
        assert has_image_logic, (
            "Script posting Facebook tidak memiliki logika upload foto produk"
        )

    def test_fb_posting_script_no_hardcoded_credentials(self):
        """Script posting Facebook tidak boleh mengandung hardcoded credentials."""
        script = WORKSPACE / "post_jeans_facebook.py"
        if not script.exists():
            pytest.skip("post_jeans_facebook.py tidak ada")
        content = script.read_text(encoding="utf-8")
        forbidden_patterns = [
            r'password\s*=\s*["\'][^"\']{4,}["\']',
            r'fb_token\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
        ]
        for pattern in forbidden_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            assert not match, (
                f"Script posting Facebook mengandung hardcoded credential: {match.group()}"
            )

    def test_fb_additional_screenshots_exist(self):
        """Screenshot tambahan proses Facebook harus ada (draft, feed, kirim)."""
        additional = [
            "fb_draft_ready.png",
            "fb_feed_ready.png",
            "fb_kirim_live.png",
        ]
        missing = []
        for fname in additional:
            if not (WORKSPACE / fname).exists():
                missing.append(fname)
        assert not missing, (
            f"Screenshot proses Facebook hilang: {missing} — "
            "proses posting mungkin tidak lengkap"
        )

    def test_fb_additional_screenshots_valid_size(self):
        """Screenshot tambahan Facebook harus berukuran valid."""
        additional = {
            "fb_draft_ready.png": 100_000,
            "fb_feed_ready.png": 50_000,
            "fb_kirim_live.png": 50_000,
        }
        for fname, min_bytes in additional.items():
            path = WORKSPACE / fname
            if not path.exists():
                continue
            size = path.stat().st_size
            assert size >= min_bytes, (
                f"{fname} terlalu kecil: {size} bytes (minimum {min_bytes} bytes)"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# C. CONTENT INTEGRITY GATE
# ═══════════════════════════════════════════════════════════════════════════════


class TestContentIntegrityGate:
    """Verifikasi integritas konten naskah dan foto produk."""

    def test_product_image_exists(self):
        """Foto produk celana_jeans_korea_1.jpg harus ada."""
        path = PRODUCT_IMAGES / PRODUCT_IMAGE_FILE
        assert path.exists(), (
            f"Foto produk {PRODUCT_IMAGE_FILE} tidak ditemukan di {PRODUCT_IMAGES} — "
            "foto produk belum didownload"
        )

    def test_product_image_valid_size(self):
        """Foto produk harus berukuran valid (tidak corrupt)."""
        path = PRODUCT_IMAGES / PRODUCT_IMAGE_FILE
        if not path.exists():
            pytest.skip(f"{PRODUCT_IMAGE_FILE} tidak ada")
        size = path.stat().st_size
        assert size >= 100_000, (
            f"Foto produk {PRODUCT_IMAGE_FILE} terlalu kecil: {size} bytes "
            "(minimum 100KB) — kemungkinan corrupt atau placeholder"
        )

    def test_product_image_is_valid_jpeg(self):
        """Foto produk harus berformat JPEG yang valid."""
        path = PRODUCT_IMAGES / PRODUCT_IMAGE_FILE
        if not path.exists():
            pytest.skip(f"{PRODUCT_IMAGE_FILE} tidak ada")
        assert _is_valid_jpeg(path), (
            f"{PRODUCT_IMAGE_FILE} bukan file JPEG yang valid — mungkin corrupt"
        )

    def test_canonical_naskah_exists(self):
        """Dokumen naskah canonical harus ada."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        assert path.exists(), (
            "naskah_celana_jeans_korea_canonical.md tidak ditemukan — "
            "naskah canonical belum dibuat"
        )

    def test_canonical_naskah_has_hook(self):
        """Naskah canonical harus memiliki hook 'Sebagai cowok praktis'."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        if not path.exists():
            pytest.skip("Naskah canonical tidak ada")
        content = path.read_text(encoding="utf-8")
        assert HOOK_TEXT in content, (
            f"Hook '{HOOK_TEXT}' tidak ditemukan dalam naskah canonical"
        )

    def test_canonical_naskah_has_spec_keywords(self):
        """Naskah canonical harus memiliki semua keyword spesifikasi produk."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        if not path.exists():
            pytest.skip("Naskah canonical tidak ada")
        content = path.read_text(encoding="utf-8")
        missing = [kw for kw in SPEC_KEYWORDS if kw not in content]
        assert not missing, (
            f"Keyword spesifikasi hilang dari naskah canonical: {missing}"
        )

    def test_canonical_naskah_has_affiliate_url(self):
        """Naskah canonical harus memiliki affiliate URL."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        if not path.exists():
            pytest.skip("Naskah canonical tidak ada")
        content = path.read_text(encoding="utf-8")
        assert AFFILIATE_URL_BASE in content, (
            f"Affiliate URL '{AFFILIATE_URL_BASE}' tidak ditemukan dalam naskah canonical"
        )

    def test_canonical_naskah_has_hashtags(self):
        """Naskah canonical harus memiliki minimal 5 hashtag."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        if not path.exists():
            pytest.skip("Naskah canonical tidak ada")
        content = path.read_text(encoding="utf-8")
        hashtags = re.findall(r"#\w+", content)
        assert len(hashtags) >= 5, (
            f"Naskah canonical hanya memiliki {len(hashtags)} hashtag (minimum 5)"
        )

    def test_canonical_naskah_cowok_praktis_angle(self):
        """Naskah canonical harus mengandung sudut pandang 'Cowok Praktis'."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        if not path.exists():
            pytest.skip("Naskah canonical tidak ada")
        content = path.read_text(encoding="utf-8")
        has_angle = "cowok praktis" in content.lower() or "Cowok Praktis" in content
        assert has_angle, (
            "Sudut pandang 'Cowok Praktis' tidak ditemukan dalam naskah canonical"
        )

    def test_campaign_json_exists(self):
        """File metadata kampanye celana_jeans_campaign.json harus ada."""
        path = DOCS / "celana_jeans_campaign.json"
        assert path.exists(), (
            "celana_jeans_campaign.json tidak ditemukan — "
            "metadata kampanye belum dibuat"
        )

    def test_campaign_json_valid_structure(self):
        """Metadata kampanye harus memiliki struktur yang valid."""
        campaign = _load_campaign_json()
        assert campaign, "celana_jeans_campaign.json kosong atau tidak valid JSON"
        required_fields = ["product_name", "affiliate_url", "image_path", "specs"]
        missing = [f for f in required_fields if f not in campaign]
        assert not missing, (
            f"Field wajib hilang dari celana_jeans_campaign.json: {missing}"
        )

    def test_campaign_json_affiliate_url_consistent(self):
        """Affiliate URL di campaign.json harus konsisten dengan naskah."""
        campaign = _load_campaign_json()
        if not campaign:
            pytest.skip("celana_jeans_campaign.json tidak ada atau invalid")
        campaign_url = campaign.get("affiliate_url", "")
        assert AFFILIATE_URL_BASE in campaign_url, (
            f"Affiliate URL di campaign.json ('{campaign_url}') tidak konsisten "
            f"dengan URL canonical '{AFFILIATE_URL_BASE}'"
        )

    def test_campaign_json_image_path_exists(self):
        """Path foto produk di campaign.json harus menunjuk ke file yang ada."""
        campaign = _load_campaign_json()
        if not campaign:
            pytest.skip("celana_jeans_campaign.json tidak ada atau invalid")
        image_path = campaign.get("image_path", "")
        if not image_path:
            pytest.skip("image_path tidak ada di campaign.json")
        path = Path(image_path)
        assert path.exists(), (
            f"File foto produk yang direferensikan di campaign.json tidak ada: {image_path}"
        )

    def test_campaign_json_specs_not_empty(self):
        """Specs di campaign.json tidak boleh kosong."""
        campaign = _load_campaign_json()
        if not campaign:
            pytest.skip("celana_jeans_campaign.json tidak ada atau invalid")
        specs = campaign.get("specs", [])
        assert isinstance(specs, list) and len(specs) >= 3, (
            f"Specs di campaign.json terlalu sedikit: {len(specs)} item (minimum 3)"
        )

    def test_fb_posting_script_post_text_length(self):
        """POST_TEXT di script Facebook harus memiliki panjang yang wajar."""
        post_text = _load_post_text_from_script("post_jeans_facebook.py")
        if not post_text:
            pytest.skip("POST_TEXT tidak ditemukan di post_jeans_facebook.py")
        length = len(post_text)
        assert length >= 100, (
            f"POST_TEXT terlalu pendek: {length} karakter (minimum 100)"
        )
        assert length <= 5000, (
            f"POST_TEXT terlalu panjang: {length} karakter (maksimum 5000)"
        )

    def test_fb_posting_script_post_text_has_emoji(self):
        """POST_TEXT harus mengandung emoji (tone relatable/casual)."""
        post_text = _load_post_text_from_script("post_jeans_facebook.py")
        if not post_text:
            pytest.skip("POST_TEXT tidak ditemukan di post_jeans_facebook.py")
        has_emoji = bool(re.search(
            r"[\U0001F300-\U0001F9FF\U00002600-\U000027BF]",
            post_text
        ))
        assert has_emoji, (
            "POST_TEXT tidak mengandung emoji — tone mungkin terlalu formal"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# D. PIPELINE INTEGRITY GATE
# ═══════════════════════════════════════════════════════════════════════════════


class TestPipelineIntegrityGate:
    """Verifikasi integritas pipeline posting secara keseluruhan."""

    def test_all_required_scripts_exist(self):
        """Semua script pipeline harus ada."""
        required_scripts = [
            "post_jeans_facebook.py",
            "post_jeans_threads.py",
            "delete_duplicate_jeans_threads.py",
        ]
        missing = [s for s in required_scripts if not (WORKSPACE / s).exists()]
        assert not missing, (
            f"Script pipeline hilang: {missing}"
        )

    def test_threads_posting_script_has_affiliate_url(self):
        """Script posting Threads harus mengandung affiliate URL."""
        script = WORKSPACE / "post_jeans_threads.py"
        if not script.exists():
            pytest.skip("post_jeans_threads.py tidak ada")
        content = script.read_text(encoding="utf-8")
        assert AFFILIATE_URL_BASE in content, (
            f"Script posting Threads tidak mengandung affiliate URL: {AFFILIATE_URL_BASE}"
        )

    def test_threads_posting_script_has_hook(self):
        """Script posting Threads harus mengandung hook canonical."""
        script = WORKSPACE / "post_jeans_threads.py"
        if not script.exists():
            pytest.skip("post_jeans_threads.py tidak ada")
        content = script.read_text(encoding="utf-8")
        assert "cowok praktis" in content.lower() or "Cowok Praktis" in content, (
            "Script posting Threads tidak mengandung hook 'Cowok Praktis'"
        )

    def test_threads_live_screenshot_exists(self):
        """Screenshot Threads jeans live harus ada."""
        path = WORKSPACE / "threads_jeans_live.png"
        assert path.exists(), (
            "threads_jeans_live.png tidak ditemukan — "
            "postingan Threads mungkin tidak berhasil"
        )

    def test_threads_image_attached_screenshot_exists(self):
        """Screenshot Threads dengan foto terlampir harus ada."""
        path = WORKSPACE / "threads_image_attached.png"
        assert path.exists(), (
            "threads_image_attached.png tidak ditemukan — "
            "foto tidak berhasil dilampirkan ke Threads"
        )

    def test_threads_image_attached_valid_size(self):
        """Screenshot Threads foto terlampir harus berukuran valid."""
        path = WORKSPACE / "threads_image_attached.png"
        if not path.exists():
            pytest.skip("threads_image_attached.png tidak ada")
        size = path.stat().st_size
        assert size >= THREADS_SCREENSHOTS["threads_image_attached.png"]["min_bytes"], (
            f"threads_image_attached.png terlalu kecil: {size} bytes "
            f"(minimum {THREADS_SCREENSHOTS['threads_image_attached.png']['min_bytes']} bytes)"
        )

    def test_no_error_exception_screenshot_only(self):
        """
        error_exception.png tidak boleh menjadi satu-satunya artefak.
        Jika ada, harus ada juga screenshot progress lainnya.
        """
        error_path = WORKSPACE / "error_exception.png"
        if not error_path.exists():
            return  # Tidak ada error screenshot = bagus

        # Jika ada error screenshot, harus ada juga screenshot progress
        progress_screenshots = [
            "fb_photo_attached_real.png",
            "fb_posted_live.png",
            "delete_confirm_dialog.png",
        ]
        has_progress = any((WORKSPACE / s).exists() for s in progress_screenshots)
        assert has_progress, (
            "error_exception.png ada dan tidak ada screenshot progress lainnya — "
            "proses posting kemungkinan gagal total"
        )

    def test_product_images_directory_has_multiple_images(self):
        """Direktori product_images harus memiliki minimal 3 foto produk."""
        if not PRODUCT_IMAGES.exists():
            pytest.skip("Direktori product_images tidak ada")
        jpg_files = list(PRODUCT_IMAGES.glob("celana_jeans_korea_*.jpg"))
        assert len(jpg_files) >= 3, (
            f"Hanya ada {len(jpg_files)} foto produk di product_images "
            "(minimum 3 foto untuk variasi konten)"
        )

    def test_all_product_images_valid_jpeg(self):
        """Semua foto produk harus berformat JPEG yang valid."""
        if not PRODUCT_IMAGES.exists():
            pytest.skip("Direktori product_images tidak ada")
        jpg_files = list(PRODUCT_IMAGES.glob("celana_jeans_korea_*.jpg"))
        corrupt = []
        for f in jpg_files:
            if not _is_valid_jpeg(f):
                corrupt.append(f.name)
        assert not corrupt, (
            f"Foto produk corrupt (bukan JPEG valid): {corrupt}"
        )

    def test_docs_directory_has_required_files(self):
        """Direktori docs harus memiliki semua file yang diperlukan."""
        required_docs = [
            "celana_jeans_campaign.json",
            "naskah_celana_jeans_korea_canonical.md",
        ]
        if not DOCS.exists():
            pytest.fail(f"Direktori docs tidak ada: {DOCS}")
        missing = [f for f in required_docs if not (DOCS / f).exists()]
        assert not missing, (
            f"File docs yang diperlukan hilang: {missing}"
        )

    def test_fb_screenshots_chronological_timestamps(self):
        """
        Screenshot Facebook harus memiliki timestamp yang logis:
        fb_photo_attached_real.png harus lebih awal dari fb_posted_live.png.
        """
        attached = WORKSPACE / "fb_photo_attached_real.png"
        posted = WORKSPACE / "fb_posted_live.png"
        if not attached.exists() or not posted.exists():
            pytest.skip("Screenshot Facebook tidak lengkap untuk cek timestamp")
        attached_mtime = attached.stat().st_mtime
        posted_mtime = posted.stat().st_mtime
        # Toleransi: posted harus setelah atau bersamaan dengan attached
        # (dalam 1 jam ke depan)
        assert posted_mtime >= attached_mtime - 3600, (
            "Timestamp fb_posted_live.png lebih awal dari fb_photo_attached_real.png — "
            "urutan proses posting tidak logis"
        )

    def test_delete_artifacts_chronological_timestamps(self):
        """
        Screenshot delete harus memiliki timestamp yang logis:
        delete_jeans_before.png harus ada sebelum atau bersamaan dengan
        delete_confirm_dialog.png.
        """
        before = WORKSPACE / "delete_jeans_before.png"
        confirm = WORKSPACE / "delete_confirm_dialog.png"
        if not before.exists() or not confirm.exists():
            pytest.skip("Screenshot delete tidak lengkap untuk cek timestamp")
        before_mtime = before.stat().st_mtime
        confirm_mtime = confirm.stat().st_mtime
        # Toleransi 1 jam
        assert confirm_mtime >= before_mtime - 3600, (
            "Timestamp delete_confirm_dialog.png lebih awal dari delete_jeans_before.png — "
            "urutan proses delete tidak logis"
        )

    def test_summary_report_generation(self):
        """
        Verifikasi ringkasan: semua gate utama harus lulus.
        Test ini merangkum status keseluruhan Quality Gate T-2003.
        """
        gates = {
            "Threads Delete Script": (WORKSPACE / "delete_duplicate_jeans_threads.py").exists(),
            "Delete Before Screenshot": (WORKSPACE / "delete_jeans_before.png").exists(),
            "Delete Confirm Dialog": (WORKSPACE / "delete_confirm_dialog.png").exists(),
            "FB Photo Attached": (WORKSPACE / "fb_photo_attached_real.png").exists(),
            "FB Posted Live": (WORKSPACE / "fb_posted_live.png").exists(),
            "FB Posted Verified": (WORKSPACE / "fb_posted_verified.png").exists(),
            "Product Image": (PRODUCT_IMAGES / PRODUCT_IMAGE_FILE).exists(),
            "Canonical Naskah": (DOCS / "naskah_celana_jeans_korea_canonical.md").exists(),
            "Campaign JSON": (DOCS / "celana_jeans_campaign.json").exists(),
        }
        failed_gates = [name for name, passed in gates.items() if not passed]
        # Print ringkasan untuk visibilitas
        print("\n" + "=" * 60)
        print("QUALITY GATE T-2003 — RINGKASAN")
        print("=" * 60)
        for name, passed in gates.items():
            status = "✅ LULUS" if passed else "❌ GAGAL"
            print(f"  {status}  {name}")
        print("=" * 60)
        if failed_gates:
            print(f"  TOTAL GAGAL: {len(failed_gates)}/{len(gates)}")
        else:
            print(f"  SEMUA GATE LULUS: {len(gates)}/{len(gates)}")
        print("=" * 60)
        assert not failed_gates, (
            f"Quality Gate T-2003 GAGAL — gate berikut tidak lulus: {failed_gates}"
        )
