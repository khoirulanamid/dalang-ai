"""
Dalang-AI — Risko Backend
FastAPI + WebSocket event bus + SSE endpoint
Orchestrator runs as a background async task, events broadcast to all connected clients.
"""

import asyncio
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator, Optional
from pydantic import BaseModel

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

# Add project root to path so we can import from parent dir
sys.path.insert(0, str(Path(__file__).parent.parent))

from risko_orchestrator import AgentEvent, RiskoOrchestrator
from wayang_router import auto_route_task

ROADMAP_PATH = Path(__file__).parent.parent / "ROADMAP.md"

app = FastAPI(title="Dalang-AI Risko Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Connection Manager ---

class ConnectionManager:
    def __init__(self):
        self.ws_clients: list[WebSocket] = []
        self.sse_queues: list[asyncio.Queue] = []

    async def connect_ws(self, ws: WebSocket):
        await ws.accept()
        self.ws_clients.append(ws)

    def disconnect_ws(self, ws: WebSocket):
        if ws in self.ws_clients:
            self.ws_clients.remove(ws)

    def add_sse_queue(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.sse_queues.append(q)
        return q

    def remove_sse_queue(self, q: asyncio.Queue):
        if q in self.sse_queues:
            self.sse_queues.remove(q)

    async def broadcast(self, event: AgentEvent):
        payload = json.dumps(asdict(event))

        # Broadcast to WebSocket clients
        dead = []
        for ws in self.ws_clients:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_ws(ws)

        # Push to SSE queues
        for q in self.sse_queues:
            await q.put(payload)


manager = ConnectionManager()

# --- Orchestrator singleton ---
orchestrator = RiskoOrchestrator(str(ROADMAP_PATH))
orchestrator_task: asyncio.Task | None = None


async def event_sink(event: AgentEvent):
    """Subscribed to orchestrator — relays all events to connected clients."""
    await manager.broadcast(event)


orchestrator.subscribe_events(event_sink)


# --- Lifecycle ---

@app.on_event("startup")
async def startup():
    # Reload roadmap on start
    orchestrator.reload_roadmap()


# --- Routes ---

@app.get("/")
async def root():
    return {"service": "Dalang-AI Risko Backend", "status": "online"}


@app.get("/roadmap")
async def get_roadmap():
    """Return the current ROADMAP state as JSON."""
    roadmap = orchestrator.reload_roadmap()
    return JSONResponse(content=roadmap)


@app.get("/events/log")
async def get_event_log():
    """Return all emitted events since server start."""
    return [asdict(e) for e in orchestrator.event_log]


@app.get("/agents/status")
async def agents_status():
    """Per-agent task breakdown from current ROADMAP."""
    from roadmap_parser import get_agent_tasks, get_next_tasks
    roadmap = orchestrator.reload_roadmap()
    agents = roadmap["metadata"].get("agents", [])
    result = []
    for a in agents:
        aid = a["id"]
        tasks = get_agent_tasks(roadmap, aid)
        result.append({
            "agent": aid,
            "role": a.get("role"),
            "total_tasks": len(tasks),
            "completed": sum(1 for t in tasks if t["done"]),
            "pending": sum(1 for t in tasks if not t["done"]),
            "tasks": [{"id": t["id"], "title": t["title"], "status": t["status"], "done": t["done"]} for t in tasks],
        })
    return result


@app.post("/orchestrate/start")
async def start_orchestration(max_cycles: int = 10):
    """Kick off Risko orchestration loop in background."""
    global orchestrator_task

    if orchestrator_task and not orchestrator_task.done():
        return JSONResponse(status_code=409, content={"error": "Orchestration already running"})

    # Reset ROADMAP for clean demo run
    async def run():
        await orchestrator.run_orchestration_cycle(max_cycles=max_cycles)

    orchestrator_task = asyncio.create_task(run())
    return {"status": "started", "max_cycles": max_cycles}


@app.post("/orchestrate/stop")
async def stop_orchestration():
    global orchestrator_task
    if orchestrator_task and not orchestrator_task.done():
        orchestrator_task.cancel()
        orchestrator.is_running = False
        return {"status": "stopped"}
    return {"status": "not_running"}


@app.get("/orchestrate/status")
async def orchestration_status():
    global orchestrator_task
    if orchestrator_task is None:
        return {"running": False, "status": "never_started"}
    if orchestrator_task.done():
        exc = orchestrator_task.exception() if not orchestrator_task.cancelled() else None
        return {"running": False, "status": "finished", "error": str(exc) if exc else None}
    return {"running": True, "status": "in_progress"}


class TaskDispatchRequest(BaseModel):
    title: str
    description: str = ""
    agent: Optional[str] = None
    duration_seconds: Optional[int] = 12


@app.post("/tasks/dispatch")
async def dispatch_task(req: TaskDispatchRequest):
    """
    Kirim tugas spesifik atau umum ke tim Wayang.
    Jika agen tidak diisi atau 'auto', Sang Dalang (Risko) otomatis memilih Wayang yang paling kompeten.
    """
    target = req.agent if req.agent and req.agent != "auto" else None
    routed_agent, confidence = auto_route_task(req.title, req.description, target)
    task_id = f"TASK-{int(datetime.now().timestamp()) % 10000:04d}"

    # 1. Risko delegasikan tugas
    orchestrator.emit_event(
        event_type="task_ready",
        agent="risko",
        task_id=task_id,
        message=f"Risko menugaskan {routed_agent.capitalize()}: {req.title}",
        metadata={"target_agent": routed_agent, "title": req.title},
    )

    # 2. Wayang yang ditunjuk mulai bekerja (NGETIK)
    orchestrator.emit_event(
        event_type="task_dispatched",
        agent=routed_agent,
        task_id=task_id,
        message=f"{req.title}" + (f" ({req.description})" if req.description else ""),
        metadata={"duration": req.duration_seconds or 12},
    )

    # 3. Selesaikan tugas setelah durasi tertentu
    async def finish_task():
        await asyncio.sleep(req.duration_seconds or 12)
        orchestrator.emit_event(
            event_type="task_completed",
            agent=routed_agent,
            task_id=task_id,
            message=f"Selesai: {req.title}",
            metadata={"status": "success"},
        )

    asyncio.create_task(finish_task())

    return {
        "status": "dispatched",
        "task_id": task_id,
        "assigned_agent": routed_agent,
        "confidence": confidence,
        "message": f"Tugas '{req.title}' diserahkan ke {routed_agent.capitalize()}",
    }


# --- WebSocket endpoint ---

@app.websocket("/ws/events")
async def websocket_events(ws: WebSocket):
    """
    WebSocket event stream. Clients connect here and receive all
    orchestrator events in real time as JSON payloads.
    """
    await manager.connect_ws(ws)
    # Send current event log on connect so new clients are caught up
    for ev in orchestrator.event_log:
        try:
            await ws.send_text(json.dumps(asdict(ev)))
        except Exception:
            break
    try:
        while True:
            # Keep alive — wait for client ping or disconnect
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_ws(ws)


# --- SSE endpoint ---

@app.get("/sse/events")
async def sse_events():
    """
    Server-Sent Events stream. Alternative to WebSocket for browser EventSource.
    """
    q = manager.add_sse_queue()

    async def generator() -> AsyncGenerator[str, None]:
        # Replay existing log
        for ev in orchestrator.event_log:
            yield f"data: {json.dumps(asdict(ev))}\n\n"

        try:
            while True:
                try:
                    payload = await asyncio.wait_for(q.get(), timeout=30)
                    yield f"data: {payload}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat to keep connection alive
                    yield f": heartbeat {datetime.now(timezone.utc).isoformat()}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            manager.remove_sse_queue(q)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
