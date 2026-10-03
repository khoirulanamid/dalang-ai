"""
Test Suite T-1706: Verifikasi Pengarsipan Akta Kelahiran & Spesifikasi Gathot
Dieksekusi oleh: Bagong (Asset & Release Custodian)
"""

import json
import os
import pytest
from pathlib import Path

VAULT_DIR = Path("/root/storage/projects/dalang-ai/vault")
VAULT_INDEX = VAULT_DIR / "vault_index.json"
FRONTEND_PUBLIC = Path("/root/storage/projects/dalang-ai/frontend/public/vault")

AKTA_ID = "VLT-52350"
SPEC_ID = "VLT-29445"
AKTA_FILENAME = "20261003_142309_gathot_akta_kelahiran.md"
SPEC_FILENAME = "20261003_142309_gathot_social_standards.md"


@pytest.fixture
def vault_index():
    """Load vault index dari disk."""
    assert VAULT_INDEX.exists(), "vault_index.json tidak ditemukan!"
    with open(VAULT_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)


class TestVaultIndexIntegrity:
    """Verifikasi integritas vault_index.json setelah pengarsipan T-1706."""

    def test_vault_index_exists(self):
        """vault_index.json harus ada di disk."""
        assert VAULT_INDEX.exists(), "vault_index.json tidak ditemukan di vault!"

    def test_vault_index_is_valid_json(self):
        """vault_index.json harus berisi JSON yang valid."""
        with open(VAULT_INDEX, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list), "vault_index.json harus berupa list"

    def test_vault_index_has_minimum_entries(self, vault_index):
        """Vault harus memiliki minimal 24 entri setelah T-1706."""
        assert len(vault_index) >= 24, (
            f"Vault hanya memiliki {len(vault_index)} entri, expected >= 24"
        )

    def test_akta_kelahiran_in_index(self, vault_index):
        """Akta Kelahiran Gathot harus terdaftar di vault_index.json."""
        ids = [item["id"] for item in vault_index]
        assert AKTA_ID in ids, f"ID {AKTA_ID} (Akta Kelahiran) tidak ditemukan di vault_index!"

    def test_spec_in_index(self, vault_index):
        """Spesifikasi Gathot harus terdaftar di vault_index.json."""
        ids = [item["id"] for item in vault_index]
        assert SPEC_ID in ids, f"ID {SPEC_ID} (Spec Gathot) tidak ditemukan di vault_index!"

    def test_gathot_entries_count(self, vault_index):
        """Harus ada tepat 2 entri terkait Gathot di vault_index."""
        gathot_entries = [
            x for x in vault_index
            if "gathot" in x.get("filename", "").lower()
            or "gathot" in x.get("title", "").lower()
        ]
        assert len(gathot_entries) >= 2, (
            f"Hanya {len(gathot_entries)} entri Gathot ditemukan, expected >= 2"
        )


class TestAktaKelahiranEntry:
    """Verifikasi entri Akta Kelahiran Gathot di vault_index."""

    @pytest.fixture
    def akta_entry(self, vault_index):
        entry = next((x for x in vault_index if x["id"] == AKTA_ID), None)
        assert entry is not None, f"Entry {AKTA_ID} tidak ditemukan!"
        return entry

    def test_akta_category_is_document(self, akta_entry):
        assert akta_entry["category"] == "document", (
            f"Category harus 'document', got '{akta_entry['category']}'"
        )

    def test_akta_producer_is_bagong(self, akta_entry):
        assert akta_entry["producer_agent"] == "bagong", (
            f"Producer harus 'bagong', got '{akta_entry['producer_agent']}'"
        )

    def test_akta_title_contains_gathot(self, akta_entry):
        assert "Gathot" in akta_entry["title"], (
            f"Title harus mengandung 'Gathot': {akta_entry['title']}"
        )

    def test_akta_title_contains_akta(self, akta_entry):
        assert "Akta" in akta_entry["title"], (
            f"Title harus mengandung 'Akta': {akta_entry['title']}"
        )

    def test_akta_size_is_positive(self, akta_entry):
        assert akta_entry["size_bytes"] > 0, "size_bytes harus > 0"

    def test_akta_has_file_path(self, akta_entry):
        assert akta_entry["file_path"], "file_path tidak boleh kosong"

    def test_akta_has_relative_url(self, akta_entry):
        assert akta_entry["relative_url"].startswith("/vault/"), (
            f"relative_url harus dimulai dengan '/vault/': {akta_entry['relative_url']}"
        )

    def test_akta_metadata_has_nomor_akta(self, akta_entry):
        meta = akta_entry.get("metadata", {})
        assert meta.get("nomor_akta") == "DALANG-WAYANG-007", (
            f"metadata.nomor_akta harus 'DALANG-WAYANG-007', got '{meta.get('nomor_akta')}'"
        )

    def test_akta_metadata_has_task_id(self, akta_entry):
        meta = akta_entry.get("metadata", {})
        assert meta.get("task_id") == "T-1706", (
            f"metadata.task_id harus 'T-1706', got '{meta.get('task_id')}'"
        )

    def test_akta_metadata_wayang_name(self, akta_entry):
        meta = akta_entry.get("metadata", {})
        assert meta.get("wayang_name") == "Gathot", (
            f"metadata.wayang_name harus 'Gathot', got '{meta.get('wayang_name')}'"
        )


