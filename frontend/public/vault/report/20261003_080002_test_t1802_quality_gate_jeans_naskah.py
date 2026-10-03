"""
Quality Gate Review — T-1802
Validasi naskah copywriting celana jeans Korea (T-1801/Gathot)
terhadap gathot_social_standards.md.

Scope: Bebas klaim palsu, natural, relatable humor, format bersambung,
hashtag/SEO, dan kesesuaian spek produk dari celana_jeans_campaign.json.
"""

import json
import re
from pathlib import Path

import pytest

CAMPAIGN_JSON = Path(__file__).parent / "docs" / "celana_jeans_campaign.json"

# Naskah canonical dari post_jeans_threads.py (T-1801 artifact)
POST_1 = (
    "Sebagai cowok praktis, musuh terbesar pas nongkrong atau duduk seharian "
    "itu bukan kerjaan, tapi celana jeans yang bikin begah & sesak napas di "
    "perut bawah 🗿\n\n"
    "Ini celana model loose-fit / baggy gaya Korea tapi ada opsi pinggang "
    "karetnya. Duduk santai di warkop berjam-jam aman, ga perlu diam-diam "
    "lepas kancing celana lagi 👌"
)

POST_2 = (
    "Kurasi speknya:\n"
    "• Model: Loose-fit wide-leg gaya Korea (ga ngetat, ga bikin gerah)\n"
    "• Bahan: Denim lembut tahan bentuk (ga melar/ga molor)\n"
    "• Pinggang: Ada varian karet fleksibel & kancing biasa\n"
    "• Saku: 4 saku dalam aman buat hp/dompet\n\n"
    "🔗 Spill etalase produk di Shopee:\n"
    "https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq"
)

# Frasa klaim palsu yang dilarang (first-person ownership claims)
FALSE_CLAIM_PATTERNS = [
    r"\baku udah pake\b",
    r"\bsaya udah pake\b",
    r"\baku pakai\b",
    r"\bsaya pakai\b",
    r"\baku beli\b",
    r"\bsaya beli\b",
    r"\bpunya aku\b",
    r"\bpunya saya\b",
    r"\baku cobain\b",
    r"\bsaya cobain\b",
    r"\baku coba\b",
    r"\bsaya coba\b",
    r"\baku rasain\b",
    r"\bsaya rasain\b",
    r"\bbeneran tahan\b",
    r"\baku buktiin\b",
    r"\bsaya buktiin\b",
    r"\bdi badan aku\b",
    r"\bdi badan saya\b",
    r"\baku rekomendasiin\b",
    r"\bsaya rekomendasiin\b",
]

# Frasa hard-selling kaku yang dilarang
HARD_SELL_PATTERNS = [
    r"\bBELI SEKARANG\b",
    r"\bORDER SEKARANG\b",
    r"\bJANGAN SAMPAI KEHABISAN\b",
    r"\bSTOK TERBATAS\b",
    r"\bDISKON HARI INI SAJA\b",
    r"\bHARGA SPESIAL\b",
    r"\bPRODUK TERBAIK\b",
    r"\bNO\. ?1 DI INDONESIA\b",
    r"\bTERBAIK DI KELASNYA\b",
    r"\bGARANTI PUAS\b",
]

# Klaim performa yang tidak terverifikasi (superlative tanpa sumber)
UNVERIFIED_PERFORMANCE_PATTERNS = [
    r"\btahan \d+ jam\b",
    r"\btahan seharian penuh\b",
    r"\btidak luntur sama sekali\b",
    r"\btidak melar sama sekali\b",
    r"\bpaling nyaman\b",
    r"\bpaling bagus\b",
    r"\bpaling awet\b",
    r"\bsangat awet\b",
    r"\bsangat nyaman\b",
]

AFFILIATE_URL = "https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq"


