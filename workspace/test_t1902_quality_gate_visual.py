"""
Quality Gate & Visual Verification — T-1902
============================================
Memastikan foto celana jeans dan naskah Cowok Praktis benar-benar tampil
utuh di screenshot live tanpa error.

Scope verifikasi:
  1. Screenshot artefak ada dan berukuran valid (tidak blank/corrupt)
  2. Foto produk celana_jeans_korea_1.jpg tersedia dan tidak corrupt
  3. Naskah canonical T-1801 lengkap (hook + spek + affiliate URL)
  4. Tidak ada error screenshot (error_exception.png tidak boleh menjadi
     satu-satunya artefak; debug shots harus menunjukkan progress)
  5. Integritas pixel: screenshot tidak sepenuhnya hitam/putih (blank)
  6. Metadata kampanye (celana_jeans_campaign.json) valid dan konsisten
     dengan naskah yang diposting
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

# Screenshot artefak dari T-1901 (Facebook posting execution)
FB_SCREENSHOTS = {
    "fb_photo_attached_real.png": {"min_bytes": 200_000, "label": "FB foto terlampir"},
    "fb_posted_live.png": {"min_bytes": 100_000, "label": "FB post live"},
    "fb_posted_verified.png": {"min_bytes": 100_000, "label": "FB post terverifikasi"},
}

# Screenshot artefak dari Threads posting (T-1803 / Sprint 18)
THREADS_SCREENSHOTS = {
    "threads_image_attached.png": {"min_bytes": 100_000, "label": "Threads foto terlampir"},
    "threads_jeans_live.png": {"min_bytes": 10_000, "label": "Threads jeans live"},
}

# Naskah canonical T-1801 (dari post_jeans_facebook.py & post_jeans_threads.py)
HOOK_TEXT = "Sebagai cowok praktis"
SPEC_KEYWORDS = [
    "Loose-fit",
    "Denim",
    "karet fleksibel",
    "4 saku",
]
AFFILIATE_URL = "https://s.shopee.co.id/4LJqTkz7w7"
PRODUCT_IMAGE_FILE = "celana_jeans_korea_1.jpg"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _png_dimensions(path: Path) -> tuple[int, int]:
    """Baca dimensi PNG dari header IHDR tanpa library eksternal."""
    with open(path, "rb") as f:
        sig = f.read(8)
        assert sig == b"\x89PNG\r\n\x1a\n", f"Bukan file PNG valid: {path.name}"
        f.read(4)  # chunk length
        chunk_type = f.read(4)
        assert chunk_type == b"IHDR", f"Chunk pertama bukan IHDR: {path.name}"
        width = struct.unpack(">I", f.read(4))[0]
        height = struct.unpack(">I", f.read(4))[0]
    return width, height


def _is_blank_image(path: Path, threshold: float = 0.98) -> bool:
    """
    Deteksi apakah gambar blank (semua piksel hampir seragam).
    Menggunakan analisis entropi sederhana via zlib compression ratio.
    Gambar blank memiliki rasio kompresi sangat tinggi (>95%).
    """
    raw = path.read_bytes()
    compressed = zlib.compress(raw)
    ratio = 1 - (len(compressed) / len(raw))
    return ratio > threshold


def _load_post_text() -> str:
    """Baca POST_TEXT dari post_jeans_facebook.py secara dinamis."""
    script = (WORKSPACE / "post_jeans_facebook.py").read_text(encoding="utf-8")
    # Ekstrak string POST_TEXT dari source code
    match = re.search(r'POST_TEXT\s*=\s*\((.*?)\)\s*\n\n', script, re.DOTALL)
    if not match:
        return ""
    raw = match.group(1)
    # Gabungkan string literal Python
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', raw)
    return "".join(parts).replace("\\n", "\n").replace("\\\\", "\\")


# ─── Test Classes ─────────────────────────────────────────────────────────────

class TestScreenshotArtifacts:
    """Verifikasi keberadaan dan integritas screenshot artefak live posting."""

    @pytest.mark.parametrize("filename,meta", list(FB_SCREENSHOTS.items()))
    def test_fb_screenshot_exists_and_not_empty(self, filename: str, meta: dict):
        """Screenshot Facebook harus ada dan berukuran di atas minimum."""
        path = WORKSPACE / filename
        assert path.exists(), (
            f"[{meta['label']}] Screenshot tidak ditemukan: {filename}\n"
            f"  → Pastikan T-1901 (eksekusi posting Facebook) sudah selesai."
        )
        size = path.stat().st_size
        assert size >= meta["min_bytes"], (
            f"[{meta['label']}] File terlalu kecil: {size} bytes "
            f"(minimum {meta['min_bytes']} bytes)\n"
            f"  → Kemungkinan screenshot blank atau corrupt."
        )

    @pytest.mark.parametrize("filename,meta", list(THREADS_SCREENSHOTS.items()))
    def test_threads_screenshot_exists_and_not_empty(self, filename: str, meta: dict):
        """Screenshot Threads harus ada dan berukuran di atas minimum."""
        path = WORKSPACE / filename
        assert path.exists(), (
            f"[{meta['label']}] Screenshot tidak ditemukan: {filename}"
        )
        size = path.stat().st_size
        assert size >= meta["min_bytes"], (
            f"[{meta['label']}] File terlalu kecil: {size} bytes "
            f"(minimum {meta['min_bytes']} bytes)"
        )

    @pytest.mark.parametrize("filename", list(FB_SCREENSHOTS.keys()) + list(THREADS_SCREENSHOTS.keys()))
    def test_screenshot_is_valid_png(self, filename: str):
        """Setiap screenshot harus merupakan file PNG yang valid."""
        path = WORKSPACE / filename
        if not path.exists():
            pytest.skip(f"File tidak ada: {filename}")
        raw = path.read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n", (
            f"{filename} bukan file PNG valid (magic bytes salah)"
        )

    @pytest.mark.parametrize("filename", list(FB_SCREENSHOTS.keys()) + list(THREADS_SCREENSHOTS.keys()))
    def test_screenshot_has_reasonable_dimensions(self, filename: str):
        """Screenshot harus memiliki dimensi yang masuk akal (≥ 800×600)."""
        path = WORKSPACE / filename
        if not path.exists():
            pytest.skip(f"File tidak ada: {filename}")
        width, height = _png_dimensions(path)
        assert width >= 800, (
            f"{filename}: lebar {width}px terlalu kecil (min 800px)"
        )
        assert height >= 600, (
            f"{filename}: tinggi {height}px terlalu kecil (min 600px)"
        )

    def test_fb_photo_attached_is_largest_screenshot(self):
        """
        fb_photo_attached_real.png harus menjadi screenshot terbesar di antara
        artefak FB — menandakan foto produk berhasil terlampir (lebih banyak data).
        """
        photo_path = WORKSPACE / "fb_photo_attached_real.png"
        if not photo_path.exists():
            pytest.skip("fb_photo_attached_real.png tidak ada")
        photo_size = photo_path.stat().st_size
        # Harus lebih besar dari fb_posted_verified.png (yang hanya teks)
        verified_path = WORKSPACE / "fb_posted_verified.png"
        if verified_path.exists():
            verified_size = verified_path.stat().st_size
            assert photo_size > verified_size, (
                f"fb_photo_attached_real.png ({photo_size} bytes) seharusnya lebih besar "
                f"dari fb_posted_verified.png ({verified_size} bytes) karena mengandung foto produk"
            )


class TestProductImageIntegrity:
    """Verifikasi foto produk celana jeans tersedia dan tidak corrupt."""

    def test_product_image_exists(self):
        """Foto produk utama harus ada di product_images/."""
        path = PRODUCT_IMAGES / PRODUCT_IMAGE_FILE
        assert path.exists(), (
            f"Foto produk tidak ditemukan: {path}\n"
            f"  → Pastikan pipeline download gambar (Sprint 16) sudah dijalankan."
        )

    def test_product_image_is_valid_jpeg(self):
        """Foto produk harus merupakan file JPEG yang valid."""
        path = PRODUCT_IMAGES / PRODUCT_IMAGE_FILE
        if not path.exists():
            pytest.skip("Foto produk tidak ada")
        raw = path.read_bytes()
        # JPEG magic: FF D8 FF
        assert raw[:3] == b"\xff\xd8\xff", (
            f"{PRODUCT_IMAGE_FILE} bukan file JPEG valid (magic bytes: {raw[:3].hex()})"
        )
        # JPEG harus diakhiri dengan FF D9
        assert raw[-2:] == b"\xff\xd9", (
            f"{PRODUCT_IMAGE_FILE} tidak diakhiri dengan JPEG EOI marker (FF D9) — "
            f"file mungkin corrupt atau terpotong"
        )

    def test_product_image_minimum_size(self):
        """Foto produk harus berukuran minimal 100KB (bukan thumbnail)."""
        path = PRODUCT_IMAGES / PRODUCT_IMAGE_FILE
        if not path.exists():
            pytest.skip("Foto produk tidak ada")
        size = path.stat().st_size
        assert size >= 100_000, (
            f"Foto produk terlalu kecil: {size} bytes (minimum 100KB)\n"
            f"  → Kemungkinan thumbnail atau file corrupt."
        )

    def test_all_product_images_available(self):
        """Semua 5 foto produk celana jeans harus tersedia."""
        expected = [f"celana_jeans_korea_{i}.jpg" for i in range(1, 6)]
        missing = [f for f in expected if not (PRODUCT_IMAGES / f).exists()]
        assert missing == [], (
            f"Foto produk berikut tidak ditemukan: {missing}"
        )


class TestNaskahCanonical:
    """Verifikasi naskah Cowok Praktis T-1801 lengkap dan konsisten."""

    def test_post_text_contains_hook(self):
        """POST_TEXT harus mengandung hook 'Sebagai cowok praktis'."""
        post_text = _load_post_text()
        assert HOOK_TEXT in post_text, (
            f"Hook tidak ditemukan dalam POST_TEXT.\n"
            f"  Expected: '{HOOK_TEXT}'\n"
            f"  Actual (first 200 chars): {post_text[:200]!r}"
        )

    @pytest.mark.parametrize("keyword", SPEC_KEYWORDS)
    def test_post_text_contains_spec_keyword(self, keyword: str):
        """POST_TEXT harus mengandung semua keyword spek produk."""
        post_text = _load_post_text()
        assert keyword in post_text, (
            f"Keyword spek '{keyword}' tidak ditemukan dalam POST_TEXT"
        )

    def test_post_text_contains_affiliate_url(self):
        """POST_TEXT harus mengandung affiliate URL Shopee yang valid."""
        post_text = _load_post_text()
        assert AFFILIATE_URL in post_text, (
            f"Affiliate URL tidak ditemukan dalam POST_TEXT.\n"
            f"  Expected: {AFFILIATE_URL}"
        )

    def test_post_text_no_false_claims(self):
        """POST_TEXT tidak boleh mengandung klaim kepemilikan palsu."""
        post_text = _load_post_text().lower()
        false_claim_patterns = [
            r"\baku udah pake\b",
            r"\bsaya udah pake\b",
            r"\baku pakai\b",
            r"\bsaya pakai\b",
            r"\baku beli\b",
            r"\bsaya beli\b",
            r"\baku cobain\b",
            r"\bsaya cobain\b",
            r"\bpunya aku\b",
            r"\bpunya saya\b",
        ]
        found = [p for p in false_claim_patterns if re.search(p, post_text)]
        assert found == [], (
            f"POST_TEXT mengandung klaim kepemilikan palsu: {found}"
        )

    def test_post_text_no_spam_triggers(self):
        """POST_TEXT tidak boleh mengandung spam trigger words."""
        post_text = _load_post_text().lower()
        spam_triggers = [
            "diskon gila",
            "promo termurah",
            "harga gila",
            "murah banget",
            "gratis ongkir",
            "flash sale",
            "limited stock",
        ]
        found = [t for t in spam_triggers if t in post_text]
        assert found == [], (
            f"POST_TEXT mengandung spam trigger words: {found}"
        )

    def test_post_text_no_raw_html(self):
        """POST_TEXT tidak boleh mengandung raw HTML tags."""
        post_text = _load_post_text()
        has_html = bool(re.search(r"<[a-zA-Z][^>]*>", post_text))
        assert not has_html, "POST_TEXT mengandung raw HTML tags"

    def test_post_text_no_markdown_formatting(self):
        """POST_TEXT tidak boleh mengandung Markdown formatting."""
        post_text = _load_post_text()
        has_bold = bool(re.search(r"\*\*[^*]+\*\*", post_text))
        has_italic = bool(re.search(r"\*[^*]+\*", post_text))
        has_heading = bool(re.search(r"^#{1,6} ", post_text, re.MULTILINE))
        assert not has_bold, "POST_TEXT mengandung Markdown **bold**"
        assert not has_italic, "POST_TEXT mengandung Markdown *italic*"
        assert not has_heading, "POST_TEXT mengandung Markdown # heading"

    def test_canonical_naskah_doc_exists(self):
        """Dokumen naskah canonical harus ada di docs/."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        assert path.exists(), (
            f"Dokumen naskah canonical tidak ditemukan: {path}"
        )

    def test_canonical_naskah_contains_compliance_checklist(self):
        """Dokumen naskah canonical harus memiliki compliance checklist."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        if not path.exists():
            pytest.skip("Dokumen naskah canonical tidak ada")
        content = path.read_text(encoding="utf-8")
        assert "Compliance Checklist" in content, (
            "Dokumen naskah canonical tidak memiliki Compliance Checklist"
        )
        # Semua checklist item harus LULUS (ditandai [x])
        checklist_items = re.findall(r"- \[(.)\]", content)
        unchecked = [i for i, v in enumerate(checklist_items) if v != "x"]
        assert unchecked == [], (
            f"Ada {len(unchecked)} checklist item yang belum dicentang (index: {unchecked})"
        )


class TestCampaignMetadata:
    """Verifikasi metadata kampanye konsisten dengan naskah yang diposting."""

    def test_campaign_json_exists(self):
        """celana_jeans_campaign.json harus ada di docs/."""
        path = DOCS / "celana_jeans_campaign.json"
        assert path.exists(), (
            f"Campaign JSON tidak ditemukan: {path}"
        )

    def test_campaign_json_valid_and_complete(self):
        """Campaign JSON harus valid dan memiliki semua field wajib."""
        path = DOCS / "celana_jeans_campaign.json"
        if not path.exists():
            pytest.skip("Campaign JSON tidak ada")
        data = json.loads(path.read_text(encoding="utf-8"))
        required_fields = ["product_name", "affiliate_url", "image_path", "specs"]
        missing = [f for f in required_fields if f not in data]
        assert missing == [], f"Campaign JSON kekurangan field: {missing}"
        assert isinstance(data["specs"], list), "Field 'specs' harus bertipe list"
        assert len(data["specs"]) >= 3, (
            f"Field 'specs' harus memiliki minimal 3 item, "
            f"ditemukan: {len(data['specs'])}"
        )

    def test_campaign_json_affiliate_url_matches_post(self):
        """Affiliate URL di campaign JSON harus sama dengan yang ada di POST_TEXT."""
        path = DOCS / "celana_jeans_campaign.json"
        if not path.exists():
            pytest.skip("Campaign JSON tidak ada")
        data = json.loads(path.read_text(encoding="utf-8"))
        post_text = _load_post_text()
        campaign_url = data.get("affiliate_url", "")
        # Ekstrak base URL (tanpa query params) untuk perbandingan
        base_campaign = campaign_url.split("?")[0]
        assert base_campaign in post_text, (
            f"Affiliate URL di campaign JSON ({base_campaign}) tidak ditemukan "
            f"dalam POST_TEXT"
        )

    def test_campaign_json_image_path_exists(self):
        """Path gambar di campaign JSON harus menunjuk ke file yang ada."""
        path = DOCS / "celana_jeans_campaign.json"
        if not path.exists():
            pytest.skip("Campaign JSON tidak ada")
        data = json.loads(path.read_text(encoding="utf-8"))
        image_path = Path(data.get("image_path", ""))
        assert image_path.exists(), (
            f"Gambar yang direferensikan di campaign JSON tidak ditemukan: {image_path}"
        )


class TestDebugScreenshotProgress:
    """
    Verifikasi debug screenshots menunjukkan progress posting yang valid
    (bukan hanya error screenshot).
    """

    DEBUG_DIR = Path("/tmp/fb_jeans_debug")

    def test_debug_dir_exists(self):
        """Debug directory harus ada (menandakan script pernah dijalankan)."""
        assert self.DEBUG_DIR.exists(), (
            f"Debug directory tidak ditemukan: {self.DEBUG_DIR}\n"
            f"  → Pastikan post_jeans_facebook.py sudah dijalankan."
        )

    def test_debug_has_initial_screenshots(self):
        """Debug directory harus memiliki screenshot awal (01_fb_home.png)."""
        if not self.DEBUG_DIR.exists():
            pytest.skip("Debug directory tidak ada")
        initial = self.DEBUG_DIR / "01_fb_home.png"
        assert initial.exists(), (
            "01_fb_home.png tidak ditemukan — script mungkin gagal sebelum membuka Facebook"
        )
        size = initial.stat().st_size
        assert size >= 100_000, (
            f"01_fb_home.png terlalu kecil ({size} bytes) — kemungkinan halaman tidak termuat"
        )

    def test_debug_fb_home_is_valid_png(self):
        """01_fb_home.png harus merupakan PNG yang valid."""
        if not self.DEBUG_DIR.exists():
            pytest.skip("Debug directory tidak ada")
        path = self.DEBUG_DIR / "01_fb_home.png"
        if not path.exists():
            pytest.skip("01_fb_home.png tidak ada")
        raw = path.read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n", "01_fb_home.png bukan PNG valid"

    def test_debug_progress_beyond_home(self):
        """
        Harus ada lebih dari satu debug screenshot — menandakan script
        berhasil melewati halaman home Facebook.
        """
        if not self.DEBUG_DIR.exists():
            pytest.skip("Debug directory tidak ada")
        debug_pngs = list(self.DEBUG_DIR.glob("*.png"))
        assert len(debug_pngs) >= 2, (
            f"Hanya {len(debug_pngs)} debug screenshot ditemukan — "
            f"script mungkin gagal sangat awal"
        )


class TestNaskahCompleteness:
    """Verifikasi kelengkapan naskah Cowok Praktis secara end-to-end."""

    def test_naskah_has_all_required_sections(self):
        """Naskah canonical harus memiliki semua seksi yang diperlukan."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        if not path.exists():
            pytest.skip("Dokumen naskah canonical tidak ada")
        content = path.read_text(encoding="utf-8")
        required_sections = [
            "Post 1",
            "Post 2",
            "Hashtag",
            "Compliance Checklist",
        ]
        missing = [s for s in required_sections if s not in content]
        assert missing == [], (
            f"Naskah canonical kekurangan seksi: {missing}"
        )

    def test_naskah_has_affiliate_url(self):
        """Naskah canonical harus mengandung affiliate URL."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        if not path.exists():
            pytest.skip("Dokumen naskah canonical tidak ada")
        content = path.read_text(encoding="utf-8")
        assert AFFILIATE_URL in content, (
            f"Affiliate URL tidak ditemukan dalam naskah canonical: {AFFILIATE_URL}"
        )

    def test_naskah_has_hashtags(self):
        """Naskah canonical harus memiliki minimal 5 hashtag."""
        path = DOCS / "naskah_celana_jeans_korea_canonical.md"
        if not path.exists():
            pytest.skip("Dokumen naskah canonical tidak ada")
        content = path.read_text(encoding="utf-8")
        hashtags = re.findall(r"#\w+", content)
        assert len(hashtags) >= 5, (
            f"Naskah canonical hanya memiliki {len(hashtags)} hashtag (minimum 5)"
        )

    def test_post_text_length_reasonable(self):
        """POST_TEXT harus memiliki panjang yang wajar (100–2000 karakter)."""
        post_text = _load_post_text()
        length = len(post_text)
        assert length >= 100, (
            f"POST_TEXT terlalu pendek: {length} karakter (minimum 100)"
        )
        assert length <= 2000, (
            f"POST_TEXT terlalu panjang: {length} karakter (maksimum 2000)"
        )

    def test_post_text_contains_emoji(self):
        """POST_TEXT harus mengandung emoji (menandakan tone relatable/casual)."""
        post_text = _load_post_text()
        # Deteksi emoji via Unicode range
        has_emoji = bool(re.search(
            r"[\U0001F300-\U0001F9FF\U00002600-\U000027BF]",
            post_text
        ))
        assert has_emoji, (
            "POST_TEXT tidak mengandung emoji — tone mungkin terlalu formal untuk platform sosial"
        )

    def test_cowok_praktis_angle_present(self):
        """Sudut pandang 'Cowok Praktis' harus hadir dalam naskah."""
        post_text = _load_post_text()
        # Hook harus menyebut konteks cowok/pria yang praktis
        has_angle = "cowok praktis" in post_text.lower() or "cowok" in post_text.lower()
        assert has_angle, (
            "Sudut pandang 'Cowok Praktis' tidak ditemukan dalam POST_TEXT"
        )
