import yaml
import re


def parse_roadmap(filepath: str):
    """Parse ROADMAP.md into YAML frontmatter metadata and structured tasks."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("---\n")
    if len(parts) < 3:
        raise ValueError("Invalid ROADMAP.md: Missing frontmatter delimiters")

    frontmatter = yaml.safe_load(parts[1])
    body = "---\n".join(parts[2:])

    tasks = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Match task header: - [ ] **T-XXX**: [agent] title
        m = re.match(r"-\s+\[(?P<done>[\sxX])\]\s+\*\*(?P<id>T-\d+)\*\*:\s+\[(?P<agent>\w+)\]\s+(?P<title>.+)", line)
        if m:
            task = {
                "id": m.group("id"),
                "agent": m.group("agent"),
                "title": m.group("title").strip(),
                "done": m.group("done").strip().lower() == "x",
                "assigned": None,
                "dependencies": [],
                "status": "pending",
                "artifacts": [],
            }
            # Parse sub-fields
            j = i + 1
            while j < len(lines):
                sub = lines[j].strip()
                if sub.startswith("- *Assigned*:"):
                    task["assigned"] = sub.split(":", 1)[1].strip()
                elif sub.startswith("- *Dependencies*:"):
                    raw = sub.split(":", 1)[1].strip()
                    task["dependencies"] = [d.strip() for d in raw.split(",") if d.strip() and d.strip().lower() != "none"]
                elif sub.startswith("- *Status*:"):
                    task["status"] = sub.split(":", 1)[1].strip()
                elif sub.startswith("- *Artifacts*:"):
                    raw = sub.split(":", 1)[1].strip()
                    task["artifacts"] = [a.strip() for a in raw.replace("`", "").split(",")]
                elif sub.startswith("- [") or sub.startswith("##") or sub.startswith("---"):
                    break
                j += 1
            tasks.append(task)
            i = j
        else:
            i += 1

    return {"metadata": frontmatter, "tasks": tasks}


def get_agent_tasks(roadmap: dict, agent_id: str) -> list:
    """Extract only tasks assigned to a specific agent (Graphify-style sub-graph)."""
    return [t for t in roadmap["tasks"] if t.get("assigned") == agent_id]


def get_pending_tasks(roadmap: dict) -> list:
    return [t for t in roadmap["tasks"] if not t["done"]]


def get_next_tasks(roadmap: dict) -> list:
    """Tasks with no unmet dependencies (ready to run)."""
    completed_ids = {t["id"] for t in roadmap["tasks"] if t["done"]}
    result = []
    for t in roadmap["tasks"]:
        if t["done"]:
            continue
        if all(dep in completed_ids for dep in t["dependencies"]):
            result.append(t)
    return result


if __name__ == "__main__":
    roadmap = parse_roadmap("/root/storage/projects/dalang-ai/ROADMAP.md")
    meta = roadmap["metadata"]
    tasks = roadmap["tasks"]

    print(f"Project  : {meta['project']} v{meta['version']}")
    print(f"Orchestrator: {meta['orchestrator']}")
    print(f"Agents   : {[a['id'] for a in meta['agents']]}")
    print(f"Total Tasks: {len(tasks)}")
    print()

    print("=== ALL TASKS ===")
    for t in tasks:
        status = "✅" if t["done"] else "⬜"
        deps = ", ".join(t["dependencies"]) if t["dependencies"] else "none"
        print(f"  {status} [{t['id']}] ({t['assigned']}) {t['title']}")
        print(f"       status={t['status']}  deps={deps}")

    print()
    print("=== NEXT RUNNABLE TASKS ===")
    for t in get_next_tasks(roadmap):
        print(f"  ▶ [{t['id']}] ({t['assigned']}) {t['title']}")

    print()
    print("=== PER-AGENT SUB-GRAPH ===")
    for agent in [a["id"] for a in meta["agents"]]:
        agent_tasks = get_agent_tasks(roadmap, agent)
        print(f"  [{agent}] -> {[t['id'] for t in agent_tasks]}")