class TestFalseClaimFree:
    """Verifikasi naskah bebas dari klaim kepemilikan/pengalaman pribadi palsu."""

    def test_post1_no_first_person_ownership_claim(self):
        # ARRANGE
        text = POST_1.lower()
        # ACT
        violations = [p for p in FALSE_CLAIM_PATTERNS if re.search(p, text)]
        # ASSERT
        assert violations == [], (
            f"POST_1 mengandung klaim palsu first-person: {violations}"
        )

    def test_post2_no_first_person_ownership_claim(self):
        # ARRANGE
        text = POST_2.lower()
        # ACT
        violations = [p for p in FALSE_CLAIM_PATTERNS if re.search(p, text)]
        # ASSERT
        assert violations == [], (
            f"POST_2 mengandung klaim palsu first-person: {violations}"
        )

    def test_post1_no_unverified_performance_claim(self):
        # ARRANGE
        text = POST_1.lower()
        # ACT
        violations = [p for p in UNVERIFIED_PERFORMANCE_PATTERNS if re.search(p, text)]
        # ASSERT
        assert violations == [], (
            f"POST_1 mengandung klaim performa tidak terverifikasi: {violations}"
        )

    def test_post2_no_unverified_performance_claim(self):
        # ARRANGE
        text = POST_2.lower()
        # ACT
        violations = [p for p in UNVERIFIED_PERFORMANCE_PATTERNS if re.search(p, text)]
        # ASSERT
        assert violations == [], (
            f"POST_2 mengandung klaim performa tidak terverifikasi: {violations}"
        )

    def test_post2_uses_kurasi_framing_not_personal_testimony(self):
        """
        Standar: kurasi spek pabrik, bukan testimoni personal.
        Kata 'Kurasi' di awal POST_2 adalah sinyal framing yang benar.
        """
        # ARRANGE
        text = POST_2
        # ACT
        has_kurasi_framing = text.strip().startswith("Kurasi")
        # ASSERT
        assert has_kurasi_framing, (
            "POST_2 harus dimulai dengan framing kurasi objektif, bukan testimoni personal"
        )


class TestHardSellFree:
    """Verifikasi naskah bebas dari gaya hard-selling kaku."""

    def test_post1_no_hard_sell_language(self):
        # ARRANGE
        text = POST_1.upper()
        # ACT
        violations = [p for p in HARD_SELL_PATTERNS if re.search(p, text)]
        # ASSERT
        assert violations == [], (
            f"POST_1 mengandung bahasa hard-sell kaku: {violations}"
        )

    def test_post2_no_hard_sell_language(self):
        # ARRANGE
        text = POST_2.upper()
        # ACT
        violations = [p for p in HARD_SELL_PATTERNS if re.search(p, text)]
        # ASSERT
        assert violations == [], (
            f"POST_2 mengandung bahasa hard-sell kaku: {violations}"
        )


class TestRelatableHumor:
    """Verifikasi naskah mengandung elemen humor situasional dan observasi relatable."""

    def test_post1_contains_situational_hook(self):
        """
        Hook harus membuka dengan observasi situasional yang relatable,
        bukan langsung promosi produk.
        """
        # ARRANGE
        text = POST_1
        # ACT
        has_situational_opening = (
            "cowok praktis" in text.lower()
            or "musuh terbesar" in text.lower()
            or "nongkrong" in text.lower()
            or "duduk seharian" in text.lower()
        )
        # ASSERT
        assert has_situational_opening, (
            "POST_1 harus membuka dengan observasi situasional relatable, bukan promosi langsung"
        )

    def test_post1_contains_punchline_element(self):
        """
        Humor situasional: 'diam-diam lepas kancing celana' adalah punchline
        yang relatable untuk target audiens cowok yang pernah mengalami celana sesak.
        """
        # ARRANGE
        text = POST_1
        # ACT
        has_punchline = "lepas kancing" in text.lower() or "sesak" in text.lower()
        # ASSERT
        assert has_punchline, (
            "POST_1 harus mengandung punchline humor situasional yang relatable"
        )

    def test_post1_hook_does_not_start_with_product_name(self):
        """
        Standar: Hook kuat tidak boleh dimulai dengan nama produk.
        Harus dimulai dengan observasi/situasi audiens.
        """
        # ARRANGE
        first_line = POST_1.split("\n")[0].strip()
        # ACT
        starts_with_product = first_line.lower().startswith("celana") or first_line.lower().startswith("produk")
        # ASSERT
        assert not starts_with_product, (
            "Hook POST_1 tidak boleh dimulai dengan nama produk — harus observasi audiens"
        )

    def test_post1_tone_is_conversational_not_formal(self):
        """
        Tone percakapan: penggunaan kata gaul/informal menandakan naturalness.
        Kata seperti 'ga', 'nongkrong', 'warkop' adalah indikator tone yang tepat.
        """
        # ARRANGE
        text = POST_1.lower()
        conversational_markers = ["ga ", "nongkrong", "warkop", "diam-diam"]
        # ACT
        found_markers = [m for m in conversational_markers if m in text]
        # ASSERT
        assert len(found_markers) >= 2, (
            f"POST_1 harus menggunakan minimal 2 penanda tone percakapan. "
            f"Ditemukan: {found_markers}"
        )


