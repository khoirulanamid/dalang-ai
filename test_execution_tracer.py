"""
Test Suite untuk Multi-Agent Execution Flow Tracer & DAG Visualizer Engine
"""

import pytest
from execution_tracer import ExecutionTracer, build_default_sprint_trace


class TestExecutionTracer:
    def test_add_nodes_and_edges(self):
        tracer = ExecutionTracer("Test DAG")
        tracer.add_task_node("T1", "Task 1", "risko")
        tracer.add_task_node("T2", "Task 2", "pingot", dependencies=["T1"])

        assert len(tracer.nodes) == 2
        assert len(tracer.edges) == 1
        assert tracer.edges[0].from_node == "T1"
        assert tracer.edges[0].to_node == "T2"

    def test_record_step_and_export_payload(self):
        tracer = ExecutionTracer("Test Trace")
        tracer.add_task_node("T1", "Task 1", "risko")
        
        f0 = tracer.record_step(None, "INIT", "Inisialisasi sistem")
        assert f0.frame_index == 0
        assert f0.action == "INIT"

        f1 = tracer.record_step("T1", "START", "Mulai task", node_status_override="running")
        assert f1.frame_index == 1
        assert f1.active_agent == "risko"
        assert f1.nodes_state["T1"]["status"] == "running"

        payload = tracer.export_trace_payload()
        assert payload["total_frames"] == 2
        assert len(payload["nodes"]) == 1
        assert len(payload["frames"]) == 2

    def test_default_sprint_trace_pipeline(self):
        tracer = build_default_sprint_trace()
        payload = tracer.export_trace_payload()

        assert payload["total_frames"] >= 10
        assert len(payload["nodes"]) == 8
        # Ensure final state has all tasks completed
        last_frame = payload["frames"][-1]
        for nid, node_info in last_frame["nodes_state"].items():
            assert node_info["status"] == "completed"
