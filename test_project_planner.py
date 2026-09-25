"""
Test Suite untuk Project Planner (Tahap 2)
Memastikan Risko bisa merencanakan proyek dari deskripsi bebas dengan benar.
"""

import pytest
import asyncio
from project_planner import _generate_fallback_plan, format_roadmap_markdown
from roadmap_parser import parse_roadmap
import tempfile
import os


class TestFallbackPlanner:
    """Uji fallback planner deterministik (tanpa LLM)."""

    def test_web_app_includes_frontend_and_backend(self):
        tasks = _generate_fallback_plan(
            "Web App",
            "Aplikasi web dengan tampilan UI dan REST API backend"
        )
        agents = [t["agent"] for t in tasks]
        assert "lulu" in agents
        assert "zaki" in agents
        assert "ren" in agents  # QA selalu ada

    def test_kalkulator_no_data_no_devops_no_security(self):
        tasks = _generate_fallback_plan(
            "Kalkulator",
            "Kalkulator web dengan tampilan bersih dan operasi dasar"
        )
        agents = [t["agent"] for t in tasks]
        assert "pingot" not in agents   # tidak ada database
        assert "nova" not in agents     # tidak ada deployment
        assert "kai" not in agents      # tidak ada auth/security
        assert "lulu" in agents
        assert "ren" in agents

    def test_database_project_includes_pingot(self):
        tasks = _generate_fallback_plan(
            "Sistem Inventaris",
            "Sistem manajemen stok dengan database dan skema produk"
        )
        agents = [t["agent"] for t in tasks]
        assert "pingot" in agents

    def test_auth_project_includes_kai(self):
        tasks = _generate_fallback_plan(
            "Auth System",
            "Sistem login register dengan password hashing dan token JWT"
        )
        agents = [t["agent"] for t in tasks]
        assert "kai" in agents

    def test_dependencies_are_ordered(self):
        tasks = _generate_fallback_plan(
            "CRUD App",
            "Aplikasi CRUD dengan database, API backend, dan tampilan UI"
        )
        # Backend tidak boleh depend on task yang belum ada
        task_ids = [t["id"] for t in tasks]
        for t in tasks:
            for dep in t.get("dependencies", []):
                assert dep in task_ids, f"Dependensi {dep} tidak ada dalam daftar task"

    def test_always_includes_qa_ren(self):
        """Ren selalu ada sebagai QA di setiap proyek."""
        for desc in [
            "Aplikasi todo list sederhana",
            "Website landing page perusahaan",
            "Tool konversi format teks",
        ]:
            tasks = _generate_fallback_plan("Proyek", desc)
            agents = [t["agent"] for t in tasks]
            assert "ren" in agents, f"Ren harus selalu ada, tapi tidak ada untuk: {desc}"


class TestRoadmapFormatting:
    """Uji output ROADMAP.md yang dihasilkan planner."""

    def test_generated_roadmap_is_parseable(self):
        tasks = [
            {"id": "T-001", "agent": "zaki", "title": "Buat API", "dependencies": []},
            {"id": "T-002", "agent": "lulu", "title": "Buat UI", "dependencies": ["T-001"]},
            {"id": "T-003", "agent": "ren", "title": "Buat Test", "dependencies": ["T-001"]},
        ]
        content = format_roadmap_markdown("Test Project", "Deskripsi test", tasks)

        # Tulis ke file sementara dan parse
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            tmp_path = f.name

        try:
            roadmap = parse_roadmap(tmp_path)
            assert roadmap["metadata"]["project"] == "Test Project"
            assert len(roadmap["tasks"]) == 3
            assert roadmap["tasks"][0]["id"] == "T-001"
            assert roadmap["tasks"][1]["dependencies"] == ["T-001"]
        finally:
            os.unlink(tmp_path)

    def test_generated_tasks_have_correct_agents(self):
        tasks = [
            {"id": "T-001", "agent": "pingot", "title": "Schema", "dependencies": []},
            {"id": "T-002", "agent": "zaki", "title": "API", "dependencies": ["T-001"]},
        ]
        content = format_roadmap_markdown("Schema Project", "Desc", tasks)
        assert "[pingot]" in content
        assert "[zaki]" in content

    def test_roadmap_contains_project_name(self):
        tasks = [{"id": "T-001", "agent": "lulu", "title": "UI", "dependencies": []}]
        content = format_roadmap_markdown("Proyek Spesial", "Deskripsi", tasks)
        assert "Proyek Spesial" in content
