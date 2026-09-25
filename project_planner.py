"""
Project Planner — Modul Perencanaan Proyek Otomatis Risko (Sang Dalang)
Menerima deskripsi bebas dari user dan otomatis memecahnya menjadi daftar subtask
terstruktur dengan dependensi dan assignment Wayang yang tepat.
"""

import json
import logging
import re
from typing import Dict, List, Optional
import httpx

from wayang_router import auto_route_task, WAYANG_ROSTER
from real_subagent_runner import _load_api_key

logger = logging.getLogger("Risko.Planner")

RISKO_PLANNER_SYSTEM_PROMPT = """Kamu adalah Risko, Sang Dalang (Master Technical Lead & Orchestrator di Dalang-AI).
Tugasmu adalah menganalisis ide/deskripsi proyek yang diberikan oleh Sang Sutradara (User),
lalu memecahnya menjadi daftar tugas (tasks) teknis yang siap dikerjakan oleh para Wayang.

Daftar Wayang dan keahlian mereka:
- pingot : Data Architect, Schema, SQL, Domain-Driven Design (DDD), ISO 8601
- zaki   : Backend Engineer, REST API, FastAPI, Auth, Business Logic, SOLID
- lulu   : Visual & Frontend, UI/UX, React, HTML, CSS, WCAG 2.1 AA, Anti-Slop UI
- mika   : Pujangga / Technical Writer, Dokumentasi Diátaxis, Quickstart, OpenAPI
- nova   : Patih / DevOps, Docker, CIS Hardened, CI/CD GitHub Actions
- kai    : Senopati / Security, OWASP ASVS v4.0, Pentest, Hashing, CVSS
- ren    : Jaksa / QA Lead, pytest, AAA Pattern, Boundary Value Analysis (BVA)

ATURAN PENTING:
1. HANYA libatkan Wayang yang RELEVAN dengan proyek.
   - Proyek kalkulator sederhana? Cukup Lulu (UI), Zaki (Logic/API jika ada), Ren (Test). Wayang lain BIARKAN IDLE/DIAM!
   - Proyek CRUD data? Butuh Pingot, Zaki, Lulu, Ren, Mika.
2. Urutkan dependensi secara logis:
   - Schema/Data (T-001) -> Backend (T-002 depends on T-001) -> Frontend & Test (depends on T-002).
3. Output WAJIB berupa JSON VALID murni tanpa pembuka/penutup markdown ```json. Format:
{
  "tasks": [
    {
      "id": "T-001",
      "agent": "pingot",
      "title": "Deskripsi singkat dan jelas tugas",
      "dependencies": []
    },
    {
      "id": "T-002",
      "agent": "zaki",
      "title": "Deskripsi tugas backend",
      "dependencies": ["T-001"]
    }
  ]
}
"""


