"""
Cloudflare-Grade Multi-Phase Security Audit Harness & Adversarial Verifier
Terinspirasi dari cloudflare/security-audit-skill

Mengimplementasikan 6-fase audit terstruktur:
1. Reconnaissance & Coverage Ledger (memetakan seluruh unit dan permukaan input)
2. Coverage-led Hunting (Kai memburu kandidat celah keamanan)
3. Adversarial Candidate Validation (Ren / Verifier independen berusaha MENYANGKAL / DISPROVE temuan)
4. Machine-Readable Structured Findings (confirmed, needs_validation, rejected)
5. Zero False-Positive Evidence Discipline
"""

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CoverageUnit:
    unit_id: str
    target_path: str
    surface_type: str  # API_ENDPOINT, AUTH_FLOW, DATA_MODEL, CLI, WEBSOCKET
    hunter: str = "kai"
    status: str = "pending"  # pending, hunting, covered
    checked_attack_classes: List[str] = field(default_factory=list)


@dataclass
class FindingRecord:
    finding_id: str
    title: str
    target_path: str
    attack_class: str
    verdict: str  # "confirmed", "needs_validation", "rejected"
    severity: Optional[str] = None  # CRITICAL, HIGH, MEDIUM, LOW (None if rejected/needs_validation)
    candidate_claim: str = ""
    reproducible_evidence: str = ""
    disprove_attempt_notes: str = ""
    remediation_steps: List[str] = field(default_factory=list)
    verifier_agent: str = "ren"
    verified_at: float = field(default_factory=time.time)


