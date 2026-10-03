"""
Test Suite untuk Wayang Gathot (Social Media & Growth Specialist)
Memastikan Wayang ke-12 resmi terdaftar, auto-routing bekerja, dan standards dimuat dengan benar.
"""

import pytest
from wayang_router import auto_route_task, WAYANG_ROSTER
from wayang_academy import STANDARDS_MAP, get_wayang_skills
from real_subagent_runner import _load_standards, ROLE_PROMPTS


class TestGathotRegistration:
    def test_gathot_in_roster(self):
        assert "gathot" in WAYANG_ROSTER
        assert WAYANG_ROSTER["gathot"]["name"] == "Gathot"
        assert WAYANG_ROSTER["gathot"]["title"] == "Wayang Wira Warta"
        assert "threads" in WAYANG_ROSTER["gathot"]["keywords"]
        assert "copywriting" in WAYANG_ROSTER["gathot"]["keywords"]

    def test_total_11_active_specialist_wayang(self):
        # 11 specialist wayang di luar dalang (Risko)
        assert len(WAYANG_ROSTER) == 11

    def test_auto_route_social_media_task(self):
        task_desc = "Buat caption viral di Threads dan riset hashtag FYP untuk produk affiliate celana jeans"
        agent, score = auto_route_task(task_desc)
        assert agent == "gathot"
        assert score > 0.0

    def test_standards_file_mapping(self):
        assert "gathot" in STANDARDS_MAP
        assert STANDARDS_MAP["gathot"] == "gathot_social_standards.md"

    def test_standards_content_loading(self):
        standards = _load_standards("gathot")
        assert "Gathot Social Media Engineering Standards" in standards
        assert "Kurasi Objektif, Bukan Klaim Palsu" in standards

    def test_subagent_prompt_exists(self):
        assert "gathot" in ROLE_PROMPTS
        assert "Social Media & Growth Specialist" in ROLE_PROMPTS["gathot"]
        assert "Never fabricate personal usage claims" in ROLE_PROMPTS["gathot"]
