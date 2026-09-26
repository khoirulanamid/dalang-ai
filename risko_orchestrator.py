import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Coroutine, Dict, List, Optional

import yaml
from roadmap_parser import get_next_tasks, parse_roadmap
from real_subagent_runner import RealSubAgentRunner
from wayang_router import auto_route_task, partition_active_and_idle_wayang, WAYANG_ROSTER

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Risko] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Risko")


@dataclass
class AgentEvent:
    event_type: str  # task_ready, task_dispatched, task_completed, task_failed, roadmap_synced
    agent: str  # risko, pingot, zaki, lulu
    task_id: Optional[str]
    message: str
    timestamp: str
    metadata: dict


class RiskoOrchestrator:

    def __init__(self, roadmap_path: str, workspace: str = None, model: str = "auto"):
        self.roadmap_path = Path(roadmap_path)
        self.roadmap = None
        self.event_subscribers: List[Callable[[AgentEvent], Coroutine]] = []
        self.event_log: List[AgentEvent] = []
        self.is_running = False
        self.workspace = workspace or str(Path(roadmap_path).parent / "workspace")
        self.model = model
        self.runner = RealSubAgentRunner(workspace=self.workspace, model=self.model)

    def emit_event(self, event_type: str, agent: str, message: str, task_id: Optional[str] = None, metadata: dict = None):
        """Emit an event to the local log and broadcast to external sinks (WebSocket/SSE)."""
        ev = AgentEvent(
            event_type=event_type,
            agent=agent,
            task_id=task_id,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self.event_log.append(ev)
        logger.info(f"[{agent.upper()}] ({event_type}) {message} {f'| Task: {task_id}' if task_id else ''}")

        # Broadcast asynchronously
        for sub in self.event_subscribers:
            asyncio.create_task(sub(ev))
        return ev

    def subscribe_events(self, callback: Callable[[AgentEvent], Coroutine]):
        self.event_subscribers.append(callback)

    def reload_roadmap(self):
        """Single source of truth sync."""
        self.roadmap = parse_roadmap(str(self.roadmap_path))
        return self.roadmap

    def update_task_status(self, task_id: str, new_status: str, done: bool = False, artifacts: list = None):
        """Update task in ROADMAP.md file atomically."""
        with open(self.roadmap_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Update checkbox: - [ ] **T-101** -> - [x] **T-101**
        check_str = "- [x]" if done else "- [ ]"
        import re

        pattern = rf"- \[[ xX]\] \*\*{task_id}\*\*"
        if not re.search(pattern, content):
            return  # Task is an ad-hoc dispatch, not in ROADMAP.md

        repl = f"{check_str} **{task_id}**"
        content = re.sub(pattern, repl, content)

        # Update status line under the task
        task_block_pattern = rf"(\*\*{task_id}\*\*[\s\S]*?- \*Status\*:\s*)([^\n]+)"
        content = re.sub(task_block_pattern, rf"\g<1>{new_status}", content)

        with open(self.roadmap_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.reload_roadmap()
        self.emit_event(
            event_type="roadmap_synced",
            agent="risko",
            task_id=task_id,
            message=f"ROADMAP.md updated: {task_id} -> {new_status} (done={done})",
            metadata={"status": new_status, "done": done, "artifacts": artifacts or []},
        )

    def extract_agent_subgraph(self, agent_id: str, current_task: dict) -> dict:
        """Graphify context reduction: extracts ONLY relevant node context for the agent."""
        return {
            "agent": agent_id,
            "current_task": {
                "id": current_task["id"],
                "title": current_task["title"],
                "dependencies": current_task.get("dependencies", []),
                "artifacts": current_task.get("artifacts", []),
            },
            "completed_upstream": [
                {"id": t["id"], "artifacts": t.get("artifacts", [])}
                for t in self.roadmap["tasks"]
                if t["id"] in current_task.get("dependencies", []) and t["done"]
            ],
            # Notice: DOES NOT include the full conversation history or unrelated tasks!
        }

    async def real_subagent_worker(self, agent_id: str, task: dict):
        """Execute real LLM-backed sub-agent with tools and isolated context."""
        subgraph = self.extract_agent_subgraph(agent_id, task)

        self.emit_event(
            event_type="task_dispatched",
            agent=agent_id,
            task_id=task["id"],
            message=f"Agent {agent_id} assigned task: '{task['title']}'",
            metadata={"subgraph_size": len(json.dumps(subgraph))},
        )

        async def agent_event_sink(action: str, detail: str):
            # Stream tool calls and progress live to dashboard
            self.emit_event(
                event_type=f"agent_{action}",
                agent=agent_id,
                task_id=task["id"],
                message=detail,
                metadata={"action": action},
            )

        # Call the real runner (OpenAI function calling loop)
        result = await self.runner.execute_task(
            agent_id=agent_id,
            task=task,
            subgraph=subgraph,
            on_event=agent_event_sink,
            max_tool_iterations=20,
        )

        if result.get("success"):
            self.update_task_status(task["id"], new_status="completed", done=True, artifacts=task.get("artifacts"))
            self.emit_event(
                event_type="task_completed",
                agent=agent_id,
                task_id=task["id"],
                message=f"Agent {agent_id} completed {task['id']} ({result.get('tool_calls', 0)} tool calls)",
                metadata=result,
            )
        else:
            self.update_task_status(task["id"], new_status="failed", done=False)
            self.emit_event(
                event_type="task_failed",
                agent=agent_id,
                task_id=task["id"],
                message=f"Agent {agent_id} failed {task['id']}: {result.get('error')}",
                metadata=result,
            )

    async def mock_subagent_worker(self, agent_id: str, task: dict):
        """Simulates isolated sub-agent execution with its restricted sub-graph context."""
        subgraph = self.extract_agent_subgraph(agent_id, task)

        self.emit_event(
            event_type="task_dispatched",
            agent=agent_id,
            task_id=task["id"],
            message=f"Agent {agent_id} starting task: '{task['title']}'",
            metadata={"subgraph_token_estimate": len(json.dumps(subgraph)) // 4},
        )

        # Simulate execution work delay
        await asyncio.sleep(1.0)

        # Mark done
        self.update_task_status(task["id"], new_status="completed", done=True)
        self.emit_event(
            event_type="task_completed",
            agent=agent_id,
            task_id=task["id"],
            message=f"Agent {agent_id} successfully completed task {task['id']}",
            metadata={"artifacts": task.get("artifacts", [])},
        )

    async def run_orchestration_cycle(self, max_cycles: int = 5):
        """Main Orchestrator Loop."""
        self.is_running = True
        self.reload_roadmap()
        logger.info(f"Loaded ROADMAP.md for project: {self.roadmap['metadata']['project']}")

        cycle = 0
        while self.is_running and cycle < max_cycles:
            cycle += 1
            next_tasks = get_next_tasks(self.roadmap)

            if not next_tasks:
                pending = [t for t in self.roadmap["tasks"] if not t["done"]]
                if not pending:
                    self.emit_event(
                        event_type="orchestration_finished",
                        agent="risko",
                        message="All roadmap tasks have been completed successfully!",
                    )
                else:
                    self.emit_event(
                        event_type="orchestration_blocked",
                        agent="risko",
                        message=f"{len(pending)} tasks pending but dependencies are not met.",
                    )
                break

            self.emit_event(
                event_type="cycle_started",
                agent="risko",
                message=f"Cycle {cycle}: Found {len(next_tasks)} runnable tasks: {[t['id'] for t in next_tasks]}",
            )

            # Auto-route & dispatch to designated sub-agents
            agent_coroutines = []
            assigned_this_cycle = set()
            for task in next_tasks:
                explicit = task.get("assigned") or task.get("agent")
                if not explicit or explicit == "unassigned":
                    assigned_agent, score = auto_route_task(task["title"], explicit_agent=None)
                    logger.info(f"[Risko Routing] Task {task['id']} '{task['title']}' auto-assigned to [{assigned_agent}] (score={score:.1f})")
                else:
                    assigned_agent = explicit.lower()

                assigned_this_cycle.add(assigned_agent)
                # Update status to running
                self.update_task_status(task["id"], new_status="in_progress", done=False)
                agent_coroutines.append(self.real_subagent_worker(assigned_agent, task))

            # Report idle wayang (tidak dapat tugas di siklus ini)
            all_known = set(WAYANG_ROSTER.keys())
            idle_now = all_known - assigned_this_cycle
            if idle_now:
                idle_names = [WAYANG_ROSTER[a]["title"] for a in idle_now if a in WAYANG_ROSTER]
                self.emit_event(
                    event_type="wayang_idle",
                    agent="risko",
                    message=f"Wayang standby/diam: {', '.join(idle_names)}",
                    metadata={"idle_agents": list(idle_now)},
                )

            # Wait for all parallel tasks in this batch to finish
            await asyncio.gather(*agent_coroutines)

            # Reload roadmap to get updated states
            self.reload_roadmap()

        logger.info("Risko Orchestration cycle finished.")


# Quick test runner
if __name__ == "__main__":
    orchestrator = RiskoOrchestrator("/root/storage/projects/dalang-ai/ROADMAP.md")

    async def log_sink(event: AgentEvent):
        # This will be replaced by WebSocket / SSE publisher
        pass

    orchestrator.subscribe_events(log_sink)
    asyncio.run(orchestrator.run_orchestration_cycle(max_cycles=3))