class TestThreadSplitFormat:
    """Verifikasi format bersambung (Thread Split) sesuai standar gathot_social_standards.md §2.3."""

    def test_post1_is_hook_plus_observation(self):
        """POST_1 harus berisi hook + observasi relatable, bukan spesifikasi teknis."""
        # ARRANGE
        text = POST_1
        # ACT
        has_hook_element = len(text) > 50
        has_no_bullet_list = "•" not in text
        # ASSERT
        assert has_hook_element, "POST_1 terlalu pendek untuk menjadi hook yang efektif"
        assert has_no_bullet_list, (
            "POST_1 (hook post) tidak boleh berisi bullet list spesifikasi — "
            "itu domain POST_2"
        )

    def test_post2_is_spec_curation_with_cta(self):
        """POST_2 harus berisi kurasi spesifikasi teknis + CTA link resmi."""
        # ARRANGE
        text = POST_2
        # ACT
        has_bullet_specs = "•" in text
        has_affiliate_link = AFFILIATE_URL in text
        # ASSERT
        assert has_bullet_specs, "POST_2 harus berisi bullet list spesifikasi produk"
        assert has_affiliate_link, (
            f"POST_2 harus berisi affiliate link resmi: {AFFILIATE_URL}"
        )

    def test_both_posts_are_non_empty(self):
        # ARRANGE
        min_length = 50
        # ACT & ASSERT
        assert len(POST_1.strip()) >= min_length, (
            f"POST_1 terlalu pendek (min {min_length} chars)"
        )
        assert len(POST_2.strip()) >= min_length, (
            f"POST_2 terlalu pendek (min {min_length} chars)"
        )

    def test_post2_spec_count_matches_campaign_json(self):
        """
        Jumlah spesifikasi di POST_2 harus konsisten dengan celana_jeans_campaign.json.
        Campaign JSON mendefinisikan 4 specs — POST_2 harus mencakup semua 4.
        """
        # ARRANGE
        campaign = json.loads(CAMPAIGN_JSON.read_text())
        expected_spec_count = len(campaign["specs"])
        # ACT
        bullet_count = POST_2.count("•")
        # ASSERT
        assert bullet_count == expected_spec_count, (
            f"POST_2 harus memiliki {expected_spec_count} bullet specs "
            f"(sesuai campaign JSON), ditemukan {bullet_count}"
        )


