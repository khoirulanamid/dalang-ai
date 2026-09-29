"""
Test Suite untuk Telemetry & Token Observability Engine
"""

import pytest
from telemetry_engine import TelemetryEngine, AgentMetricRecord


class TestTelemetryEngine:
    def test_record_single_execution(self):
        engine = TelemetryEngine()
        rec = engine.record_execution(
            task_id="TASK-01",
            agent_id="zaki",
            prompt_tokens=450,
            completion_tokens=200,
            latency_ms=1250.5,
            tool_calls=2,
        )

        assert isinstance(rec, AgentMetricRecord)
        assert rec.total_tokens == 650
        assert rec.cost_estimate_usd > 0
        assert rec.agent_id == "zaki"
        assert len(engine.records) == 1

    def test_agent_summary_aggregation(self):
        engine = TelemetryEngine()
        engine.record_execution("T1", "kai", 500, 100, 800.0, tool_calls=1)
        engine.record_execution("T2", "kai", 700, 300, 1200.0, tool_calls=3)

        summary = engine.get_agent_summary("kai")
        assert summary["total_tasks"] == 2
        assert summary["total_tokens"] == 1600
        assert summary["avg_latency_ms"] == 1000.0
        assert summary["total_tool_calls"] == 4

    def test_fleet_telemetry_and_prometheus_export(self):
        engine = TelemetryEngine()
        engine.record_execution("T1", "risko", 300, 100, 500.0)
        engine.record_execution("T2", "lulu", 600, 400, 1500.0)

        fleet = engine.get_fleet_telemetry()
        assert fleet["total_tasks"] == 2
        assert fleet["total_tokens"] == 1400
        assert "risko" in fleet["agents_breakdown"]
        assert "lulu" in fleet["agents_breakdown"]

        prom = engine.export_prometheus_metrics()
        assert "dalang_agent_total_tokens" in prom
        assert 'agent="risko"' in prom
        assert 'agent="lulu"' in prom
