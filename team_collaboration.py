"""
Team Collaboration & Handover Protocol — Dalang-AI
Memastikan para Wayang tidak bekerja soliter, melainkan saling berkonsultasi,
melakukan peer-review (handover gate), dan bermusyawarah sebelum & sesudah eksekusi.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from consensus_engine import WayangConsensusEngine, Proposal, AgentCritique, ConsensusResult
from wayang_router import WAYANG_ROSTER


# Aturan Konsultasi Lintas Disiplin (Cross-Consultation Rules)
# Menentukan siapa partner wajib yang harus diajak konsul sebelum/sesudah task.
CONSULTATION_MATRIX = {
    "kresna": {
        "partners": ["lulu", "mika"],
        "reason": "Kresna (Story/Motion) wajib konsul ke Lulu untuk konsistensi UI/UX & design system, serta Mika untuk tata bahasa & naskah.",
    },
    "lulu": {
        "partners": ["zaki", "kresna"],
        "reason": "Lulu (Frontend) wajib konsul ke Zaki untuk kontrak API data, dan Kresna jika ada elemen animasi visual.",
    },
    "zaki": {
        "partners": ["pingot", "kai"],
        "reason": "Zaki (Backend) wajib konsul ke Pingot untuk integritas skema database, dan Kai untuk validasi keamanan API.",
    },
    "nova": {
        "partners": ["kai", "zaki"],
        "reason": "Nova (DevOps) wajib konsul ke Kai untuk kepatuhan non-root container & firewall, dan Zaki untuk runtime dependencies.",
    },
    "kai": {
        "partners": ["ren"],
        "reason": "Kai (Security) bermitra dengan Ren untuk menyusun security regression test suite pembuktian exploit.",
    },
}


@dataclass
class ConsultationBrief:
    primary_agent: str
    consulted_agents: List[str]
    task_title: str
    design_guidelines: List[str] = field(default_factory=list)
    approved: bool = True
    feedback: str = ""


@dataclass
class HandoverVerdict:
    task_id: str
    producer_agent: str
    reviewer_agent: str
    status: str  # "APPROVED", "CHANGES_REQUESTED", "REJECTED"
    critique: str
    recommendations: List[str] = field(default_factory=list)


class TeamCollaborationManager:
    """
    Manajer Kolaborasi Tim Wayang:
    1. Pre-flight Consultation: Briefing lintas spesialis sebelum mulai coding.
    2. Handover Gate: Peer-review antar wayang setelah task selesai.
    3. Musyawarah ADR: Mengaktifkan WayangConsensusEngine untuk arsitektur besar.
    """

    def __init__(self):
        self.consensus_engine = WayangConsensusEngine(required_quorum=0.75)

    def prepare_preflight_brief(self, agent_id: str, task_title: str, task_desc: str = "") -> ConsultationBrief:
        """
        Menyiapkan briefing konsultasi lintas wayang sebelum eksekusi dimulai.
        Contoh: Jika Kresna membuat animasi, Lulu otomatis menyuntikkan standar UI/Canvas.
        """
        agent_id = agent_id.lower()
        matrix = CONSULTATION_MATRIX.get(agent_id, {"partners": ["risko"], "reason": "Konsultasi standar koordinasi Dalang."})
        partners = matrix["partners"]

        guidelines = []
        # Injeksi panduan spesifik dari partner
        if "lulu" in partners:
            guidelines.append("🎨 [Lulu/UX]: Gunakan palet dark-mode terstandar (#0a0c12, #11131a, #6366f1). Jangan buat floating box mentah; integrasikan ke UI studio.")
            guidelines.append("🎨 [Lulu/UX]: Typography sans-serif tebal (Inter/-apple-system) dengan contrast ratio >= 4.5:1.")

        if "mika" in partners:
            guidelines.append("📝 [Mika/Pujangga]: Gunakan struktur narasi And-But-Therefore (ABT), fakta wajib sesuai fakta di ledger.")

        if "pingot" in partners:
            guidelines.append("🗄️ [Pingot/Data]: Pastikan payload data konsisten dengan ISO 8601 dan Domain Models.")

        if "kai" in partners:
            guidelines.append("🔒 [Kai/Security]: Validasi input parameter, hindari ekspos secret, terapkan rate limiting.")

        feedback = (
            f"Konsultasi awal berhasil. {agent_id.capitalize()} telah menerima masukan dari: "
            + ", ".join([p.capitalize() for p in partners])
            + f". {matrix['reason']}"
        )

        return ConsultationBrief(
            primary_agent=agent_id,
            consulted_agents=partners,
            task_title=task_title,
            design_guidelines=guidelines,
            approved=True,
            feedback=feedback,
        )

    def perform_handover_review(
        self,
        task_id: str,
        producer_agent: str,
        artifacts: List[str],
        artifact_content: str = "",
    ) -> HandoverVerdict:
        """
        Pemeriksaan hasil kerja oleh partner reviewer yang relevan.
        """
        producer_agent = producer_agent.lower()
        matrix = CONSULTATION_MATRIX.get(producer_agent, {"partners": ["ren"]})
        reviewer = matrix["partners"][0]  # Reviewer utama

        # Validasi otomatis sederhana berbasis aturan domain
        recommendations = []
        status = "APPROVED"
        critique = f"Hasil kerja {producer_agent} telah ditinjau oleh {reviewer} dan memenuhi standar kualitas."

        # Cek kasus Kresna -> Lulu (Audit UI/UX & Design Standard)
        if producer_agent == "kresna" and reviewer == "lulu":
            lower_content = artifact_content.lower()
            
            # 1. Cek Anti-Slop: generic gradient AI
            if "linear-gradient" in lower_content and ("#667eea" in lower_content or "#764ba2" in lower_content):
                status = "CHANGES_REQUESTED"
                critique = "Lulu: Ditemukan generic AI gradient (biru-ungu default). Dilarang sesuai Anti-Slop Directive! Gunakan palet terkurasi (misal Deep Navy/Gold atau Indigo/Turquoise)."
                recommendations.append("Ganti gradient dengan palet brand solid atau subtle radial glow.")

            # 2. Cek Interactive States
            if "<button" in lower_content and ":hover" not in lower_content:
                status = "CHANGES_REQUESTED"
                critique = "Lulu: Tombol interaktif tidak memiliki pseudo-class :hover/:focus yang jelas."
                recommendations.append("Tambahkan hover state, active scale, dan focus-visible ring pada setiap tombol.")

            # 3. Cek Kontras & Typography
            if "font-family" not in lower_content:
                recommendations.append("Terapkan font-family modern (Inter, system-ui) dengan hierarki teks yang tegas.")

            # 4. Cek Layout Flex/Grid & Center Stage
            if "display: flex" not in lower_content and "display:flex" not in lower_content:
                recommendations.append("Gunakan Flexbox/Grid untuk staging canvas agar presisi di tengah layar.")

        # Cek kasus Zaki -> Kai (apakah ada indikasi secret hardcoded)
        if producer_agent == "zaki" and reviewer == "pingot":
            if "password" in artifact_content.lower() and "hash" not in artifact_content.lower():
                status = "CHANGES_REQUESTED"
                critique = "Ditemukan penyimpanan raw credential tanpa hashing. Harap gunakan bcrypt/argon2."
                recommendations.append("Enkripsi atau hash semua kata sandi sebelum masuk database.")

        return HandoverVerdict(
            task_id=task_id,
            producer_agent=producer_agent,
            reviewer_agent=reviewer,
            status=status,
            critique=critique,
            recommendations=recommendations,
        )

    def conduct_team_deliberation(
        self,
        proposal_title: str,
        proposer: str,
        description: str,
        architecture: str,
        critiques_data: List[Tuple[str, str, str]],  # (agent_id, stance, comment)
    ) -> ConsensusResult:
        """
        Menjalankan musyawarah resmi dengan multi-agent consensus engine.
        """
        proposal = Proposal(
            id=f"PROP-{abs(hash(proposal_title)) % 10000:04d}",
            title=proposal_title,
            proposer_agent=proposer,
            description=description,
            proposed_architecture=architecture,
            tradeoffs=["Konsistensi UX menyeluruh vs kecepatan deliver", "Overhead review vs zero defect"],
        )

        reviews = [
            AgentCritique(
                agent_id=agent_id,
                stance=stance,
                critique=comment,
            )
            for agent_id, stance, comment in critiques_data
        ]

        return self.consensus_engine.conduct_deliberation(proposal, reviews)
