"""
Evidence Tracker — Pelacakan Rantai Bukti (Evidence → Finding → Path) untuk Dalang-AI
Terinspirasi dari ops/evidence-finding-path.md di zhaoxuya520/reverse-skill

Menjamin zero-hallucination pada audit keamanan dan pengujian:
Setiap temuan harus memiliki bukti nyata (Evidence E-xxx) yang dapat direproduksi,
dipetakan ke Finding (F-xxx) dengan CVSS v3.1 & CWE, serta jalur remediasi konkret.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Evidence:
    id: str  # e.g., E-001
    title: str
    severity: str  # critical, high, medium, low, info
    status: str  # observed, validated, false_positive
    source_type: str  # command, test, code_inspection
    repro_command: str  # command or script to reproduce 100%
    observed_output: str
    discovered_by: str = "kai"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Finding:
    id: str  # e.g., F-001
    title: str
    cwe_id: str  # e.g., CWE-287, CWE-89
    cvss_score: float  # e.g., 7.5
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    description: str
    evidence_ids: List[str]  # links to Evidence.id
    remediation_steps: List[str]
    assigned_fixer: str  # zaki, lulu, nova
    verifier: str = "ren"
    status: str = "OPEN"  # OPEN, IN_PROGRESS, RESOLVED, VERIFIED


class EvidenceRegistry:
    """Manajer registrasi bukti dan temuan keamanan."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir) if storage_dir else Path(__file__).parent / "audit_cases"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_list: List[Evidence] = []
        self.finding_list: List[Finding] = []

    def add_evidence(
        self,
        evidence_id: str,
        title: str,
        severity: str,
        repro_command: str,
        observed_output: str,
        source_type: str = "test",
        status: str = "validated",
        discovered_by: str = "kai",
    ) -> Evidence:
        ev = Evidence(
            id=evidence_id,
            title=title,
            severity=severity.lower(),
            status=status,
            source_type=source_type,
            repro_command=repro_command,
            observed_output=observed_output,
            discovered_by=discovered_by,
        )
        self.evidence_list.append(ev)
        return ev

    def add_finding(
        self,
        finding_id: str,
        title: str,
        cwe_id: str,
        cvss_score: float,
        description: str,
        evidence_ids: List[str],
        remediation_steps: List[str],
        assigned_fixer: str = "zaki",
    ) -> Finding:
        if cvss_score >= 9.0:
            sev = "CRITICAL"
        elif cvss_score >= 7.0:
            sev = "HIGH"
        elif cvss_score >= 4.0:
            sev = "MEDIUM"
        else:
            sev = "LOW"

        f = Finding(
            id=finding_id,
            title=title,
            cwe_id=cwe_id,
            cvss_score=cvss_score,
            severity=sev,
            description=description,
            evidence_ids=evidence_ids,
            remediation_steps=remediation_steps,
            assigned_fixer=assigned_fixer,
        )
        self.finding_list.append(f)
        return f

    def export_summary(self) -> Dict:
        return {
            "evidence_count": len(self.evidence_list),
            "findings_count": len(self.finding_list),
            "evidence": [asdict(e) for e in self.evidence_list],
            "findings": [asdict(f) for f in self.finding_list],
        }
