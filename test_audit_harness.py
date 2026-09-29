"""
Test Suite untuk Cloudflare-Grade Security Audit Harness & Adversarial Verifier
"""

import pytest
import json
import tempfile
from pathlib import Path

from audit_harness import CloudflareAuditHarness, CoverageUnit, FindingRecord


class TestCloudflareAuditHarness:
    def test_coverage_ledger_registration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            harness = CloudflareAuditHarness(tmpdir)
            u1 = harness.register_coverage_unit("UNIT-01", "auth_api.py", "API_ENDPOINT", hunter="kai")
            assert u1.unit_id == "UNIT-01"
            assert u1.status == "pending"

            ok = harness.record_hunting_pass("UNIT-01", ["AUTH_BYPASS", "TOKEN_TAMPER"])
            assert ok is True
            assert harness.ledger["UNIT-01"].status == "covered"
            assert "TOKEN_TAMPER" in harness.ledger["UNIT-01"].checked_attack_classes

    def test_adversarial_validation_disproved_rejected(self):
        """Uji sangkal: Verifier berhasil menyangkal bug karena kontrol mitigasi sudah ada (Zero False Positive)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness = CloudflareAuditHarness(tmpdir)
            f = harness.validate_candidate_adversarially(
                finding_id="CAND-001",
                title="Potential Timing Attack in Token Check",
                target_path="token_service.py",
                attack_class="SIDE_CHANNEL_TIMING",
                claimed_severity="HIGH",
                candidate_claim="Perbandingan string token terindikasi non-constant time.",
                reproducible_evidence="inspect token_service.py: line 45",
                mitigating_controls_exist=True,
                disprove_rationale="Kode menggunakan hmac.compare_digest secara eksplisit, bukan `==`. Klaim terbantahkan.",
            )

            assert f.verdict == "rejected"
            assert f.severity is None
            assert "DISPROVED BY VERIFIER" in f.disprove_attempt_notes

    def test_adversarial_validation_confirmed(self):
        """Uji sangkal: Verifier gagal membantah -> bug terkonfirmasi 100% nyata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness = CloudflareAuditHarness(tmpdir)
            f = harness.validate_candidate_adversarially(
                finding_id="CAND-002",
                title="Missing Rate Limiting on Login Endpoint",
                target_path="auth_api.py",
                attack_class="RESOURCE_EXHAUSTION",
                claimed_severity="MEDIUM",
                candidate_claim="Endpoint /api/login dapat di-bruteforce tanpa batas rate limit.",
                reproducible_evidence="POST /api/login 500x in 2s -> all return 401 without 429",
                mitigating_controls_exist=False,
            )

            assert f.verdict == "confirmed"
            assert f.severity == "MEDIUM"
            assert len(f.remediation_steps) >= 1

    def test_export_json_and_markdown_reports(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            harness = CloudflareAuditHarness(tmpdir)
            harness.register_coverage_unit("UNIT-01", "main.py", "API_ENDPOINT")
            harness.record_hunting_pass("UNIT-01", ["INJECTION"])

            harness.validate_candidate_adversarially(
                finding_id="CAND-003",
                title="SQL Injection in raw string query",
                target_path="db.py",
                attack_class="INJECTION",
                claimed_severity="CRITICAL",
                candidate_claim="Query memakai f-string",
                reproducible_evidence="f'SELECT * FROM users WHERE id={id}'",
                mitigating_controls_exist=False,
            )

            json_str = harness.export_findings_json()
            payload = json.loads(json_str)
            assert payload["findings_summary"]["confirmed"] == 1
            assert payload["total_units_covered"] == 1

            reports = harness.generate_audit_reports()
            assert "REPORT.md" in reports
            assert "FINDINGS-DETAIL.md" in reports
            assert "Cloudflare-Grade Security Audit Report" in reports["REPORT.md"]
            assert "CAND-003" in reports["REPORT.md"]
