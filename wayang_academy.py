"""
Wayang Academy — Modul Pelatihan & Upgrade Skill Wayang
Memungkinkan Bos Muda mengajari keahlian baru kepada para Wayang secara permanen.
Setiap skill yang diajarkan langsung masuk ke knowledge base (standards/) wayang terkait.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import os

from wayang_router import WAYANG_ROSTER

BASE_DIR = Path(__file__).parent
STANDARDS_DIR = BASE_DIR / "standards"

# Mapping file standar per agent
STANDARDS_MAP = {
    "pingot": "pingot_data_standards.md",
    "zaki": "zaki_backend_standards.md",
    "lulu": "lulu_frontend_standards.md",
    "mika": "mika_docs_standards.md",
    "nova": "nova_devops_standards.md",
    "kai": "kai_security_standards.md",
    "ren": "ren_qa_standards.md",
}


def get_wayang_skills(agent_id: str) -> str:
    """Membaca isi buku standar / keahlian seorang wayang saat ini."""
    agent_id = agent_id.lower()
    filename = STANDARDS_MAP.get(agent_id)
    if not filename:
        raise ValueError(f"Wayang '{agent_id}' tidak ditemukan di roster.")

    filepath = STANDARDS_DIR / filename
    if not filepath.exists():
        return f"# Standar untuk {agent_id.upper()} (Belum ada catatan)"

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def teach_wayang(agent_id: str, new_skill: str, instructor: str = "Bos Muda") -> Dict[str, str]:
    """
    Mengajari skill baru kepada seorang wayang.
    Skill ditambahkan ke file standar wayang secara permanen dengan format rapi.
    """
    agent_id = agent_id.lower()
    if agent_id not in STANDARDS_MAP:
        valid = ", ".join(STANDARDS_MAP.keys())
        raise ValueError(f"Wayang '{agent_id}' tidak dikenal. Wayang yang ada: {valid}")

    filename = STANDARDS_MAP[agent_id]
    filepath = STANDARDS_DIR / filename
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Format blok pelajaran baru
    lesson_block = f"""

---

### 🎓 Pelajaran Baru — Diajarkan oleh {instructor} ({now_str})
{new_skill.strip()}
"""

    # Buat direktori jika belum ada
    STANDARDS_DIR.mkdir(parents=True, exist_ok=True)

    if filepath.exists():
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(lesson_block)
    else:
        wayang_info = WAYANG_ROSTER.get(agent_id, {})
        name = wayang_info.get("name", agent_id.capitalize())
        title = wayang_info.get("title", "Wayang")
        initial_content = f"# Standar Keahlian {name} ({title})\n{lesson_block}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(initial_content)

    return {
        "agent": agent_id,
        "wayang_name": WAYANG_ROSTER[agent_id]["name"],
        "wayang_title": WAYANG_ROSTER[agent_id]["title"],
        "learned_at": now_str,
        "skill": new_skill.strip(),
        "file": str(filepath),
    }


def list_all_wayang_skills_summary() -> List[dict]:
    """Melihat ringkasan keahlian dan riwayat pelatihan seluruh wayang."""
    summary = []
    for agent_id, info in WAYANG_ROSTER.items():
        filename = STANDARDS_MAP.get(agent_id)
        learned_count = 0
        file_size_kb = 0.0

        if filename:
            filepath = STANDARDS_DIR / filename
            if filepath.exists():
                file_size_kb = round(os.path.getsize(filepath) / 1024, 1)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    learned_count = content.count("🎓 Pelajaran Baru")

        summary.append({
            "id": agent_id,
            "name": info["name"],
            "title": info["title"],
            "knowledge_base_kb": file_size_kb,
            "custom_lessons": learned_count,
            "core_keywords": info["keywords"][:4],
        })
    return summary
