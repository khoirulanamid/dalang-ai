import yaml
import re


def parse_roadmap(filepath: str):
    """
    Parse ROADMAP.md menjadi metadata dan daftar tasks terstruktur.

    Format task yang didukung:
      Format baru (Risko auto-assign):
        - [ ] **T-001** Judul task
      Format lama (backward compatible, user tentukan agent):
        - [ ] **T-001**: [zaki] Judul task
    """
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

    # Pola format lama: - [ ] **T-001**: [agent] Judul
    RE_LEGACY = re.compile(
        r"-\s+\[(?P<done>[\sxX])\]\s+\*\*(?P<id>T-\d+)\*\*:\s+\[(?P<agent>\w+)\]\s+(?P<title>.+)"
    )
    # Pola format baru: - [ ] **T-001** Judul (tanpa [agent])
    RE_NEW = re.compile(
        r"-\s+\[(?P<done>[\sxX])\]\s+\*\*(?P<id>T-\d+)\*\*\s+(?P<title>[^\[].+)"
    )

    while i < len(lines):
        line = lines[i].strip()

        m_legacy = RE_LEGACY.match(line)
        m_new = RE_NEW.match(line) if not m_legacy else None

        if m_legacy:
            task = {
                "id": m_legacy.group("id"),
                "agent": m_legacy.group("agent"),
                "title": m_legacy.group("title").strip(),
                "done": m_legacy.group("done").strip().lower() == "x",
                "assigned": None,
                "dependencies": [],
                "status": "pending",
                "artifacts": [],
            }
        elif m_new:
            task = {
                "id": m_new.group("id"),
                "agent": None,  # Risko auto-assign via wayang_router
                "title": m_new.group("title").strip(),
                "done": m_new.group("done").strip().lower() == "x",
                "assigned": None,
                "dependencies": [],
                "status": "pending",
                "artifacts": [],
            }
        else:
            i += 1
            continue

        # Parse sub-fields di bawah header task
        j = i + 1
        while j < len(lines):
            sub = lines[j].strip()
            if sub.startswith("- *Assigned*:"):
                task["assigned"] = sub.split(":", 1)[1].strip()
            elif sub.startswith("- *Dependencies*:"):
                raw = sub.split(":", 1)[1].strip()
                task["dependencies"] = [
                    d.strip() for d in raw.split(",")
                    if d.strip() and d.strip().lower() != "none"
                ]
            elif sub.startswith("- *Status*:"):
                task["status"] = sub.split(":", 1)[1].strip()
            elif sub.startswith("- *Artifacts*:"):
                raw = sub.split(":", 1)[1].strip()
                task["artifacts"] = [
                    a.strip() for a in raw.replace("`", "").split(",")
                ]
            elif sub.startswith("- [") or sub.startswith("##") or sub.startswith("---"):
                break
            j += 1

        tasks.append(task)
        i = j

    return {"metadata": frontmatter, "tasks": tasks}


def get_agent_tasks(roadmap: dict, agent_id: str) -> list:
    """Extract hanya task milik agent tertentu (Graphify sub-graph)."""
    return [t for t in roadmap["tasks"] if t.get("assigned") == agent_id]


def get_pending_tasks(roadmap: dict) -> list:
    return [t for t in roadmap["tasks"] if not t["done"]]


def get_next_tasks(roadmap: dict) -> list:
    """Tasks yang semua dependensinya sudah selesai (siap dijalankan)."""
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
    print(f"Total Tasks: {len(tasks)}")
    print()

    print("=== SEMUA TASK ===")
    for t in tasks:
        status = "✅" if t["done"] else "⬜"
        agent_label = t.get("agent") or "auto"
        deps = ", ".join(t["dependencies"]) if t["dependencies"] else "none"
        print(f"  {status} [{t['id']}] ({agent_label}) {t['title']}")
        print(f"       status={t['status']}  deps={deps}")

    print()
    print("=== TASK YANG SIAP DIJALANKAN ===")
    for t in get_next_tasks(roadmap):
        agent_label = t.get("agent") or "auto-assign"
        print(f"  ▶ [{t['id']}] ({agent_label}) {t['title']}")
