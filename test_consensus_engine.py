"""
Test Suite untuk Multi-Agent Consensus & Debate Protocol (Musyawarah Para Wayang)
"""

import pytest
from consensus_engine import (
    WayangConsensusEngine,
    Proposal,
    AgentCritique,
    ConsensusResult,
)


class TestWayangConsensusEngine:
    def test_unanimous_consensus_reached(self):
        engine = WayangConsensusEngine(required_quorum=0.75)
        prop = Proposal(
            id="PROP-01",
            title="Migrasi ke PostgreSQL Connection Pooling dengan PGBouncer",
            proposer_agent="pingot",
            description="Trafik API meningkat, koneksi langsung ke DB mulai boros connection slot.",
            proposed_architecture="Pasang PGBouncer di depan PostgreSQL port 5432.",
            tradeoffs=["Menambah 1 layer proxy", "Meningkatkan throughput 3x lipat"],
        )

        reviews = [
            AgentCritique("risko", "APPROVE", "Sangat tepat untuk kapasitas concurrency."),
            AgentCritique("zaki", "APPROVE", "Driver asyncpg kami kompatibel penuh."),
            AgentCritique("nova", "APPROVE", "Container image pgbouncer sudah siap di Docker registry."),
            AgentCritique("kai", "APPROVE", "Pastikan TLS listening mode diaktifkan di proxy."),
        ]

        result = engine.conduct_deliberation(prop, reviews)
        assert result.status == "CONSENSUS_REACHED"
        assert result.approval_percentage == 100.0
        assert "ADR" in result.adr_markdown
        assert "DITERIMA" in result.adr_markdown

    def test_security_veto_by_kai(self):
        """Hak veto keamanan: Kai menolak proposal karena ada celah kritis, status langsung VETOED."""
        engine = WayangConsensusEngine(required_quorum=0.75)
        prop = Proposal(
            id="PROP-02",
            title="Bypass Signature Check pada Endpoint Internal Webhook",
            proposer_agent="zaki",
            description="Mempercepat latensi inter-service communication.",
            proposed_architecture="Menonaktifkan HMAC verification khusus IP lokal.",
            tradeoffs=["Resiko IP spoofing jika reverse proxy salah konfigurasi"],
        )

        reviews = [
            AgentCritique("risko", "APPROVE", "Bisa menghemat waktu 15ms."),
            AgentCritique("pingot", "APPROVE", "Data tetap valid."),
            AgentCritique("kai", "OBJECT", "BAHAYA: IP spoofing memungkinkan SSRF injection tanpa auth."),
            AgentCritique("ren", "NEUTRAL", "Sulit diuji konsistensinya di CI."),
        ]

        result = engine.conduct_deliberation(prop, reviews)
        assert result.status == "VETOED"
        assert result.approval_percentage == 0.0
        assert "PROPOSAL DI-VETO OLEH KAI" in result.synthesis
        assert "DITOLAK (VETOED)" in result.adr_markdown

    def test_insufficient_quorum_requires_amendment(self):
        engine = WayangConsensusEngine(required_quorum=0.75)
        prop = Proposal(
            id="PROP-03",
            title="Penggunaan Redux Global State untuk Semua Form Input",
            proposer_agent="lulu",
            description="Sentralisasi state input frontend ke Redux store.",
            proposed_architecture="Setiap keystroke diproses Redux action.",
        )

        reviews = [
            AgentCritique("risko", "APPROVE", "Mudah di-debug."),
            AgentCritique("zaki", "OBJECT", "Redundant re-render di DOM akan menyebabkan input lag."),
            AgentCritique("ren", "NEUTRAL", "Menambah overhead unit test."),
            AgentCritique("kai", "APPROVE", "Tidak ada masalah keamanan."),
        ]

        # Approval rate 50% (2/4) < 75%
        result = engine.conduct_deliberation(prop, reviews)
        assert result.status == "AMENDMENT_REQUIRED"
        assert result.approval_percentage == 50.0
        assert "Konsensus belum tercapai" in result.synthesis