class TestSpecAccuracy:
    """Verifikasi akurasi spesifikasi produk terhadap celana_jeans_campaign.json."""

    def setup_method(self):
        self.campaign = json.loads(CAMPAIGN_JSON.read_text())

    def test_product_name_referenced_in_posts(self):
        """Produk harus dapat diidentifikasi dari naskah (jeans/celana/Korea)."""
        # ARRANGE
        combined = (POST_1 + POST_2).lower()
        # ACT
        has_jeans_reference = "jeans" in combined or "celana" in combined
        has_korea_reference = "korea" in combined
        # ASSERT
        assert has_jeans_reference, "Naskah harus menyebut jenis produk (jeans/celana)"
        assert has_korea_reference, "Naskah harus menyebut asal gaya produk (Korea)"

    def test_loose_fit_spec_mentioned(self):
        """Spec 'loose fit / wide-leg' dari campaign JSON harus tercermin di naskah."""
        # ARRANGE
        combined = (POST_1 + POST_2).lower()
        # ACT
        has_loose_fit = "loose" in combined or "longgar" in combined or "wide-leg" in combined
        # ASSERT
        assert has_loose_fit, (
            "Spec 'loose fit / wide-leg' dari campaign JSON tidak ditemukan di naskah"
        )

    def test_elastic_waist_spec_mentioned(self):
        """Spec 'pinggang karet fleksibel' dari campaign JSON harus tercermin di naskah."""
        # ARRANGE
        combined = (POST_1 + POST_2).lower()
        # ACT
        has_elastic = "karet" in combined
        # ASSERT
        assert has_elastic, (
            "Spec 'pinggang karet fleksibel' dari campaign JSON tidak ditemukan di naskah"
        )

    def test_pocket_spec_mentioned(self):
        """Spec '4 saku fungsional' dari campaign JSON harus tercermin di naskah."""
        # ARRANGE
        combined = (POST_1 + POST_2).lower()
        # ACT
        has_pocket = "saku" in combined
        # ASSERT
        assert has_pocket, (
            "Spec '4 saku fungsional' dari campaign JSON tidak ditemukan di naskah"
        )

    def test_denim_material_spec_mentioned(self):
        """Spec 'bahan denim halus tidak melar' dari campaign JSON harus tercermin di naskah."""
        # ARRANGE
        combined = (POST_1 + POST_2).lower()
        # ACT
        has_denim = "denim" in combined
        # ASSERT
        assert has_denim, (
            "Spec 'bahan denim' dari campaign JSON tidak ditemukan di naskah"
        )

    def test_affiliate_url_matches_campaign_json(self):
        """URL affiliate di naskah harus identik dengan yang ada di campaign JSON."""
        # ARRANGE
        expected_url = self.campaign["affiliate_url"]
        # ACT
        url_in_post2 = expected_url in POST_2
        # ASSERT
        assert url_in_post2, (
            f"URL affiliate di POST_2 tidak cocok dengan campaign JSON.\n"
            f"Expected: {expected_url}"
        )

    def test_no_specs_invented_beyond_campaign_json(self):
        """
        Naskah tidak boleh mengklaim spesifikasi yang tidak ada di campaign JSON.
        Klaim seperti 'anti-air', 'UV protection', 'quick-dry' adalah fabricated specs.
        """
        # ARRANGE
        combined = (POST_1 + POST_2).lower()
        fabricated_specs = [
            "anti air", "anti-air", "waterproof",
            "uv protection", "quick dry", "quick-dry",
            "anti bau", "anti-bau", "odor",
            "anti jamur", "anti-jamur",
            "tahan api", "fire resistant",
        ]
        # ACT
        violations = [s for s in fabricated_specs if s in combined]
        # ASSERT
        assert violations == [], (
            f"Naskah mengklaim spesifikasi yang tidak ada di campaign JSON: {violations}"
        )


class TestAffiliateDisclosure:
    """Verifikasi transparansi afiliasi — tidak menyembunyikan sifat promosi."""

    def test_post2_contains_shopee_reference(self):
        """
        Naskah harus secara eksplisit menyebut platform (Shopee) agar audiens
        tahu ini adalah link belanja, bukan link editorial.
        """
        # ARRANGE
        text = POST_2.lower()
        # ACT
        has_shopee = "shopee" in text
        # ASSERT
        assert has_shopee, (
            "POST_2 harus menyebut 'Shopee' secara eksplisit sebagai transparansi afiliasi"
        )

    def test_affiliate_url_is_valid_shopee_format(self):
        """URL harus menggunakan domain Shopee yang valid (s.shopee.co.id)."""
        # ARRANGE
        url = AFFILIATE_URL
        # ACT
        is_valid_domain = url.startswith("https://s.shopee.co.id/")
        # ASSERT
        assert is_valid_domain, (
            f"URL affiliate harus menggunakan domain s.shopee.co.id, ditemukan: {url}"
        )


