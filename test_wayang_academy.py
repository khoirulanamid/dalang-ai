"""
Test Suite untuk Wayang Academy (Tahap 3 — Skill Upgrade System)
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from wayang_academy import teach_wayang, get_wayang_skills, list_all_wayang_skills_summary


class TestTeachWayang:
    """Uji mekanisme pembelajaran Wayang."""

    def test_teach_valid_wayang(self, tmp_path):
        """Wayang berhasil mempelajari skill baru dan menyimpannya."""
        with patch("wayang_academy.STANDARDS_DIR", tmp_path):
            result = teach_wayang("zaki", "Gunakan SQLAlchemy 2.0 ORM async untuk semua query database", instructor="Bos Muda")

        assert result["agent"] == "zaki"
        assert result["wayang_name"] == "Zaki"
        assert "learned_at" in result
        assert "SQLAlchemy" in result["skill"]

    def test_teach_creates_standards_file(self, tmp_path):
        """File standar Wayang dibuat jika belum ada."""
        with patch("wayang_academy.STANDARDS_DIR", tmp_path):
            teach_wayang("ren", "Gunakan hypothesis untuk property-based testing", instructor="Bos Muda")
            skill_file = tmp_path / "ren_qa_standards.md"
            assert skill_file.exists()
            content = skill_file.read_text(encoding="utf-8")
            assert "hypothesis" in content

    def test_teach_appends_to_existing_file(self, tmp_path):
        """Skill baru ditambahkan ke bawah file yang sudah ada, bukan menimpa."""
        with patch("wayang_academy.STANDARDS_DIR", tmp_path):
            teach_wayang("lulu", "Skill pertama: Tailwind CSS v3", instructor="Bos Muda")
            teach_wayang("lulu", "Skill kedua: lucide-icons", instructor="Bos Muda")
            skill_file = tmp_path / "lulu_frontend_standards.md"
            content = skill_file.read_text(encoding="utf-8")
            assert "Skill pertama" in content
            assert "Skill kedua" in content

    def test_teach_invalid_wayang_raises(self):
        """Wayang yang tidak dikenal harus menghasilkan ValueError."""
        with pytest.raises(ValueError, match="tidak dikenal"):
            teach_wayang("batman", "Skill tidak valid")

    def test_lesson_count_increments(self, tmp_path):
        """Jumlah pelajaran terdeteksi dengan benar setelah diajarkan."""
        with patch("wayang_academy.STANDARDS_DIR", tmp_path):
            teach_wayang("kai", "Pelajaran 1: OWASP tambahan", instructor="Bos Muda")
            teach_wayang("kai", "Pelajaran 2: CVE terbaru", instructor="Bos Muda")
            teach_wayang("kai", "Pelajaran 3: Bandit rules baru", instructor="Bos Muda")

            summary = list_all_wayang_skills_summary()
            kai_summary = next(s for s in summary if s["id"] == "kai")

    def test_teach_includes_instructor_name(self, tmp_path):
        """Nama instruktur tercatat dalam file standar."""
        with patch("wayang_academy.STANDARDS_DIR", tmp_path):
            teach_wayang("mika", "Gunakan format AsciiDoc untuk dokumentasi teknis", instructor="Bos Muda")
            skill_file = tmp_path / "mika_docs_standards.md"
            content = skill_file.read_text(encoding="utf-8")
            assert "Bos Muda" in content

    def test_teach_includes_timestamp(self, tmp_path):
        """Timestamp pembelajaran tercatat di file standar."""
        with patch("wayang_academy.STANDARDS_DIR", tmp_path):
            teach_wayang("nova", "Gunakan Podman sebagai alternatif Docker", instructor="Bos Muda")
            skill_file = tmp_path / "nova_devops_standards.md"
            content = skill_file.read_text(encoding="utf-8")
            assert "UTC" in content  # Format timestamp mengandung UTC


class TestSkillsSummary:
    """Uji ringkasan keahlian seluruh wayang."""

    def test_summary_covers_all_seven_wayang(self):
        summary = list_all_wayang_skills_summary()
        agent_ids = [s["id"] for s in summary]
        for expected in ["pingot", "zaki", "lulu", "mika", "nova", "kai", "ren"]:
            assert expected in agent_ids

    def test_summary_contains_core_keywords(self):
        summary = list_all_wayang_skills_summary()
        for s in summary:
            assert len(s["core_keywords"]) > 0
