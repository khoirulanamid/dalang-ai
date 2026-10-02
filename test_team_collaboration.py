"""
Test Suite: Team Collaboration, Pre-flight Consultation & Handover Gate — Dalang-AI
Memverifikasi bahwa para Wayang saling berkonsultasi, berkoordinasi, dan mereview artefak.
"""

import pytest
from team_collaboration import (
    TeamCollaborationManager,
    ConsultationBrief,
    HandoverVerdict,
    CONSULTATION_MATRIX,
)


class TestTeamCollaboration:

    def setup_method(self):
        self.collab = TeamCollaborationManager()

    def test_kresna_preflight_consults_lulu_and_mika(self):
        """Kresna membuat animasi -> wajib menerima standar UI dari Lulu dan naskah dari Mika."""
        brief = self.collab.prepare_preflight_brief(
            agent_id="kresna",
            task_title="Buat video explainer arsitektur Dalang-AI",
        )
        assert "lulu" in brief.consulted_agents
        assert "mika" in brief.consulted_agents
        assert any("Lulu/UX" in g for g in brief.design_guidelines)
        assert any("Mika/Pujangga" in g for g in brief.design_guidelines)

    def test_zaki_preflight_consults_pingot_and_kai(self):
        """Zaki membuat API endpoint -> wajib menerima aturan skema Pingot & keamanan Kai."""
        brief = self.collab.prepare_preflight_brief(
            agent_id="zaki",
            task_title="Implementasi endpoint transaksi",
        )
        assert "pingot" in brief.consulted_agents
        assert "kai" in brief.consulted_agents
        assert any("Pingot/Data" in g for g in brief.design_guidelines)
        assert any("Kai/Security" in g for g in brief.design_guidelines)

    def test_kresna_handover_review_by_lulu_detects_isolated_layout(self):
        """Lulu memberikan rekomendasi jika animasi Kresna belum terintegrasi ke dashboard."""
        artifact_content = """
        <html>
        <div id="film-container" style="width: 960px;">
          <canvas id="stage"></canvas>
        </div>
        </html>
        """
        verdict = self.collab.perform_handover_review(
            task_id="TASK-99",
            producer_agent="kresna",
            artifacts=["kresna_film.html"],
            artifact_content=artifact_content,
        )
        assert verdict.reviewer_agent == "lulu"
        assert len(verdict.recommendations) > 0
        assert any("font-family" in r or "modal responsif" in r for r in verdict.recommendations)

    def test_zaki_handover_review_by_pingot_detects_unhashed_passwords(self):
        """Pingot menolak (CHANGES_REQUESTED) jika Zaki menyimpan password mentah."""
        bad_code = "def save_user(username, password): db.execute('INSERT INTO users VALUES (?, ?)', username, password)"
        verdict = self.collab.perform_handover_review(
            task_id="TASK-100",
            producer_agent="zaki",
            artifacts=["auth.py"],
            artifact_content=bad_code,
        )
        assert verdict.reviewer_agent == "pingot"
        assert verdict.status == "CHANGES_REQUESTED"
        assert "raw credential" in verdict.critique

    def test_team_deliberation_reaches_consensus(self):
        """Musyawarah tim mencapai konsensus jika quorum >= 75%."""
        critiques = [
            ("lulu", "APPROVE", "Desain UI linear & fluid."),
            ("zaki", "APPROVE", "API backend ringan."),
            ("pingot", "APPROVE", "Skema konsisten."),
            ("kai", "APPROVE", "Tidak ada celah OWASP."),
        ]
        res = self.collab.conduct_team_deliberation(
            proposal_title="Adopsi Canvas 2D Bird Eye View",
            proposer="lulu",
            description="Mengganti 3D monolitik menjadi 2D Canvas terisolasi.",
            architecture="Pure Canvas 2D + React state.",
            critiques_data=critiques,
        )
        assert res.status == "CONSENSUS_REACHED"
        assert res.approval_percentage == 100.0
        assert "Architecture Decision Record" in res.adr_markdown