class TestSpecEntry:
    """Verifikasi entri Spesifikasi Gathot di vault_index."""

    @pytest.fixture
    def spec_entry(self, vault_index):
        entry = next((x for x in vault_index if x["id"] == SPEC_ID), None)
        assert entry is not None, f"Entry {SPEC_ID} tidak ditemukan!"
        return entry

    def test_spec_category_is_document(self, spec_entry):
        assert spec_entry["category"] == "document", (
            f"Category harus 'document', got '{spec_entry['category']}'"
        )

    def test_spec_producer_is_gathot(self, spec_entry):
        assert spec_entry["producer_agent"] == "gathot", (
            f"Producer harus 'gathot', got '{spec_entry['producer_agent']}'"
        )

    def test_spec_title_contains_standards(self, spec_entry):
        assert "Standards" in spec_entry["title"] or "Engineering" in spec_entry["title"], (
            f"Title harus mengandung 'Standards' atau 'Engineering': {spec_entry['title']}"
        )

    def test_spec_size_is_substantial(self, spec_entry):
        """Spesifikasi harus berukuran > 10KB (dokumen lengkap)."""
        assert spec_entry["size_bytes"] > 10_000, (
            f"Spec terlalu kecil: {spec_entry['size_bytes']} bytes, expected > 10,000"
        )

    def test_spec_metadata_has_version(self, spec_entry):
        meta = spec_entry.get("metadata", {})
        assert meta.get("version") == "1.0.0", (
            f"metadata.version harus '1.0.0', got '{meta.get('version')}'"
        )

    def test_spec_metadata_has_sections(self, spec_entry):
        meta = spec_entry.get("metadata", {})
        assert meta.get("sections") == 10, (
            f"metadata.sections harus 10, got '{meta.get('sections')}'"
        )

    def test_spec_metadata_platforms_covered(self, spec_entry):
        meta = spec_entry.get("metadata", {})
        platforms = meta.get("platforms_covered", [])
        assert "Threads" in platforms, "Threads harus ada di platforms_covered"
        assert "Facebook" in platforms, "Facebook harus ada di platforms_covered"


