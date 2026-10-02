"""
Test Suite untuk Wayang Router (Auto-Routing Risko)
Memastikan Risko cerdas dalam menunjuk Wayang yang tepat dan menidurkan wayang idle.
"""

import pytest
from wayang_router import auto_route_task, partition_active_and_idle_wayang, WAYANG_ROSTER


class TestAutoRouting:
    """Uji coba kecerdasan Risko mengenali peran tiap wayang."""

    def test_route_data_task_to_pingot(self):
        title = "Rancang skema database PostgreSQL untuk katalog produk"
        agent, score = auto_route_task(title)
        assert agent == "pingot"
        assert score > 0

    def test_route_backend_task_to_zaki(self):
        title = "Buat REST API endpoint FastAPI untuk registrasi dan login JWT"
        agent, score = auto_route_task(title)
        assert agent == "zaki"
        assert score > 0

    def test_route_frontend_task_to_lulu(self):
        title = "Buat antarmuka kalkulator web dengan CSS responsif dan button interaktif"
        agent, score = auto_route_task(title)
        assert agent == "lulu"
        assert score > 0

    def test_route_documentation_task_to_mika(self):
        title = "Tulis dokumentasi QUICKSTART panduan penggunaan sistem"
        agent, score = auto_route_task(title)
        assert agent == "mika"
        assert score > 0

    def test_route_devops_task_to_nova(self):
        title = "Buat Dockerfile dan GitHub Actions CI/CD workflow untuk automated deployment"
        agent, score = auto_route_task(title)
        assert agent == "nova"
        assert score > 0

    def test_route_security_task_to_kai(self):
        title = "Audit keamanan OWASP ASVS dan scan vulnerability bandit pada endpoint auth"
        agent, score = auto_route_task(title)
        assert agent == "kai"
        assert score > 0

    def test_route_qa_task_to_ren(self):
        title = "Tulis unit test dan integration test dengan pytest untuk verifikasi skenario login"
        agent, score = auto_route_task(title)
        assert agent == "ren"
        assert score > 0

    def test_route_reverse_engineering_to_kai(self):
        """Keahlian baru dari reverse-skill harus di-route ke Kai."""
        title = "Decompile APK dan analisis deobfuscation binary untuk audit anti-tamper dan sbom"
        agent, score = auto_route_task(title)
        assert agent == "kai"
        assert score > 0

    def test_route_api_hardening_to_zaki(self):
        """Countermeasure pertahanan backend harus di-route ke Zaki."""
        title = "Implementasi api hardening dengan rate limit dan signature verification di server route"
        agent, score = auto_route_task(title)
        assert agent == "zaki"
        assert score > 0

    def test_route_security_regression_to_ren(self):
        """Verifikasi test security dan regression test harus di-route ke Ren."""
        title = "Tulis security test dan regression test otomatis untuk poc verification"
        agent, score = auto_route_task(title)
        assert agent == "ren"
        assert score > 0

    def test_explicit_agent_override(self):
        """Jika user sengaja menulis nama agent, pilihan user harus dihormati."""
        title = "Buat sesuatu yang umum"
        agent, score = auto_route_task(title, explicit_agent="nova")
        assert agent == "nova"


class TestWayangIdlePartition:
    """Uji coba partisi wayang aktif vs wayang yang diam."""

    def test_partial_assignment_leaves_others_idle(self):
        """Proyek kalkulator hanya butuh Lulu (UI), Zaki (Logic), Ren (Test). Sisanya diam."""
        tasks = [
            {"id": "T-001", "assigned": "lulu"},
            {"id": "T-002", "assigned": "zaki"},
            {"id": "T-003", "assigned": "ren"},
        ]
        status = partition_active_and_idle_wayang(tasks)

        assert status["total_active"] == 3
        assert status["total_idle"] == 7  # 10 wayang total (termasuk Wiku, Kresna & Bagong) - 3 aktif = 7 idle (termasuk Wiku & Kresna) - 3 aktif = 6 idle
        assert "lulu" in status["active"]
        assert "zaki" in status["active"]
        assert "ren" in status["active"]
        assert "pingot" in status["idle"]
        assert "mika" in status["idle"]
        assert "nova" in status["idle"]
        assert "kai" in status["idle"]
        assert "wiku" in status["idle"]
        assert "kresna" in status["idle"]
        assert "bagong" in status["idle"]

    def test_route_storytelling_task_to_kresna(self):
        title = "Buatkan animasi explainer dan skenario cerita arsitektur"
        desc = "Gunakan format And-But-Therefore dengan karakter Canvas 2D untuk presentasi klien"
        agent, conf = auto_route_task(title, desc)
        assert agent == "kresna"
        assert conf > 0.0
