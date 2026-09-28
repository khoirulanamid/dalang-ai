"""
Test Suite untuk Integrasi Komprehensif Arsitektur Reverse-Skill ke Dalang-AI
Menguji:
1. Field Journal (Self-Evolving Knowledge Base & Pitfalls Injection)
2. Scope Guard (Workspace Path & Network Boundary Protection)
3. Evidence Tracker & Security Reporter (Zero-Hallucination Evidence Chain)
4. Toolchain Bootstrapper & Status Audit
"""

import pytest
from pathlib import Path
import tempfile
import os

from field_journal import (
    record_journal_entry,
    list_journal_entries,
    query_journal_learnings,
    ensure_journal_dirs,
)
from scope_guard import (
    validate_path_in_scope,
    validate_network_target,
    ScopeViolationError,
)
from evidence_tracker import EvidenceRegistry
from security_reporter import SecurityReporter
from toolchain_bootstrap import check_tool_available, audit_full_toolchain, get_bootstrap_recipe


class TestFieldJournal:
    """Menguji sistem ingatan empiris dan pencegahan error berulang."""

    def test_record_and_list_entries(self):
        entry = record_journal_entry(
            title="Uji Coba Test Precedent",
            category="test-category",
            agent_id="kai",
            summary="Ini adalah ringkasan pengujian unit test.",
            pitfalls=["Jebakan testing 1", "Jebakan testing 2"],
            solution="Solusi testing yang bekerja.",
            tags=["unit-test", "verification"],
        )
        assert entry["id"].startswith("JRN-")
        assert entry["agent_id"] == "kai"

        entries = list_journal_entries(agent_id="kai", category="test-category")
        assert any(e["id"] == entry["id"] for e in entries)

    def test_query_journal_learnings_injection(self):
        context = "Saya ingin memperbaiki tiga dimensi avatar Three.js kinematics rotasi paha"
        learnings = query_journal_learnings(context, agent_id="lulu")
        assert "PRECEDENT & FIELD JOURNAL LEARNINGS" in learnings
        assert "Rotasi Sendi Three.js Sumbu X Avatar Humanoid Duduk" in learnings
        assert "⚠️ Menggunakan rotation.x negatif" in learnings


class TestScopeGuard:
    """Menguji batasan scope kontrak pengerjaan agent."""

    def test_path_inside_scope_allowed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            safe_file = os.path.join(tmpdir, "subdir", "test.py")
            resolved = validate_path_in_scope(safe_file, tmpdir)
            assert str(resolved).startswith(tmpdir)

    def test_path_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evil_path = os.path.join(tmpdir, "..", "..", "etc", "passwd")
            with pytest.raises(ScopeViolationError):
                validate_path_in_scope(evil_path, tmpdir)

    def test_network_target_scope(self):
        assert validate_network_target("http://127.0.0.1:8765/agents/status") is True
        assert validate_network_target("http://localhost:5173") is True
        with pytest.raises(ScopeViolationError):
            validate_network_target("http://malicious-external-site.com/steal")


class TestEvidenceAndSecurityReporter:
    """Menguji rantai bukti empiris dan generator laporan audit Mika."""

    def test_evidence_finding_lifecycle(self):
        reg = EvidenceRegistry()
        ev = reg.add_evidence(
            evidence_id="E-101",
            title="JWT Signature Bypassed with Alg None",
            severity="critical",
            repro_command="pytest workspace/test_security.py -k test_jwt_none",
            observed_output="HTTP 200 instead of 401",
        )
        assert ev.id == "E-101"

        finding = reg.add_finding(
            finding_id="F-101",
            title="JWT Algorithm Confusion Vulnerability",
            cwe_id="CWE-327",
            cvss_score=9.1,
            description="Server accepts token with alg: none header.",
            evidence_ids=["E-101"],
            remediation_steps=[
                "Enforce algorithms=['HS256'] explicitly in jwt.decode().",
                "Reject all tokens with missing or none algorithms."
            ],
            assigned_fixer="zaki",
        )
        assert finding.severity == "CRITICAL"

        reporter = SecurityReporter(reg)
        report_md = reporter.generate_markdown_report("Dalang-AI Auth Engine", "workspace/")
        assert "Laporan Audit Keamanan" in report_md
        assert "E-101" in report_md
        assert "F-101" in report_md
        assert "CRITICAL" in report_md
        assert "Enforce algorithms=['HS256']" in report_md


class TestToolchainBootstrap:
    """Menguji audit ketersediaan toolchain Nova."""

    def test_python_and_git_available(self):
        py_status = check_tool_available("python")
        git_status = check_tool_available("git")
        assert py_status["available"] is True
        assert git_status["available"] is True

    def test_audit_full_toolchain(self):
        full = audit_full_toolchain()
        assert "pytest" in full
        assert "node" in full
        assert "git" in full

    def test_bootstrap_recipe_known(self):
        recipe = get_bootstrap_recipe("bandit")
        assert recipe is not None
        assert "pip install" in recipe
        assert "bandit" in recipe