class TestPhysicalFiles:
    """Verifikasi file fisik ada di vault dan frontend/public."""

    def test_akta_exists_in_vault(self):
        """File akta harus ada di vault/document/."""
        vault_path = VAULT_DIR / "document" / AKTA_FILENAME
        assert vault_path.exists(), f"File tidak ditemukan di vault: {vault_path}"

    def test_spec_exists_in_vault(self):
        """File spec harus ada di vault/document/."""
        vault_path = VAULT_DIR / "document" / SPEC_FILENAME
        assert vault_path.exists(), f"File tidak ditemukan di vault: {vault_path}"

    def test_akta_exists_in_frontend_public(self):
        """File akta harus di-mirror ke frontend/public/vault/document/."""
        public_path = FRONTEND_PUBLIC / "document" / AKTA_FILENAME
        assert public_path.exists(), f"File tidak ditemukan di frontend/public: {public_path}"

    def test_spec_exists_in_frontend_public(self):
        """File spec harus di-mirror ke frontend/public/vault/document/."""
        public_path = FRONTEND_PUBLIC / "document" / SPEC_FILENAME
        assert public_path.exists(), f"File tidak ditemukan di frontend/public: {public_path}"

    def test_akta_file_size_matches_index(self, vault_index):
        """Ukuran file akta di disk harus sesuai dengan yang tercatat di index."""
        entry = next((x for x in vault_index if x["id"] == AKTA_ID), None)
        assert entry is not None
        vault_path = VAULT_DIR / "document" / AKTA_FILENAME
        actual_size = os.path.getsize(vault_path)
        assert actual_size == entry["size_bytes"], (
            f"Size mismatch: disk={actual_size}, index={entry['size_bytes']}"
        )

    def test_spec_file_size_matches_index(self, vault_index):
        """Ukuran file spec di disk harus sesuai dengan yang tercatat di index."""
        entry = next((x for x in vault_index if x["id"] == SPEC_ID), None)
        assert entry is not None
        vault_path = VAULT_DIR / "document" / SPEC_FILENAME
        actual_size = os.path.getsize(vault_path)
        assert actual_size == entry["size_bytes"], (
            f"Size mismatch: disk={actual_size}, index={entry['size_bytes']}"
        )

    def test_akta_content_has_gathot_identity(self):
        """Konten akta harus mengandung identitas Gathot yang valid."""
        vault_path = VAULT_DIR / "document" / AKTA_FILENAME
        content = vault_path.read_text(encoding="utf-8")
        assert "DALANG-WAYANG-007" in content, "Nomor akta tidak ditemukan dalam file"
        assert "Gathot" in content, "Nama Gathot tidak ditemukan dalam file"
        assert "Social Media" in content, "Peran tidak ditemukan dalam file"

    def test_spec_content_has_required_sections(self):
        """Konten spec harus mengandung semua 10 seksi yang dipersyaratkan."""
        vault_path = VAULT_DIR / "document" / SPEC_FILENAME
        content = vault_path.read_text(encoding="utf-8")
        required_sections = [
            "Scope and Applicability",
            "Copywriting SOP",
            "Hook Psychology",
            "Ethical Curation",
            "Social SEO",
            "Posting Management",
            "Platform-Specific Rules",
            "Quality Gate",
            "Prohibited Patterns",
            "Glossary",
        ]
        for section in required_sections:
            assert section in content, f"Seksi '{section}' tidak ditemukan dalam spec!"

    def test_vault_and_public_files_are_identical(self):
        """File di vault dan frontend/public harus identik (byte-for-byte)."""
        for filename in [AKTA_FILENAME, SPEC_FILENAME]:
            vault_path = VAULT_DIR / "document" / filename
            public_path = FRONTEND_PUBLIC / "document" / filename
            assert vault_path.read_bytes() == public_path.read_bytes(), (
                f"File {filename} berbeda antara vault dan frontend/public!"
            )


class TestVaultIndexSchema:
    """Verifikasi schema setiap entri di vault_index.json."""

    REQUIRED_FIELDS = [
        "id", "filename", "category", "producer_agent",
        "title", "description", "file_path", "relative_url",
        "size_bytes", "created_at", "metadata"
    ]

    def test_all_entries_have_required_fields(self, vault_index):
        """Setiap entri di vault_index harus memiliki semua field wajib."""
        for entry in vault_index:
            for field in self.REQUIRED_FIELDS:
                assert field in entry, (
                    f"Entry {entry.get('id', '?')} tidak memiliki field '{field}'"
                )

    def test_all_ids_are_unique(self, vault_index):
        """Semua ID di vault_index harus unik."""
        ids = [x["id"] for x in vault_index]
        assert len(ids) == len(set(ids)), "Terdapat ID duplikat di vault_index!"

    def test_all_size_bytes_are_positive(self, vault_index):
        """Semua size_bytes harus bernilai positif."""
        for entry in vault_index:
            assert entry["size_bytes"] > 0, (
                f"Entry {entry['id']} memiliki size_bytes <= 0: {entry['size_bytes']}"
            )

    def test_all_relative_urls_start_with_vault(self, vault_index):
        """Semua relative_url harus dimulai dengan '/vault/'."""
        for entry in vault_index:
            assert entry["relative_url"].startswith("/vault/"), (
                f"Entry {entry['id']} memiliki relative_url tidak valid: {entry['relative_url']}"
            )
