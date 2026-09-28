"""
Test Suite untuk Sistem Cantrik (Ephemeral Worker Pool) Dalang-AI
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from cantrik_worker_pool import CantrikPool, CantrikTask, CantrikResult
from agent_tools import AgentToolbox
from scope_guard import ScopeViolationError


@pytest.mark.asyncio
async def test_cantrik_pool_parallel_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        pool = CantrikPool(workspace=tmpdir, max_concurrency=3)

        tasks = [
            {"title": "Subtask 1", "data": 10},
            {"title": "Subtask 2", "data": 20},
            {"title": "Subtask 3", "data": 30},
        ]

        async def worker(payload):
            await asyncio.sleep(0.01)
            return payload["data"] * 2

        result = await pool.execute_batch("zaki", tasks, worker)

        assert isinstance(result, CantrikResult)
        assert result.parent_agent == "zaki"
        assert result.total_tasks == 3
        assert result.successful_tasks == 3
        assert result.failed_tasks == 0
        assert len(result.task_results) == 3
        assert result.task_results[0]["result"] == 20
        assert result.task_results[1]["result"] == 40
        assert result.task_results[2]["result"] == 60


@pytest.mark.asyncio
async def test_cantrik_pool_scope_guard_enforcement():
    with tempfile.TemporaryDirectory() as tmpdir:
        pool = CantrikPool(workspace=tmpdir, max_concurrency=2)

        tasks = [
            {"title": "Illegal Escape", "path": "../../etc/shadow"},
        ]

        def worker(payload):
            return "should not be reached"

        result = await pool.execute_batch("kai", tasks, worker)

        assert result.total_tasks == 1
        assert result.successful_tasks == 0
        assert result.failed_tasks == 1
        assert "AKSES DITOLAK" in result.task_results[0]["error"]


def test_agent_toolbox_spawn_cantrik():
    with tempfile.TemporaryDirectory() as tmpdir:
        tb = AgentToolbox(tmpdir)
        # Create a sample file
        tb.write_file("test.txt", "Hello from Dalang")

        subtasks = [
            {"title": "Check echo 1", "cmd": "echo 'cantrik-1'"},
            {"title": "Check echo 2", "cmd": "echo 'cantrik-2'"},
        ]

        res = tb.spawn_cantrik("ren", subtasks)
        assert "OK: Cantrik Pool finished" in res
        assert "Success: 2/2" in res
