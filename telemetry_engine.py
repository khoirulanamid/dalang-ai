"""
Telemetry & Token Observability Engine — Dalang-AI
Terinspirasi dari OpenTelemetry (OTel) & LLM Token Hygiene

Memantau dan mencatat:
1. Konsumsi token (Prompt & Completion Tokens) per Wayang
2. Latensi eksekusi tugas (latency dalam milidetik)
3. Frekuensi pemanggilan tools (Tool Call Counts)
4. Estimasi biaya eksekusi per sprint
5. Format metrik OpenTelemetry / Prometheus compatible
"""

import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class AgentMetricRecord:
    task_id: str
    agent_id: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    tool_calls: int = 0
    cost_estimate_usd: float = 0.0
    timestamp: float = field(default_factory=time.time)


class TelemetryEngine:
    """
    Kolektor telemetri dan observabilitas LLM sub-agent.
    """

    # Tarif acuan estimasi per 1k token ($0.0015 input, $0.002 output)
    COST_PER_1K_PROMPT = 0.0015
    COST_PER_1K_COMPLETION = 0.0020

    def __init__(self):
        self.records: List[AgentMetricRecord] = []

    def record_execution(
        self,
        task_id: str,
        agent_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        tool_calls: int = 0,
    ) -> AgentMetricRecord:
        """Mencatat metrik satu kali eksekusi tugas Wayang."""
        tot = prompt_tokens + completion_tokens
        cost = (
            (prompt_tokens / 1000.0) * self.COST_PER_1K_PROMPT
            + (completion_tokens / 1000.0) * self.COST_PER_1K_COMPLETION
        )

        rec = AgentMetricRecord(
            task_id=task_id,
            agent_id=agent_id.lower(),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=tot,
            latency_ms=round(latency_ms, 2),
            tool_calls=tool_calls,
            cost_estimate_usd=round(cost, 6),
        )
        self.records.append(rec)
        return rec

    def get_agent_summary(self, agent_id: str) -> Dict[str, Any]:
        """Ringkasan performa dan konsumsi token untuk satu Wayang spesifik."""
        agent_records = [r for r in self.records if r.agent_id == agent_id.lower()]
        if not agent_records:
            return {
                "agent_id": agent_id,
                "total_tasks": 0,
                "total_tokens": 0,
                "avg_latency_ms": 0.0,
                "total_cost_usd": 0.0,
            }

        tot_tok = sum(r.total_tokens for r in agent_records)
        avg_lat = sum(r.latency_ms for r in agent_records) / len(agent_records)
        tot_cost = sum(r.cost_estimate_usd for r in agent_records)

        return {
            "agent_id": agent_id,
            "total_tasks": len(agent_records),
            "total_tokens": tot_tok,
            "avg_latency_ms": round(avg_lat, 2),
            "total_cost_usd": round(tot_cost, 6),
            "total_tool_calls": sum(r.tool_calls for r in agent_records),
        }

    def get_fleet_telemetry(self) -> Dict[str, Any]:
        """Ringkasan keseluruhan 8 Wayang dan efisiensi sprint."""
        if not self.records:
            return {
                "total_tasks": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0.0,
                "agents_breakdown": {},
            }

        total_tok = sum(r.total_tokens for r in self.records)
        total_cost = sum(r.cost_estimate_usd for r in self.records)
        avg_latency = sum(r.latency_ms for r in self.records) / len(self.records)

        distinct_agents = sorted(list(set(r.agent_id for r in self.records)))
        breakdown = {aid: self.get_agent_summary(aid) for aid in distinct_agents}

        return {
            "total_tasks": len(self.records),
            "total_tokens": total_tok,
            "total_cost_usd": round(total_cost, 6),
            "avg_latency_ms": round(avg_latency, 2),
            "agents_breakdown": breakdown,
        }

    def export_prometheus_metrics(self) -> str:
        """Menghasilkan representasi metrik OpenTelemetry / Prometheus exposition format."""
        lines = [
            "# HELP dalang_agent_total_tokens Total tokens consumed by agent",
            "# TYPE dalang_agent_total_tokens counter",
        ]
        fleet = self.get_fleet_telemetry()
        for aid, s in fleet.get("agents_breakdown", {}).items():
            lines.append(f'dalang_agent_total_tokens{{agent="{aid}"}} {s["total_tokens"]}')

        lines.extend([
            "# HELP dalang_agent_latency_ms Average task latency in milliseconds",
            "# TYPE dalang_agent_latency_ms gauge",
        ])
        for aid, s in fleet.get("agents_breakdown", {}).items():
            lines.append(f'dalang_agent_latency_ms{{agent="{aid}"}} {s["avg_latency_ms"]}')

        return "\n".join(lines)
