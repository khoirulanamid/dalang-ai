"""
Multi-Agent Consensus & Debate Protocol (Musyawarah Para Wayang) — Dalang-AI
Terinspirasi dari riset Stanford Multi-Agent & Architecture Decision Records (ADR).

Memfasilitasi musyawarah teknis antar-Wayang sebelum eksekusi tugas besar:
- Risko: Moderator & Pembuat Keputusan Akhir
- Pingot: Reviewer Skema & Integritas Data
- Zaki: Reviewer Efisiensi API & Backend
- Kai: Reviewer Keamanan & Anti-Tamper (Veto Power untuk isu keamanan kritis)
- Ren: Reviewer Testabilitas & Verifikasi Mutu

Mencegah keputusan teknis sepihak dan menghasilkan Architecture Decision Record (ADR) resmi.
"""

import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class AgentCritique:
    agent_id: str
    stance: str  # "APPROVE", "OBJECT", "NEUTRAL"
    critique: str
    concerns: List[str] = field(default_factory=list)
    suggested_amendment: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class Proposal:
    id: str
    title: str
    proposer_agent: str
    description: str
    proposed_architecture: str
    tradeoffs: List[str] = field(default_factory=list)


@dataclass
class ConsensusResult:
    proposal_id: str
    title: str
    status: str  # "CONSENSUS_REACHED", "AMENDMENT_REQUIRED", "VETOED"
    approval_percentage: float
    reviews: List[AgentCritique] = field(default_factory=list)
    synthesis: str = ""
    adr_markdown: str = ""


class WayangConsensusEngine:
    """
    Engine Musyawarah Teknis Multi-Agent.
    Mengevaluasi usulan arsitektur melalui peer review terstruktur.
    """

    def __init__(self, required_quorum: float = 0.75):
        self.required_quorum = required_quorum  # Minimal 75% approval untuk lolos

    def conduct_deliberation(
        self,
        proposal: Proposal,
        reviews: List[AgentCritique],
    ) -> ConsensusResult:
        """
        Menghitung konsensus berdasarkan review dari para Wayang.
        Aturan Khusus (Security Veto):
        Jika Kai (Security) menyatakan "OBJECT" dengan alasan keamanan kritis,
        proposal otomatis VETOED hingga ada mitigasi nyata.
        """
        total_reviewers = len(reviews)
        if total_reviewers == 0:
            return ConsensusResult(
                proposal_id=proposal.id,
                title=proposal.title,
                status="AMENDMENT_REQUIRED",
                approval_percentage=0.0,
                synthesis="Tidak ada review yang masuk.",
            )

        # 1. Cek Hak Veto Keamanan (Kai Veto Check)
        kai_review = next((r for r in reviews if r.agent_id == "kai"), None)
        if kai_review and kai_review.stance == "OBJECT":
            return ConsensusResult(
                proposal_id=proposal.id,
                title=proposal.title,
                status="VETOED",
                approval_percentage=0.0,
                reviews=reviews,
                synthesis=f"PROPOSAL DI-VETO OLEH KAI: {kai_review.critique}. Diperlukan mitigasi keamanan sebelum musyawarah diulang.",
                adr_markdown=self._format_adr(proposal, reviews, "VETOED"),
            )

        # 2. Hitung Persentase Persetujuan
        approvals = sum(1 for r in reviews if r.stance == "APPROVE")
        approval_rate = approvals / total_reviewers

        status = "CONSENSUS_REACHED" if approval_rate >= self.required_quorum else "AMENDMENT_REQUIRED"
        synthesis = (
            f"Musyawarah mencapai konsensus bulat ({round(approval_rate * 100, 1)}% persetujuan). Arsitektur disetujui untuk sprint."
            if status == "CONSENSUS_REACHED"
            else f"Konsensus belum tercapai ({round(approval_rate * 100, 1)}% persetujuan < target {int(self.required_quorum * 100)}%). Diperlukan revisi usulan."
        )

        adr_doc = self._format_adr(proposal, reviews, status)

        return ConsensusResult(
            proposal_id=proposal.id,
            title=proposal.title,
            status=status,
            approval_percentage=round(approval_rate * 100, 1),
            reviews=reviews,
            synthesis=synthesis,
            adr_markdown=adr_doc,
        )

    def _format_adr(self, proposal: Proposal, reviews: List[AgentCritique], status: str) -> str:
        """Menghasilkan dokumen resmi Architecture Decision Record (ADR)."""
        badge = "🟢 DITERIMA (APPROVED)" if status == "CONSENSUS_REACHED" else ("🔴 DITOLAK (VETOED)" if status == "VETOED" else "🟡 PERLU REVISI (AMENDMENT)")
        
        lines = [
            f"# Architecture Decision Record (ADR): {proposal.title}",
            f"\n- **ID Proposal**: `{proposal.id}`",
            f"- **Pengusul**: Wayang `{proposal.proposer_agent}`",
            f"- **Status Konsensus**: {badge}",
            f"- **Tanggal Evaluasi**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}",
            "\n## 1. Konteks & Kebutuhan Arsitektur",
            proposal.description,
            "\n## 2. Usulan Arsitektur & Perubahan",
            proposal.proposed_architecture,
            "\n## 3. Catatan Trade-Offs",
        ]
        for t in proposal.tradeoffs:
            lines.append(f"- ⚖️ {t}")

        lines.extend([
            "\n## 4. Musyawarah & Pandangan Para Wayang",
            "| Wayang | Sikap | Catatan Kritis / Saran Masukan |",
            "|:---|:---:|:---|",
        ])

        for r in reviews:
            icon = "✅ APPROVE" if r.stance == "APPROVE" else ("❌ OBJECT" if r.stance == "OBJECT" else "⚪ NEUTRAL")
            lines.append(f"| **{r.agent_id.upper()}** | {icon} | {r.critique} |")

        return "\n".join(lines)
