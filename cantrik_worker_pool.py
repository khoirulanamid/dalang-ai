"""
Cantrik Worker Pool — Sistem Asisten Sub-Agent (Ephemeral Worker) untuk Dalang-AI
Arsitektur terdistribusi ringan: Setiap Wayang dapat men-spawn Cantrik (murid/asisten sementara)
untuk mengeksekusi tugas batch, audit paralel, pengujian regresi, dan scaffolding tanpa membebani memori.

Filosofi Wayang: Tokoh sakti (Wayang Inti) didukung oleh Cantrik (asisten lapangan)
yang patuh pada Scope Guard dan mencatat pembelajaran ke Field Journal.
"""

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

from scope_guard import validate_path_in_scope, ScopeViolationError
from field_journal import record_journal_entry


@dataclass
class CantrikTask:
    id: str
    title: str
    payload: Dict[str, Any]
    assigned_worker: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class CantrikResult:
    parent_agent: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    duration_ms: float
    task_results: List[Dict[str, Any]] = field(default_factory=list)


class CantrikPool:
    """
    Pool pekerja ephemeral (asisten sementara) yang dapat di-spawn on-demand oleh Wayang.
    Mendukung eksekusi asinkronus paralel dengan isolasi dan batasan concurrency.
    """

    def __init__(self, workspace: str, max_concurrency: int = 4):
        self.workspace = Path(workspace).resolve()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def _execute_single_task(
        self,
        parent_agent: str,
        task: CantrikTask,
        worker_func: Callable[[Dict[str, Any]], Any],
    ) -> CantrikTask:
        async with self.semaphore:
            task.status = "running"
            start_t = time.perf_counter()
            try:
                # Validasi jika task melibatkan path file di payload
                if "path" in task.payload:
                    validate_path_in_scope(task.payload["path"], self.workspace)

                # Jalankan fungsi worker
                if asyncio.iscoroutinefunction(worker_func):
                    res = await worker_func(task.payload)
                else:
                    res = worker_func(task.payload)

                task.status = "completed"
                task.result = res
            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                # Catat insiden ke Field Journal
                try:
                    record_journal_entry(
                        title=f"Cantrik Failure: {task.title}",
                        category=f"{parent_agent}-cantrik-error",
                        agent_id=parent_agent,
                        summary=f"Kegagalan eksekusi Cantrik saat menjalankan task {task.id}",
                        pitfalls=[str(e)],
                        solution="Evaluasi parameter payload dan pastikan batasan scope/path terpenuhi.",
                        tags=["cantrik", "error", parent_agent],
                    )
                except Exception:
                    pass
            finally:
                task.execution_time_ms = (time.perf_counter() - start_t) * 1000.0

            return task

    async def execute_batch(
        self,
        parent_agent: str,
        tasks: List[Dict[str, Any]],
        worker_func: Callable[[Dict[str, Any]], Any],
    ) -> CantrikResult:
        """
        Mengeksekusi sekumpulan task secara paralel dengan bantuan kawanan Cantrik.
        """
        start_batch = time.perf_counter()
        cantrik_tasks = [
            CantrikTask(
                id=f"CTK-{parent_agent.upper()}-{i+1:03d}",
                title=t.get("title", f"Subtask {i+1}"),
                payload=t,
                assigned_worker=f"cantrik-{parent_agent}-{i+1}",
            )
            for i, t in enumerate(tasks)
        ]

        # Jalankan secara konkuren
        coros = [
            self._execute_single_task(parent_agent, c_task, worker_func)
            for c_task in cantrik_tasks
        ]
        completed_tasks = await asyncio.gather(*coros)

        success_count = sum(1 for t in completed_tasks if t.status == "completed")
        failed_count = sum(1 for t in completed_tasks if t.status == "failed")
        duration_total = (time.perf_counter() - start_batch) * 1000.0

        return CantrikResult(
            parent_agent=parent_agent,
            total_tasks=len(tasks),
            successful_tasks=success_count,
            failed_tasks=failed_count,
            duration_ms=duration_total,
            task_results=[
                {
                    "task_id": t.id,
                    "worker": t.assigned_worker,
                    "title": t.title,
                    "status": t.status,
                    "result": t.result,
                    "error": t.error,
                    "duration_ms": round(t.execution_time_ms, 2),
                }
                for t in completed_tasks
            ],
        )
