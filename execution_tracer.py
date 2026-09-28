"""
Multi-Agent Execution Flow Tracer & DAG Visualizer Engine — Dalang-AI
Terinspirasi dari https://github.com/algorithm-visualizer/algorithm-visualizer

Mencatat, menganalisis, dan memproyeksikan alur eksekusi multi-agent (DAG task graph)
menjadi frame visual langkah-demi-langkah (step-by-step playback).
"""

import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class TraceNode:
    id: str
    title: str
    agent: str
    status: str = "pending"  # pending, running, completed, failed
    dependencies: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class TraceEdge:
    from_node: str
    to_node: str
    status: str = "idle"  # idle, pulsing, completed


@dataclass
class TraceFrame:
    frame_index: int
    timestamp: float
    active_node_id: Optional[str]
    active_agent: Optional[str]
    action: str  # QUEUE, START, CODE_WRITE, TEST_RUN, VERIFY, COMPLETE, FAIL
    description: str
    nodes_state: Dict[str, Dict[str, Any]]
    edges_state: List[Dict[str, str]]


class ExecutionTracer:
    """
    Tracer Engine yang merekam siklus tugas multi-agent menjadi serangkaian frame
    yang dapat di-playback maju/mundur di UI layaknya Algorithm Visualizer.
    """

    def __init__(self, project_name: str = "Dalang-AI Project"):
        self.project_name = project_name
        self.nodes: Dict[str, TraceNode] = {}
        self.edges: List[TraceEdge] = []
        self.frames: List[TraceFrame] = []
        self.current_frame_idx: int = 0
        self._start_time: float = time.time()

    def add_task_node(
        self,
        task_id: str,
        title: str,
        agent: str,
        dependencies: Optional[List[str]] = None,
        artifacts: Optional[List[str]] = None,
    ) -> TraceNode:
        """Menambahkan node task ke dalam graph DAG."""
        deps = dependencies or []
        node = TraceNode(
            id=task_id,
            title=title,
            agent=agent,
            dependencies=deps,
            artifacts=artifacts or [],
        )
        self.nodes[task_id] = node

        # Hubungkan edge dari dependency ke node ini
        for dep_id in deps:
            self.edges.append(TraceEdge(from_node=dep_id, to_node=task_id))

        return node

    def record_step(
        self,
        active_node_id: Optional[str],
        action: str,
        description: str,
        node_status_override: Optional[str] = None,
        error: Optional[str] = None,
    ) -> TraceFrame:
        """
        Merekam satu frame visual trace perubahan state pada DAG.
        """
        active_agent = None
        if active_node_id and active_node_id in self.nodes:
            node = self.nodes[active_node_id]
            active_agent = node.agent
            if node_status_override:
                node.status = node_status_override
            if error:
                node.error = error

        # Evaluasi status edge
        updated_edges = []
        for edge in self.edges:
            from_st = self.nodes.get(edge.from_node, TraceNode("", "", "")).status
            to_st = self.nodes.get(edge.to_node, TraceNode("", "", "")).status

            if to_st == "running" and edge.to_node == active_node_id:
                edge_status = "pulsing"
            elif from_st == "completed" and to_st in ["completed", "running"]:
                edge_status = "completed"
            else:
                edge_status = "idle"

            updated_edges.append({
                "from": edge.from_node,
                "to": edge.to_node,
                "status": edge_status,
            })

        # Ambil snapshot state semua node
        nodes_snapshot = {
            nid: {
                "id": n.id,
                "title": n.title,
                "agent": n.agent,
                "status": n.status,
                "dependencies": n.dependencies,
                "artifacts": n.artifacts,
                "error": n.error,
            }
            for nid, n in self.nodes.items()
        }

        frame = TraceFrame(
            frame_index=len(self.frames),
            timestamp=round(time.time() - self._start_time, 3),
            active_node_id=active_node_id,
            active_agent=active_agent,
            action=action,
            description=description,
            nodes_state=nodes_snapshot,
            edges_state=updated_edges,
        )
        self.frames.append(frame)
        return frame

    def export_trace_payload(self) -> Dict[str, Any]:
        """
        Mengonversi seluruh trace ke JSON format yang siap dikonsumsi komponen React frontend.
        """
        return {
            "project": self.project_name,
            "total_frames": len(self.frames),
            "nodes": [asdict(n) for n in self.nodes.values()],
            "edges": [{"from": e.from_node, "to": e.to_node, "status": e.status} for e in self.edges],
            "frames": [
                {
                    "frame_index": f.frame_index,
                    "timestamp": f.timestamp,
                    "active_node_id": f.active_node_id,
                    "active_agent": f.active_agent,
                    "action": f.action,
                    "description": f.description,
                    "nodes_state": f.nodes_state,
                    "edges_state": f.edges_state,
                }
                for f in self.frames
            ],
        }