def _generate_fallback_plan(project: str, description: str) -> List[dict]:
    """
    Fallback deterministic planner jika LLM sedang offline / tidak terjangkau.
    Menggunakan analisis kata kunci untuk menghasilkan 2-5 task logis.
    """
    desc_lower = description.lower()
    tasks = []
    tid = 1

    needs_data = any(w in desc_lower for w in ["database", "db", "tabel", "skema", "schema", "model", "simpan", "data"])
    needs_backend = any(w in desc_lower for w in ["api", "backend", "crud", "endpoint", "server", "logic", "perhitungan", "hitung", "proses"])
    needs_frontend = any(w in desc_lower for w in ["tampilan", "ui", "ux", "halaman", "web", "kalkulator", "antarmuka", "tombol", "layar"])
    needs_auth = any(w in desc_lower for w in ["login", "register", "auth", "token", "password", "keamanan", "security"])

    prev_id = None

    if needs_data:
        curr_id = f"T-{tid:03}"
        tasks.append({
            "id": curr_id,
            "agent": "pingot",
            "title": f"Rancang skema data dan model domain untuk {project}",
            "dependencies": [],
        })
        prev_id = curr_id
        tid += 1

    if needs_backend or (not needs_frontend and not needs_data):
        curr_id = f"T-{tid:03}"
        deps = [prev_id] if prev_id else []
        tasks.append({
            "id": curr_id,
            "agent": "zaki",
            "title": f"Implementasikan core logic dan API endpoint untuk {project}",
            "dependencies": deps,
        })
        prev_id = curr_id
        tid += 1

    if needs_frontend:
        curr_id = f"T-{tid:03}"
        deps = [prev_id] if prev_id else []
        tasks.append({
            "id": curr_id,
            "agent": "lulu",
            "title": f"Bangun antarmuka visual (UI) responsif dan aksesibel untuk {project}",
            "dependencies": deps,
        })
        tid += 1

    if needs_auth:
        curr_id = f"T-{tid:03}"
        tasks.append({
            "id": curr_id,
            "agent": "kai",
            "title": f"Audit keamanan dan verifikasi kerentanan auth untuk {project}",
            "dependencies": [prev_id] if prev_id else [],
        })
        tid += 1

    # Selalu sertakan QA
    test_id = f"T-{tid:03}"
    all_prev = [t["id"] for t in tasks]
    tasks.append({
        "id": test_id,
        "agent": "ren",
        "title": f"Tulis automated unit test dan integration test untuk {project}",
        "dependencies": all_prev[:2] if all_prev else [],
    })
    tid += 1

    # Dokumentasi
    doc_id = f"T-{tid:03}"
    tasks.append({
        "id": doc_id,
        "agent": "mika",
        "title": f"Tulis panduan penggunaan dan dokumentasi teknis untuk {project}",
        "dependencies": [],
    })

    return tasks


async def decompose_project_to_tasks(project: str, description: str, gateway_url: str = "http://192.168.1.100:20127/v1") -> List[dict]:
    """
    Risko menganalisis ide proyek dan memecahnya menjadi subtask terstruktur.
    Mencoba LLM terlebih dahulu; jika timeout/gagal, beralih ke fallback cerdas.
    """
    api_key = _load_api_key()
    user_prompt = f"Proyek: {project}\nDeskripsi: {description}\n\nBuat rencana tugas (tasks) untuk para Wayang."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": "auto",
        "messages": [
            {"role": "system", "content": RISKO_PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{gateway_url}/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                # Bersihkan markdown formatting jika LLM memasukkannya
                content = re.sub(r"^```json\s*", "", content, flags=re.MULTILINE)
                content = re.sub(r"^```\s*", "", content, flags=re.MULTILINE)
                parsed = json.loads(content)
                if "tasks" in parsed and isinstance(parsed["tasks"], list) and len(parsed["tasks"]) > 0:
                    logger.info(f"[Planner] LLM berhasil merencanakan {len(parsed['tasks'])} task untuk '{project}'")
                    return parsed["tasks"]
    except Exception as e:
        logger.warning(f"[Planner] LLM decomposition gagal atau timeout ({e}), menggunakan fallback cerdas.")

    # Fallback jika LLM gagal / tidak ada koneksi
    return _generate_fallback_plan(project, description)


def format_roadmap_markdown(project: str, description: str, tasks: List[dict], version: str = "1.0.0") -> str:
    """
    Mengubah hasil perencanaan menjadi file ROADMAP.md yang valid dan rapi.
    """
    header = f"""---
project: {project}
description: >
  {description}
version: {version}
orchestrator: Risko (Sang Dalang)
---

# 🎭 {project} — Master Roadmap

> **Deskripsi Proyek**: {description}
> **Direncanakan oleh**: Risko (Sang Dalang)

## Daftar Tugas Para Wayang

"""
    body_lines = []
    for t in tasks:
        agent = t.get("agent", "auto")
        deps_str = ", ".join(t.get("dependencies", [])) if t.get("dependencies") else "none"
        body_lines.append(f"- [ ] **{t['id']}**: [{agent}] {t['title']}")
        body_lines.append(f"  - *Assigned*: {agent}")
        body_lines.append(f"  - *Dependencies*: {deps_str}")
        body_lines.append(f"  - *Status*: pending")
        body_lines.append("")

    return header + "\n".join(body_lines)
