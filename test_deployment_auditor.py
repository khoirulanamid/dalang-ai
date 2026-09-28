"""
Test Suite untuk Pre-Deployment Gate & GO/NO-GO Auditor
"""

import pytest
import tempfile
from pathlib import Path

from deployment_auditor import DeploymentAuditor, DeploymentVerdict


class TestDeploymentAuditor:
    def test_clean_workspace_gets_go_verdict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            # Create a mock test file and a clean Dockerfile with healthcheck
            (ws / "test_sample.py").write_text("def test_ok(): assert True")
            (ws / "Dockerfile").write_text("FROM python:3.11-slim\nHEALTHCHECK CMD exit 0")

            auditor = DeploymentAuditor(str(ws))
            verdict = auditor.run_full_preflight_audit("Test Clean App")

            assert isinstance(verdict, DeploymentVerdict)
            assert verdict.verdict == "GO"
            assert verdict.failed_blockers == 0
            assert verdict.passed_count >= 3

            report = auditor.generate_markdown_report(verdict)
            assert "VERDICT: GO" in report

    def test_exposed_env_triggers_no_go_blocker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            (ws / "test_sample.py").write_text("def test_ok(): assert True")
            # Insecure: .env committed in workspace
            (ws / ".env").write_text("SECRET_KEY=leaked_production_secret")

            auditor = DeploymentAuditor(str(ws))
            verdict = auditor.run_full_preflight_audit("Insecure App")

            assert verdict.verdict == "NO-GO"
            assert verdict.failed_blockers >= 1
            assert any(item.id == "DEP-SEC-01" and item.status == "FAIL" for item in verdict.items)

            report = auditor.generate_markdown_report(verdict)
            assert "VERDICT: NO-GO" in report
            assert "Ditemukan file .env" in report

    def test_missing_tests_triggers_qa_blocker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            # No test files at all

            auditor = DeploymentAuditor(str(ws))
            verdict = auditor.run_full_preflight_audit("No Tests App")

            assert verdict.verdict == "NO-GO"
            assert any(item.id == "DEP-QA-01" and item.status == "FAIL" for item in verdict.items)
