#!/usr/bin/env python3
"""
dalang.py — CLI Sang Dalang

Cara pakai:
  python3 dalang.py init "Nama Proyek" "Deskripsi proyek"
  python3 dalang.py run
  python3 dalang.py status
  python3 dalang.py roster
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
ROADMAP_PATH = BASE_DIR / "ROADMAP.md"


async def cmd_init(project: str, description: str):
    """Buat ROADMAP.md baru dari deskripsi bebas — Risko yang urus sisanya."""
    from project_planner import decompose_project_to_tasks, format_roadmap_markdown

    print(f"\n🎭 Risko sedang membaca deskripsi proyek '{project}'...")
    print(f"   \"{description}\"\n")

    tasks = await decompose_project_to_tasks(project, description)

    print(f"✅ Risko merencanakan {len(tasks)} tugas:\n")
    for t in tasks:
        from wayang_router import WAYANG_ROSTER
        wayang = WAYANG_ROSTER.get(t.get("agent", ""), {})
        wayang_name = wayang.get("name", t.get("agent", "?"))
        wayang_title = wayang.get("title", "")
        deps = ", ".join(t.get("dependencies", [])) or "—"
        print(f"  {t['id']} → [{wayang_name} / {wayang_title}]")
        print(f"       Tugas     : {t['title']}")
        print(f"       Menunggu  : {deps}")
        print()

    # Cek wayang yang tidak perlu ikut (idle)
    from wayang_router import partition_active_and_idle_wayang
    all_agents = [{**t, "assigned": t.get("agent")} for t in tasks]
    status = partition_active_and_idle_wayang(all_agents)
    from wayang_router import WAYANG_ROSTER
    if status["idle"]:
        idle_names = [f"{WAYANG_ROSTER[a]['name']} ({WAYANG_ROSTER[a]['title']})" for a in status["idle"]]
        print(f"💤 Wayang Idle (tidak diperlukan proyek ini):")
        for n in idle_names:
            print(f"   - {n}")
        print()

    # Tulis ROADMAP.md
    content = format_roadmap_markdown(project, description, tasks)
    with open(ROADMAP_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📄 ROADMAP.md berhasil dibuat: {ROADMAP_PATH}")
    print(f"\nJalankan 'python3 dalang.py run' untuk memulai lakon.\n")


def cmd_status():
    """Tampilkan status ROADMAP.md saat ini."""
    if not ROADMAP_PATH.exists():
        print("❌ ROADMAP.md belum ada. Jalankan: python3 dalang.py init 'Proyek' 'Deskripsi'")
        return

    from roadmap_parser import parse_roadmap
    roadmap = parse_roadmap(str(ROADMAP_PATH))
    tasks = roadmap["tasks"]
    meta = roadmap.get("metadata", {})

    done = [t for t in tasks if t["done"]]
    pending = [t for t in tasks if not t["done"]]

    print(f"\n🎭 {meta.get('project', '—')}")
    print(f"   Total: {len(tasks)} task  |  ✅ Selesai: {len(done)}  |  ⏳ Pending: {len(pending)}\n")

    for t in tasks:
        icon = "✅" if t["done"] else "⏳"
        agent = t.get("agent") or t.get("assigned") or "auto"
        print(f"  {icon} {t['id']} [{agent}] {t['title']}")
    print()


def cmd_roster():
    """Tampilkan daftar semua Wayang beserta keahliannya."""
    from wayang_router import WAYANG_ROSTER

    print("\n🎭 DALANG-AI — ROSTER PARA WAYANG\n")
    icons = {
        "risko": "🟣", "pingot": "🟢", "zaki": "🟡",
        "lulu": "🩷", "mika": "🩵", "nova": "🟠",
        "kai": "🔴", "ren": "🔵",
    }
    for agent_id, info in WAYANG_ROSTER.items():
        icon = icons.get(agent_id, "⚪")
        kw_sample = ", ".join(info["keywords"][:5])
        print(f"  {icon} {info['name']:8} — {info['title']}")
        print(f"           Keahlian: {kw_sample}, ...")
        print()
    print("  Tambah Wayang baru: edit wayang_router.py → WAYANG_ROSTER\n")


def cmd_teach(agent_id: str, skill: str):
    """Ajarkan skill baru kepada seorang Wayang secara permanen."""
    from wayang_academy import teach_wayang

    print(f"\n🎓 Bos Muda mengajarkan skill baru kepada [{agent_id.capitalize()}]...\n")
    print(f"   Skill  : {skill}\n")

    try:
        result = teach_wayang(agent_id, skill, instructor="Bos Muda")
        print(f"✅ [{result['wayang_name']} / {result['wayang_title']}] berhasil mempelajari skill baru!")
        print(f"   Disimpan di : {result['file']}")
        print(f"   Waktu belajar: {result['learned_at']}")
        print(f"\n   Skill ini akan aktif digunakan di sprint/lakon berikutnya.\n")
    except ValueError as e:
        print(f"❌ Error: {e}\n")


def cmd_skills(agent_id: Optional[str] = None):
    """Tampilkan ringkasan keahlian satu atau semua Wayang."""
    from wayang_academy import list_all_wayang_skills_summary, get_wayang_skills

    if agent_id:
        # Tampilkan detail lengkap satu wayang
        agent_id = agent_id.lower()
        try:
            content = get_wayang_skills(agent_id)
            from wayang_router import WAYANG_ROSTER
            info = WAYANG_ROSTER.get(agent_id, {})
            print(f"\n📚 Buku Keahlian {info.get('name', agent_id)} ({info.get('title', '')})\n")
            print(content)
        except ValueError as e:
            print(f"❌ {e}")
        return

    # Tampilkan ringkasan semua wayang
    summary = list_all_wayang_skills_summary()
    icons = {
        "pingot": "🟢", "zaki": "🟡", "lulu": "🩷",
        "mika": "🩵", "nova": "🟠", "kai": "🔴", "ren": "🔵",
    }
    print("\n📚 DALANG-AI — RINGKASAN KEAHLIAN PARA WAYANG\n")
    for s in summary:
        icon = icons.get(s["id"], "⚪")
        lessons_str = f"  🎓 {s['custom_lessons']} pelajaran tambahan" if s["custom_lessons"] > 0 else "  (belum ada pelajaran tambahan)"
        print(f"  {icon} {s['name']:8} — {s['title']}")
        print(f"       Knowledge base : {s['knowledge_base_kb']} KB")
        print(f"       Keahlian inti  : {', '.join(s['core_keywords'])}, ...")
        print(f"      {lessons_str}")
        print()


async def cmd_run(cycles: int):
    """Jalankan orkestrasi Dalang-AI dari ROADMAP.md yang sudah ada."""
    if not ROADMAP_PATH.exists():
        print("❌ ROADMAP.md belum ada. Jalankan: python3 dalang.py init 'Proyek' 'Deskripsi'")
        return

    from risko_orchestrator import RiskoOrchestrator
    orch = RiskoOrchestrator(
        roadmap_path=str(ROADMAP_PATH),
        workspace=str(BASE_DIR / "workspace"),
    )
    print(f"\n🎭 Risko mulai memimpin lakon... (max {cycles} siklus)\n")
    await orch.run_orchestration_cycle(max_cycles=cycles)
    print("\n✅ Lakon selesai. Lihat hasil di workspace/\n")


def main():
    parser = argparse.ArgumentParser(
        prog="dalang",
        description="🎭 Dalang-AI — Multi-Agent Autonomous Studio",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # dalang init
    p_init = sub.add_parser("init", help="Buat ROADMAP.md dari deskripsi proyek")
    p_init.add_argument("project", help="Nama proyek (contoh: 'Aplikasi Kasir Kopi')")
    p_init.add_argument("description", help="Deskripsi bebas tentang proyek yang ingin dibangun")

    # dalang run
    p_run = sub.add_parser("run", help="Mulai lakon (eksekusi ROADMAP.md)")
    p_run.add_argument("--cycles", type=int, default=10, help="Jumlah maksimum siklus orkestrasi (default: 10)")

    # dalang status
    sub.add_parser("status", help="Lihat status ROADMAP.md saat ini")

    # dalang roster
    sub.add_parser("roster", help="Lihat daftar para Wayang dan keahliannya")

    # dalang teach
    p_teach = sub.add_parser("teach", help="Ajarkan skill baru kepada seorang Wayang")
    p_teach.add_argument("wayang", help="Nama wayang (pingot/zaki/lulu/mika/nova/kai/ren)")
    p_teach.add_argument("skill", help="Skill atau instruksi baru yang ingin diajarkan")

    # dalang skills
    p_skills = sub.add_parser("skills", help="Lihat ringkasan keahlian semua Wayang")
    p_skills.add_argument("--wayang", default=None, help="Filter ke satu wayang saja (opsional)")

    args = parser.parse_args()

    if args.command == "init":
        asyncio.run(cmd_init(args.project, args.description))
    elif args.command == "run":
        asyncio.run(cmd_run(args.cycles))
    elif args.command == "status":
        cmd_status()
    elif args.command == "roster":
        cmd_roster()
    elif args.command == "teach":
        cmd_teach(args.wayang, args.skill)
    elif args.command == "skills":
        cmd_skills(args.wayang)


if __name__ == "__main__":
    main()