def build_default_sprint_trace() -> ExecutionTracer:
    """
    Membangun run trace bawaan berbasis sprint auth & security nyata Dalang-AI
    sebagai demonstrasi awal siap tonton di visualizer.
    """
    tracer = ExecutionTracer("Dalang-AI Auth & Reverse-Skill Sprint")

    # Definisi Task Nodes
    tracer.add_task_node("TASK-01", "Desain Arsitektur & Task Breakdown", "risko", dependencies=[])
    tracer.add_task_node("TASK-02", "Domain Model & Data Contracts", "pingot", dependencies=["TASK-01"], artifacts=["domain/user.py"])
    tracer.add_task_node("TASK-03", "Backend JWT Service & Constant-Time Hash", "zaki", dependencies=["TASK-02"], artifacts=["token_service.py"])
    tracer.add_task_node("TASK-04", "Frontend Auth UI & Three.js Integration", "lulu", dependencies=["TASK-03"], artifacts=["frontend_auth/app.js"])
    tracer.add_task_node("TASK-05", "Audit Reverse-Skill & Tamper Resistance", "kai", dependencies=["TASK-03"], artifacts=["SECURITY_AUDIT.md"])
    tracer.add_task_node("TASK-06", "Test Otomasi Boundary Value & Regresi", "ren", dependencies=["TASK-04", "TASK-05"], artifacts=["test_e2e_flow.py"])
    tracer.add_task_node("TASK-07", "Docker Container & SRE Toolchain Setup", "nova", dependencies=["TASK-06"], artifacts=["Dockerfile"])
    tracer.add_task_node("TASK-08", "Dokumentasi Arsitektur Diátaxis & Release", "mika", dependencies=["TASK-07"], artifacts=["docs/ARCHITECTURE.md"])

    # Langkah 0: Inisialisasi
    tracer.record_step(None, "INIT", "Risko memuat roadmap dan inisialisasi DAG dependency graph.")

    # Langkah 1: Risko
    tracer.record_step("TASK-01", "START", "Risko mulai menganalisis spesifikasi sprint dan membagi dependensi.", "running")
    tracer.record_step("TASK-01", "COMPLETE", "Risko menyelesaikan rancangan subtask. Kontrak diserahkan ke Pingot.", "completed")

    # Langkah 2: Pingot
    tracer.record_step("TASK-02", "START", "Pingot mendesain Value Objects dan Entitas User dengan prinsip DDD.", "running")
    tracer.record_step("TASK-02", "COMPLETE", "Pingot menyelesaikan domain/user.py tanpa plaintext credentials.", "completed")

    # Langkah 3: Zaki
    tracer.record_step("TASK-03", "START", "Zaki mengimplementasikan token_service.py dengan verifikasi constant-time.", "running")
    tracer.record_step("TASK-03", "COMPLETE", "Zaki memvalidasi signature HMAC-SHA256 lolos uji kriptografi.", "completed")

    # Langkah 4 & 5 (Paralel): Lulu & Kai
    tracer.record_step("TASK-04", "START", "Lulu mulai merancang UI auth anti-slop dengan WebGL backdrop.", "running")
    tracer.record_step("TASK-05", "START", "Kai mengaudit resistansi token terhadap JWT algorithm confusion.", "running")
    tracer.record_step("TASK-04", "COMPLETE", "Lulu menyelesaikan frontend auth yang responsif dan aman.", "completed")
    tracer.record_step("TASK-05", "COMPLETE", "Kai memverifikasi zero-vulnerability dan menutup celah tampered signature.", "completed")

    # Langkah 6: Ren
    tracer.record_step("TASK-06", "START", "Ren mengeksekusi 302 automated regression tests di workspace.", "running")
    tracer.record_step("TASK-06", "COMPLETE", "Ren mengonfirmasi 302/302 tests pass (100% clean).", "completed")

    # Langkah 7: Nova
    tracer.record_step("TASK-07", "START", "Nova membangun container Docker hermetic multi-stage build.", "running")
    tracer.record_step("TASK-07", "COMPLETE", "Container health check hijau. Port 8765 dan 5173 siap operasional.", "completed")

    # Langkah 8: Mika
    tracer.record_step("TASK-08", "START", "Mika menuliskan dokumentasi teknis lengkap berstandar Diátaxis.", "running")
    tracer.record_step("TASK-08", "COMPLETE", "Dokumentasi QUICKSTART dan ARCHITECTURE selesai. Sprint dinyatakan sukses!", "completed")

    return tracer
