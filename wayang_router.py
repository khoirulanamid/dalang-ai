"""
Wayang Router — Modul Auto-Routing Risko (Sang Dalang)
Menganalisis deskripsi task dan otomatis menunjuk Wayang yang paling berkompeten.
Wayang yang tidak relevan tetap idle (diam di tempat).
"""

import re
from typing import Dict, List, Optional, Tuple

WAYANG_ROSTER = {
    "pingot": {
        "name": "Pingot",
        "title": "Wayang Data",
        "keywords": [
            "database", "schema", "sql", "migration", "data model", "domain model",
            "orm", "pydantic", "sqlite", "postgres", "mysql", "redis", "contract",
            "iso 8601", "json schema", "entity", "value object", "repository", "tabel"
        ],
        "weight": 1.0,
    },
    "zaki": {
        "name": "Zaki",
        "title": "Wayang Backend",
        "keywords": [
            "backend", "api", "fastapi", "rest", "endpoint", "crud", "auth",
            "token", "jwt", "login", "register", "controller", "service",
            "business logic", "route", "server", "middleware", "handler"
        ],
        "weight": 1.0,
    },
    "lulu": {
        "name": "Lulu",
        "title": "Wayang Visual",
        "keywords": [
            "frontend", "ui", "ux", "tampilan", "antarmuka", "halaman", "css",
            "html", "react", "component", "button", "form", "layout", "responsive",
            "three.js", "canvas", "styling", "modal", "table view", "wcag", "aksesibilitas"
        ],
        "weight": 1.0,
    },
    "mika": {
        "name": "Mika",
        "title": "Wayang Pujangga",
        "keywords": [
            "dokumen", "dokumentasi", "docs", "readme", "quickstart", "tutorial",
            "panduan", "guide", "buku petunjuk", "openapi", "swagger", "diataxis",
            "architecture.md", "manual", "catatan rilis", "release notes",
            "tulis", "penulisan", "jelaskan", "jelaskan cara", "cara menggunakan",
            "instruksi", "langkah", "artikel", "blog", "changelog", "wiki"
        ],
        "weight": 1.5,
    },
    "nova": {
        "name": "Nova",
        "title": "Wayang Patih",
        "keywords": [
            "devops", "docker", "dockerfile", "compose", "ci/cd", "github actions",
            "pipeline", "nginx", "deploy", "deployment", "container", "infrastructure",
            "workflow", "linux", "systemd", "build", "image"
        ],
        "weight": 1.0,
    },
    "kai": {
        "name": "Kai",
        "title": "Wayang Senopati",
        "keywords": [
            "security", "keamanan", "audit", "vulnerability", "pentest", "owasp",
            "asvs", "cvss", "bandit", "pip-audit", "sast", "injection", "xss",
            "csrf", "hashing", "hardening", "rahasia", "enkripsi"
        ],
        "weight": 1.0,
    },
    "ren": {
        "name": "Ren",
        "title": "Wayang Jaksa",
        "keywords": [
            "test", "testing", "pengujian", "uji coba", "qa", "unit test",
            "integration test", "e2e", "pytest", "bva", "aaa pattern", "assertion",
            "scenario", "mock", "verifikasi", "validasi"
        ],
        "weight": 1.0,
    },
}


def score_agent_fit(text: str, agent_id: str) -> float:
    """Menghitung skor kesesuaian wayang terhadap suatu deskripsi task."""
    meta = WAYANG_ROSTER.get(agent_id)
    if not meta:
        return 0.0

    text_lower = text.lower()
    score = 0.0

    for kw in meta["keywords"]:
        # Match whole word or exact substring
        pattern = r"\b" + re.escape(kw) + r"\b"
        matches = len(re.findall(pattern, text_lower))
        if matches > 0:
            score += matches * 2.0
        elif kw in text_lower:
            score += 1.0

    return score * meta["weight"]


def auto_route_task(title: str, description: str = "", explicit_agent: Optional[str] = None) -> Tuple[str, float]:
    """
    Menentukan Wayang terbaik untuk suatu task.
    Jika user sudah menulis explicit_agent (misal: 'zaki'), hormati pilihan user.
    Jika tidak, Risko melakukan auto-scoring berbasis NLP keyword.
    
    Returns: (agent_id, confidence_score)
    """
    if explicit_agent and explicit_agent.lower() in WAYANG_ROSTER:
        return explicit_agent.lower(), 10.0

    combined = f"{title} {description}"
    scores = {}

    for agent_id in WAYANG_ROSTER.keys():
        scores[agent_id] = score_agent_fit(combined, agent_id)

    # Ambil skor tertinggi
    sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_agent, best_score = sorted_agents[0]

    # Fallback jika tidak ada keyword yang cocok sama sekali
    if best_score == 0:
        # Default fallback: jika ada unsur coding umum -> zaki, jika tidak -> mika
        best_agent = "zaki"
        best_score = 0.5

    return best_agent, best_score


def partition_active_and_idle_wayang(tasks: List[dict]) -> Dict[str, list]:
    """
    Memisahkan Wayang mana yang aktif (memegang task) dan mana yang idle (diam).
    """
    active = {}
    all_known = set(WAYANG_ROSTER.keys())

    for t in tasks:
        agent = t.get("assigned") or t.get("agent")
        if agent and agent in all_known:
            if agent not in active:
                active[agent] = []
            active[agent].append(t.get("id"))

    idle = [a for a in all_known if a not in active]

    return {
        "active": active,
        "idle": idle,
        "total_active": len(active),
        "total_idle": len(idle),
    }
