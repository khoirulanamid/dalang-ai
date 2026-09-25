import asyncio, sys
sys.path.insert(0, '/root/storage/projects/dalang-ai')
from risko_orchestrator import RiskoOrchestrator

orch = RiskoOrchestrator(
    roadmap_path='/root/storage/projects/dalang-ai/ROADMAP.md',
    workspace='/root/storage/projects/dalang-ai/workspace'
)

asyncio.run(orch.run_orchestration_cycle(max_cycles=5))