class TestBoundaryValueLength:
    """
    BVA pada panjang teks naskah.
    Facebook optimal: 40-80 kata per post untuk engagement tertinggi.
    Minimum viable: > 20 kata (terlalu pendek = tidak informatif).
    Maximum safe: < 500 kata (terlalu panjang = drop-off rate tinggi).
    """

    def _word_count(self, text: str) -> int:
        return len(text.split())

    def test_post1_word_count_above_minimum(self):
        # ARRANGE
        min_words = 20
        # ACT
        count = self._word_count(POST_1)
        # ASSERT
        assert count >= min_words, (
            f"POST_1 terlalu pendek: {count} kata (minimum {min_words})"
        )

    def test_post1_word_count_below_maximum(self):
        # ARRANGE
        max_words = 500
        # ACT
        count = self._word_count(POST_1)
        # ASSERT
        assert count <= max_words, (
            f"POST_1 terlalu panjang: {count} kata (maksimum {max_words})"
        )

    def test_post2_word_count_above_minimum(self):
        # ARRANGE
        min_words = 20
        # ACT
        count = self._word_count(POST_2)
        # ASSERT
        assert count >= min_words, (
            f"POST_2 terlalu pendek: {count} kata (minimum {min_words})"
        )

    def test_post2_word_count_below_maximum(self):
        # ARRANGE
        max_words = 500
        # ACT
        count = self._word_count(POST_2)
        # ASSERT
        assert count <= max_words, (
            f"POST_2 terlalu panjang: {count} kata (maksimum {max_words})"
        )

    def test_post1_char_count_within_threads_limit(self):
        """Threads character limit: 500 chars per post."""
        # ARRANGE
        threads_limit = 500
        # ACT
        count = len(POST_1)
        # ASSERT
        assert count <= threads_limit, (
            f"POST_1 melebihi Threads character limit: {count} chars (max {threads_limit})"
        )

    def test_post2_char_count_within_threads_limit(self):
        """Threads character limit: 500 chars per post."""
        # ARRANGE
        threads_limit = 500
        # ACT
        count = len(POST_2)
        # ASSERT
        assert count <= threads_limit, (
            f"POST_2 melebihi Threads character limit: {count} chars (max {threads_limit})"
        )


class TestEdgeCaseContentIntegrity:
    """Edge case dan type-confusion checks pada konten naskah."""

    def test_posts_are_strings_not_none(self):
        # ARRANGE & ACT & ASSERT
        assert isinstance(POST_1, str), "POST_1 harus bertipe string"
        assert isinstance(POST_2, str), "POST_2 harus bertipe string"
        assert POST_1 is not None, "POST_1 tidak boleh None"
        assert POST_2 is not None, "POST_2 tidak boleh None"

    def test_posts_have_no_placeholder_text(self):
        """Naskah tidak boleh mengandung placeholder yang belum diganti."""
        # ARRANGE
        combined = (POST_1 + POST_2).lower()
        placeholders = [
            "[nama produk]", "[link]", "[harga]", "[diskon]",
            "lorem ipsum", "xxx", "todo", "tbd", "placeholder",
            "[insert", "[tambahkan",
        ]
        # ACT
        found = [p for p in placeholders if p in combined]
        # ASSERT
        assert found == [], f"Naskah mengandung placeholder yang belum diganti: {found}"

    def test_posts_have_no_raw_html_tags(self):
        """Naskah untuk Threads/Facebook tidak boleh mengandung raw HTML tags."""
        # ARRANGE
        combined = POST_1 + POST_2
        # ACT
        has_html = bool(re.search(r"<[a-zA-Z][^>]*>", combined))
        # ASSERT
        assert not has_html, "Naskah mengandung raw HTML tags yang tidak sesuai untuk platform sosial"

    def test_posts_have_no_markdown_formatting(self):
        """
        Threads/Facebook tidak render Markdown. Naskah tidak boleh menggunakan
        **bold**, *italic*, atau # heading yang akan tampil sebagai literal chars.
        """
        # ARRANGE
        combined = POST_1 + POST_2
        # ACT
        has_markdown_bold = bool(re.search(r"\*\*[^*]+\*\*", combined))
        has_markdown_italic = bool(re.search(r"\*[^*]+\*", combined))
        has_markdown_heading = bool(re.search(r"^#{1,6} ", combined, re.MULTILINE))
        # ASSERT
        assert not has_markdown_bold, "Naskah mengandung Markdown **bold** yang tidak dirender di Threads/FB"
        assert not has_markdown_italic, "Naskah mengandung Markdown *italic* yang tidak dirender di Threads/FB"
        assert not has_markdown_heading, "Naskah mengandung Markdown # heading yang tidak dirender di Threads/FB"

    def test_campaign_json_is_parseable(self):
        """celana_jeans_campaign.json harus valid JSON dan memiliki field wajib."""
        # ARRANGE
        raw = CAMPAIGN_JSON.read_text()
        # ACT
        data = json.loads(raw)
        # ASSERT
        assert "product_name" in data, "campaign JSON harus memiliki field 'product_name'"
        assert "affiliate_url" in data, "campaign JSON harus memiliki field 'affiliate_url'"
        assert "specs" in data, "campaign JSON harus memiliki field 'specs'"
        assert isinstance(data["specs"], list), "field 'specs' harus bertipe list"
        assert len(data["specs"]) > 0, "field 'specs' tidak boleh kosong"