class CloudflareAuditHarness:
    """
    Harness audit keamanan multi-agent berstandar Cloudflare Vulnerability Discovery.
    Menerapkan Coverage Ledger dan Adversarial Validation untuk mengeliminasi false positive.
    """

    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path).resolve()
        self.ledger: Dict[str, CoverageUnit] = {}
        self.findings: Dict[str, FindingRecord] = {}

    def register_coverage_unit(
        self,
        unit_id: str,
        target_path: str,
        surface_type: str,
        hunter: str = "kai",
    ) -> CoverageUnit:
        """Fase 1: Mendaftarkan unit kode ke dalam Coverage Ledger."""
        unit = CoverageUnit(
            unit_id=unit_id,
            target_path=target_path,
            surface_type=surface_type,
            hunter=hunter,
            status="pending",
        )
        self.ledger[unit_id] = unit
        return unit

    def record_hunting_pass(
        self,
        unit_id: str,
        attack_classes: List[str],
    ) -> bool:
        """Fase 2: Mencatat cakupan pengujian yang telah selesai disisir oleh Hunter."""
        if unit_id not in self.ledger:
            return False
        unit = self.ledger[unit_id]
        unit.status = "covered"
        unit.checked_attack_classes.extend(attack_classes)
        return True

    def validate_candidate_adversarially(
        self,
        finding_id: str,
        title: str,
        target_path: str,
        attack_class: str,
        claimed_severity: str,
        candidate_claim: str,
        reproducible_evidence: str,
        mitigating_controls_exist: bool,
        disprove_rationale: str = "",
        unresolved_facts: Optional[str] = None,
    ) -> FindingRecord:
        """
        Fase 3 & 4: Adversarial Candidate Validation (Uji Sangkal Temuan).
        Verifier independen (Ren) secara aktif mencari kontrol mitigasi yang ada untuk
        membantah/menyangkal kandidat temuan dari hunter (Kai).
        """
        # Skenario A: Celah berhasil disangkal (mitigasi sudah ada / false positive)
        if mitigating_controls_exist:
            record = FindingRecord(
                finding_id=finding_id,
                title=title,
                target_path=target_path,
                attack_class=attack_class,
                verdict="rejected",
                severity=None,
                candidate_claim=candidate_claim,
                reproducible_evidence=reproducible_evidence,
                disprove_attempt_notes=f"DISPROVED BY VERIFIER: {disprove_rationale}",
                verifier_agent="ren",
            )
        # Skenario B: Bukti belum konklusif / ada fakta yang belum pasti
        elif unresolved_facts:
            record = FindingRecord(
                finding_id=finding_id,
                title=title,
                target_path=target_path,
                attack_class=attack_class,
                verdict="needs_validation",
                severity=None,
                candidate_claim=candidate_claim,
                reproducible_evidence=reproducible_evidence,
                disprove_attempt_notes=f"UNRESOLVED FACT: {unresolved_facts}",
                verifier_agent="ren",
            )
        # Skenario C: Lolos uji sangkal (Confirmed Vulnerability)
        else:
            record = FindingRecord(
                finding_id=finding_id,
                title=title,
                target_path=target_path,
                attack_class=attack_class,
                verdict="confirmed",
                severity=claimed_severity.upper(),
                candidate_claim=candidate_claim,
                reproducible_evidence=reproducible_evidence,
                disprove_attempt_notes="Adversarial verification attempted and failed to disprove. Finding confirmed.",
                remediation_steps=[
                    f"Terapkan validasi input ketat pada {target_path}",
                    "Buat unit test regresi di Pytest untuk memverifikasi patch."
                ],
                verifier_agent="ren",
            )

        self.findings[finding_id] = record
        return record

    def export_findings_json(self) -> str:
        """Fase 4: Export temuan terstruktur machine-readable."""
        payload = {
            "audit_standard": "Cloudflare-Grade Multi-Phase Audit",
            "total_units_covered": sum(1 for u in self.ledger.values() if u.status == "covered"),
            "total_ledger_units": len(self.ledger),
            "findings_summary": {
                "confirmed": sum(1 for f in self.findings.values() if f.verdict == "confirmed"),
                "needs_validation": sum(1 for f in self.findings.values() if f.verdict == "needs_validation"),
                "rejected": sum(1 for f in self.findings.values() if f.verdict == "rejected"),
            },
            "findings": [asdict(f) for f in self.findings.values()],
        }
        return json.dumps(payload, indent=2)

    def generate_audit_reports(self) -> Dict[str, str]:
        """Fase 6: Men-generate REPORT.md dan FINDINGS-DETAIL.md."""
        confirmed_list = [f for f in self.findings.values() if f.verdict == "confirmed"]
        rejected_list = [f for f in self.findings.values() if f.verdict == "rejected"]
        needs_val_list = [f for f in self.findings.values() if f.verdict == "needs_validation"]

        # REPORT.md (Executive Summary)
        report_md = [
            "# Cloudflare-Grade Security Audit Report",
            f"\n- **Workspace Target**: `{self.workspace}`",
            f"- **Coverage Ledger Units**: {len(self.ledger)} (Covered: {sum(1 for u in self.ledger.values() if u.status == 'covered')})",
            f"- **Confirmed Vulnerabilities**: {len(confirmed_list)}",
            f"- **Disproved / Rejected Candidates (Zero False Positive)**: {len(rejected_list)}",
            f"- **Needs Validation**: {len(needs_val_list)}\n",
            "## Matriks Temuan Terkonfirmasi",
            "| ID | Keparahan | Judul Celah | Target | Attack Class | Status Uji Sangkal |",
            "|:---|:---:|:---|:---|:---|:---|",
        ]

        for f in confirmed_list:
            report_md.append(f"| `{f.finding_id}` | **{f.severity}** | {f.title} | `{f.target_path}` | {f.attack_class} | ✅ Lolos Uji Sangkal |")

        if not confirmed_list:
            report_md.append("| - | - | *Zero Confirmed Vulnerabilities (Semua kandidat lolos/tersaring)* | - | - | - |")

        # FINDINGS-DETAIL.md (Technical Detail & Proofs)
        detail_md = [
            "# Detailed Findings & Adversarial Disprove Log",
            "\nDokumen ini merangkum bukti reproduksi dan analisis uji sangkal verifier.\n"
        ]

        for f in self.findings.values():
            detail_md.extend([
                f"### [{f.verdict.upper()}] {f.finding_id}: {f.title}",
                f"- **Target File**: `{f.target_path}`",
                f"- **Attack Class**: `{f.attack_class}`",
                f"- **Verdict**: `{f.verdict}` (Severity: {f.severity or 'N/A'})",
                f"- **Klaim Hunter (Kai)**: {f.candidate_claim}",
                f"- **Bukti Reproduksi**: `{f.reproducible_evidence}`",
                f"- **Catatan Verifier (Ren)**: {f.disprove_attempt_notes}",
                ""
            ])

        return {
            "REPORT.md": "\n".join(report_md),
            "FINDINGS-DETAIL.md": "\n".join(detail_md),
        }
