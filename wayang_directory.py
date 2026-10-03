"""
wayang_directory.py

Direktori resmi seluruh anggota tim Dalang-AI (12 Wayang Resmi Nusantara).
Menyimpan profil keahlian, domain tugas, alat utama, dan kontak rujukan
dalam bentuk domain model yang ketat sesuai prinsip Domain-Driven Design (DDD).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import FrozenSet, Sequence, Tuple


class AgentRole(str, Enum):
    """Peran fungsional 12 Wayang resmi dalam tim Dalang-AI."""
    ORCHESTRATOR = "orchestrator"
    BACKEND_ENGINEER = "backend_engineer"
    FRONTEND_ENGINEER = "frontend_engineer"
    DATA_ARCHITECT = "data_architect"
    SECURITY_ANALYST = "security_analyst"
    QA_ENGINEER = "qa_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    GRAPHIC_DESIGNER = "graphic_designer"
    MOTION_ANIMATOR = "motion_animator"
    CONTENT_STRATEGIST = "content_strategist"
    ASSET_CUSTODIAN = "asset_custodian"
    DOCUMENTATION_WRITER = "documentation_writer"


@dataclass(frozen=True)
class WayangId:
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[a-z0-9_-]{2,32}$", self.value):
            raise ValueError(f"Invalid wayang_id: '{self.value}'")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ExpertiseDomain:
    name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("ExpertiseDomain name cannot be empty")

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class ContactHandle:
    email: str
    slack: str

    def __post_init__(self) -> None:
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        if not self.slack.startswith("@"):
            raise ValueError(f"Slack handle must start with '@': {self.slack}")


@dataclass(frozen=True)
class WayangProfile:
    wayang_id: WayangId
    display_name: str
    role: AgentRole
    expertise_domains: Sequence[ExpertiseDomain]
    assigned_tasks: Sequence[str]
    is_available: bool
    contact: ContactHandle

    def has_expertise(self, domain_name: str) -> bool:
        target = domain_name.lower().strip()
        return any(target in e.name.lower() for e in self.expertise_domains)

    def handles_task(self, task_description: str) -> bool:
        desc = task_description.lower()
        return any(e.name.lower() in desc for e in self.expertise_domains)


class WayangDirectory:
    def __init__(self) -> None:
        self._profiles: dict[str, WayangProfile] = {}

    def register(self, profile: WayangProfile) -> None:
        key = str(profile.wayang_id)
        self._profiles[key] = profile

    def find_by_id(self, wayang_id: str) -> WayangProfile:
        if wayang_id not in self._profiles:
            raise KeyError(f"Wayang with id '{wayang_id}' not found in directory")
        return self._profiles[wayang_id]

    def find_by_role(self, role: AgentRole) -> list[WayangProfile]:
        return [p for p in self._profiles.values() if p.role == role]

    def all_profiles(self) -> list[WayangProfile]:
        return list(self._profiles.values())

    def count(self) -> int:
        return len(self._profiles)


def build_dalang_directory() -> WayangDirectory:
    d = WayangDirectory()

    raw_roster = [
        ("risko", "Risko — Sang Dalang", AgentRole.ORCHESTRATOR,
         ["Task Decomposition", "Multi-agent Orchestration", "Roadmap Execution", "Project Management"],
         "risko@dalang.ai", "@risko"),
        ("pingot", "Pingot — Wayang Data", AgentRole.DATA_ARCHITECT,
         ["Schema Design", "Domain-Driven Design", "Data Modeling", "SQL", "Pydantic", "ISO 8601"],
         "pingot@dalang.ai", "@pingot"),
        ("zaki", "Zaki — Wayang Backend", AgentRole.BACKEND_ENGINEER,
         ["FastAPI", "REST API", "Browser Automation", "Playwright", "Subprocess Execution", "Authentication"],
         "zaki@dalang.ai", "@zaki"),
        ("lulu", "Lulu — Wayang Visual", AgentRole.FRONTEND_ENGINEER,
         ["React", "UI/UX", "Canvas 2D", "Accessibility", "TailwindCSS", "CSS Animation"],
         "lulu@dalang.ai", "@lulu"),
        ("mika", "Mika — Wayang Pujangga", AgentRole.DOCUMENTATION_WRITER,
         ["Technical Writing", "Diataxis Documentation", "API Guides", "README", "Release Notes"],
         "mika@dalang.ai", "@mika"),
        ("nova", "Nova — Wayang Patih", AgentRole.DEVOPS_ENGINEER,
         ["Docker", "CI/CD", "Infrastructure as Code", "Monitoring", "Linux Automation", "Deployment"],
         "nova@dalang.ai", "@nova"),
        ("kai", "Kai — Wayang Senopati", AgentRole.SECURITY_ANALYST,
         ["Penetration Testing", "OWASP Audit", "Sanitization", "Permission Checks", "Vulnerability Scan"],
         "kai@dalang.ai", "@kai"),
        ("ren", "Ren — Wayang Jaksa", AgentRole.QA_ENGINEER,
         ["Test Automation", "Pytest", "Quality Gates", "E2E Testing", "Physical Artifact Verification"],
         "ren@dalang.ai", "@ren"),
        ("wiku", "Wiku — Wayang Pematung", AgentRole.GRAPHIC_DESIGNER,
         ["3D Modeling", "Three.js", "Spatial Geometry", "Procedural Assets", "WebGL"],
         "wiku@dalang.ai", "@wiku"),
        ("kresna", "Kresna — Wayang Sutradara", AgentRole.MOTION_ANIMATOR,
         ["Motion Graphics", "Canvas Video", "Explainer Films", "Visual Storytelling", "Pillow"],
         "kresna@dalang.ai", "@kresna"),
        ("bagong", "Bagong — Wayang Juru Simpan", AgentRole.ASSET_CUSTODIAN,
         ["Asset Vault", "Artifact Indexing", "Release Custody", "Storage Archival", "Git Synchronization"],
         "bagong@dalang.ai", "@bagong"),
        ("gathot", "Gathot — Wayang Wira Warta", AgentRole.CONTENT_STRATEGIST,
         ["Social Media", "Viral Copywriting", "Hook Psychology", "Hashtag Optimization", "Omnichannel Publishing"],
         "gathot@dalang.ai", "@gathot"),
    ]

    for wid, name, role, domains, email, slack in raw_roster:
        profile = WayangProfile(
            wayang_id=WayangId(wid),
            display_name=name,
            role=role,
            expertise_domains=[ExpertiseDomain(dom) for dom in domains],
            assigned_tasks=[],
            is_available=True,
            contact=ContactHandle(email=email, slack=slack),
        )
        d.register(profile)

    return d


def get_directory() -> WayangDirectory:
    return build_dalang_directory()
