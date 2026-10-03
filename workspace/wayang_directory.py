"""
wayang_directory.py

Direktori resmi seluruh anggota tim Dalang-AI (12 Wayang).
Menyimpan profil keahlian, domain tugas, alat utama, dan kontak rujukan
dalam bentuk domain model yang ketat sesuai prinsip Domain-Driven Design (DDD).

Setiap Wayang dimodelkan sebagai Entity dengan identitas unik (wayang_id),
sedangkan atribut seperti ExpertiseDomain dan ContactHandle adalah Value Objects
yang bersifat immutable dan divalidasi saat konstruksi.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import FrozenSet, Sequence, Tuple


class AgentRole(str, Enum):
    """Peran fungsional seorang Wayang dalam tim Dalang-AI."""
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
    MICROSTOCK_SPECIALIST = "microstock_specialist"
    DOCUMENTATION_WRITER = "documentation_writer"


class AvailabilityStatus(str, Enum):
    """Status ketersediaan Wayang untuk menerima tugas baru."""
    ACTIVE = "active"
    BUSY = "busy"
    STANDBY = "standby"
    OFFLINE = "offline"


@dataclass(frozen=True)
class WayangId:
    """
    Identitas unik seorang Wayang.
    Format: huruf kecil alfanumerik diawali huruf alfabet, 2 hingga 32 karakter.
    """
    value: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_]{1,31}", self.value):
            raise ValueError(
                f"WayangId '{self.value}' tidak valid. "
                "Harus diawali huruf kecil, hanya alfanumerik/underscore, 2–32 karakter."
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ExpertiseDomain:
    """Domain keahlian spesifik yang dimiliki seorang Wayang."""
    name: str

    def __post_init__(self) -> None:
        stripped = self.name.strip()
        if not stripped or len(stripped) > 80:
            raise ValueError(
                f"ExpertiseDomain '{self.name}' tidak valid. "
                "Nama tidak boleh kosong dan maksimal 80 karakter."
            )
        object.__setattr__(self, "name", stripped)

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class ContactHandle:
    """Kontak rujukan internal tim berbentuk handle terstandarisasi (@<wayang_id>)."""
    handle: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"@[a-z][a-z0-9_]{1,31}", self.handle):
            raise ValueError(
                f"ContactHandle '{self.handle}' tidak valid. "
                "Harus diawali '@', diikuti wayang_id yang valid."
            )

    def __str__(self) -> str:
        return self.handle


@dataclass(frozen=True)
class TaskDomain:
    """Domain tanggung jawab tugas seorang Wayang."""
    description: str

    def __post_init__(self) -> None:
        stripped = self.description.strip()
        if not stripped or len(stripped) > 120:
            raise ValueError(
                f"TaskDomain '{self.description}' tidak valid. "
                "Deskripsi tidak boleh kosong dan maksimal 120 karakter."
            )
        object.__setattr__(self, "description", stripped)

    def __str__(self) -> str:
        return self.description


@dataclass
class WayangProfile:
    """
    Entity yang merepresentasikan profil lengkap seorang Wayang.

    Identitas ditentukan oleh wayang_id. Semua koleksi disimpan sebagai
    frozenset untuk menjamin immutability konten dan mencegah duplikasi.
    """
    wayang_id: WayangId
    display_name: str
    role: AgentRole
    expertise_domains: FrozenSet[ExpertiseDomain]
    task_domains: FrozenSet[TaskDomain]
    primary_tools: FrozenSet[str]
    contact_handle: ContactHandle
    availability: AvailabilityStatus
    registered_at: datetime

    def __post_init__(self) -> None:
        self._validate_display_name()
        self._validate_collections_not_empty()
        self._validate_registered_at_utc()
        self._validate_contact_matches_id()

    def _validate_display_name(self) -> None:
        name = self.display_name.strip()
        if not name or len(name) > 64:
            raise ValueError(
                "display_name tidak boleh kosong dan maksimal 64 karakter."
            )
        self.display_name = name

    def _validate_collections_not_empty(self) -> None:
        if not self.expertise_domains:
            raise ValueError(
                f"Wayang '{self.wayang_id}' harus memiliki minimal satu ExpertiseDomain."
            )
        if not self.task_domains:
            raise ValueError(
                f"Wayang '{self.wayang_id}' harus memiliki minimal satu TaskDomain."
            )
        if not self.primary_tools:
            raise ValueError(
                f"Wayang '{self.wayang_id}' harus memiliki minimal satu primary tool."
            )

    def _validate_registered_at_utc(self) -> None:
        if self.registered_at.tzinfo is None or self.registered_at.tzinfo.utcoffset(self.registered_at) is None:
            raise ValueError(
                "registered_at harus berupa datetime timezone-aware (UTC)."
            )

    def _validate_contact_matches_id(self) -> None:
        expected_handle = f"@{self.wayang_id.value}"
        if self.contact_handle.handle != expected_handle:
            raise ValueError(
                f"ContactHandle '{self.contact_handle}' tidak sesuai dengan "
                f"wayang_id '{self.wayang_id}'. Harus '{expected_handle}'."
            )

    def has_expertise(self, domain_name: str) -> bool:
        """Evaluasi kepemilikan keahlian tertentu secara case-insensitive."""
        return any(
            ed.name.lower() == domain_name.lower()
            for ed in self.expertise_domains
        )

    def handles_task(self, task_description: str) -> bool:
        """Evaluasi kecocokan substring pada domain tugas."""
        return any(
            task_description.lower() in td.description.lower()
            for td in self.task_domains
        )

    def to_public_summary(self) -> "WayangPublicSummary":
        """Proyeksi publik untuk eksposur data tanpa membocorkan struktur internal."""
        return WayangPublicSummary(
            wayang_id=str(self.wayang_id),
            display_name=self.display_name,
            role=self.role.value,
            expertise_domains=sorted(str(ed) for ed in self.expertise_domains),
            task_domains=sorted(str(td) for td in self.task_domains),
            primary_tools=sorted(self.primary_tools),
            contact_handle=str(self.contact_handle),
            availability=self.availability.value,
            registered_at=self.registered_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )


@dataclass(frozen=True)
class WayangPublicSummary:
    """
    Model proyeksi publik untuk eksposur API dan visualisasi antarmuka.
    Menghindari eksposur representasi internal domain entity.
    """
    wayang_id: str
    display_name: str
    role: str
    expertise_domains: Tuple[str, ...]
    task_domains: Tuple[str, ...]
    primary_tools: Tuple[str, ...]
    contact_handle: str
    availability: str
    registered_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "expertise_domains", tuple(self.expertise_domains))
        object.__setattr__(self, "task_domains", tuple(self.task_domains))
        object.__setattr__(self, "primary_tools", tuple(self.primary_tools))


class WayangDirectory:
    """
    Aggregate Root pengelola direktori profil seluruh Wayang.
    Menegakkan invarian keunikan identitas agen dalam direktori.
    """

    def __init__(self) -> None:
        self._registry: dict[str, WayangProfile] = {}

    def register(self, profile: WayangProfile) -> None:
        """Daftarkan profil baru ke dalam direktori."""
        key = str(profile.wayang_id)
        if key in self._registry:
            raise ValueError(
                f"Wayang dengan id '{key}' sudah terdaftar dalam direktori."
            )
        self._registry[key] = profile

    def find_by_id(self, wayang_id: str) -> WayangProfile:
        """Cari profil berdasarkan ID unik."""
        profile = self._registry.get(wayang_id)
        if profile is None:
            raise KeyError(f"Wayang '{wayang_id}' tidak ditemukan dalam direktori.")
        return profile

    def find_by_role(self, role: AgentRole) -> list[WayangProfile]:
        """Filter profil berdasarkan peran fungsional."""
        return [p for p in self._registry.values() if p.role == role]

    def find_by_expertise(self, domain_name: str) -> list[WayangProfile]:
        """Filter profil yang menguasai domain keahlian tertentu."""
        return [p for p in self._registry.values() if p.has_expertise(domain_name)]

    def find_available(self) -> list[WayangProfile]:
        """Filter profil yang siap menerima delegasi tugas."""
        return [
            p for p in self._registry.values()
            if p.availability in (AvailabilityStatus.ACTIVE, AvailabilityStatus.STANDBY)
        ]

    def all_profiles(self) -> list[WayangProfile]:
        """Daftar seluruh profil terurut berdasarkan ID."""
        return sorted(self._registry.values(), key=lambda p: str(p.wayang_id))

    def count(self) -> int:
        """Jumlah total agen terdaftar."""
        return len(self._registry)

    def public_roster(self) -> list[WayangPublicSummary]:
        """Daftar ringkasan publik seluruh agen."""
        return [p.to_public_summary() for p in self.all_profiles()]


def _utc(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, 0, 0, 0, tzinfo=timezone.utc)


def _profile(
    wayang_id: str,
    display_name: str,
    role: AgentRole,
    expertise: Sequence[str],
    tasks: Sequence[str],
    tools: Sequence[str],
    availability: AvailabilityStatus,
    registered_at: datetime,
) -> WayangProfile:
    return WayangProfile(
        wayang_id=WayangId(wayang_id),
        display_name=display_name,
        role=role,
        expertise_domains=frozenset(ExpertiseDomain(e) for e in expertise),
        task_domains=frozenset(TaskDomain(t) for t in tasks),
        primary_tools=frozenset(tools),
        contact_handle=ContactHandle(f"@{wayang_id}"),
        availability=availability,
        registered_at=registered_at,
    )


def build_dalang_directory() -> WayangDirectory:
    """
    Inisialisasi direktori dengan 12 Wayang resmi tim Dalang-AI.
    Sumber kebenaran tunggal komposisi tim multi-disiplin kantor.
    """
    directory = WayangDirectory()

    profiles = [
        _profile(
            wayang_id="kai",
            display_name="Kai — Lead Orchestrator",
            role=AgentRole.ORCHESTRATOR,
            expertise=["Multi-agent Orchestration", "Task Decomposition", "Sprint Planning", "Risk Assessment"],
            tasks=["Koordinasi lintas-agen", "Dekomposisi tugas kompleks", "Manajemen dependensi antar-task", "Eskalasi keputusan strategis"],
            tools=["Dalang Orchestration Engine", "Task Graph Planner", "Handover Gate Protocol"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="zaki",
            display_name="Zaki — Backend Engineer",
            role=AgentRole.BACKEND_ENGINEER,
            expertise=["FastAPI", "Python", "PostgreSQL", "REST API Design", "SQLAlchemy", "Async Programming"],
            tasks=["Desain dan implementasi REST API", "Manajemen database relasional", "Autentikasi dan otorisasi", "Integrasi layanan eksternal"],
            tools=["FastAPI", "SQLAlchemy", "Alembic", "PostgreSQL", "Redis", "Pytest"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="ren",
            display_name="Ren — Frontend Engineer",
            role=AgentRole.FRONTEND_ENGINEER,
            expertise=["React", "TypeScript", "Next.js", "Tailwind CSS", "State Management", "Web Accessibility"],
            tasks=["Implementasi UI komponen", "Integrasi API ke frontend", "Optimasi performa halaman", "Responsivitas dan aksesibilitas"],
            tools=["React", "Next.js", "TypeScript", "Tailwind CSS", "Vite", "Storybook"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="pingot",
            display_name="Pingot — Senior Data Architect",
            role=AgentRole.DATA_ARCHITECT,
            expertise=["Domain-Driven Design", "Data Modeling", "Schema Design", "Pydantic", "Data Contracts", "PostgreSQL"],
            tasks=["Desain model domain dan schema", "Definisi data contracts antar-layanan", "Validasi invariant data", "Proyeksi model publik vs internal"],
            tools=["Pydantic", "SQLAlchemy", "Alembic", "PostgreSQL", "dataclasses", "Pytest"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="nova",
            display_name="Nova — Security Analyst",
            role=AgentRole.SECURITY_ANALYST,
            expertise=["OWASP Top 10", "Penetration Testing", "JWT Security", "Cryptography", "SQL Injection Prevention", "Threat Modeling"],
            tasks=["Audit keamanan kode dan infrastruktur", "Implementasi autentikasi aman", "Analisis kerentanan dependensi", "Definisi security policy"],
            tools=["Bandit", "OWASP ZAP", "Semgrep", "PyJWT", "cryptography", "passlib"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="tara",
            display_name="Tara — QA Engineer",
            role=AgentRole.QA_ENGINEER,
            expertise=["Test Automation", "Pytest", "Integration Testing", "End-to-End Testing", "Test Coverage Analysis", "Bug Triage"],
            tasks=["Penulisan test suite otomatis", "Validasi acceptance criteria", "Regression testing", "Laporan kualitas dan coverage"],
            tools=["Pytest", "httpx", "Playwright", "Coverage.py", "Allure Report"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="deva",
            display_name="Deva — DevOps Engineer",
            role=AgentRole.DEVOPS_ENGINEER,
            expertise=["Docker", "CI/CD", "GitHub Actions", "Kubernetes", "Infrastructure as Code", "Monitoring"],
            tasks=["Konfigurasi pipeline CI/CD", "Containerisasi aplikasi", "Manajemen environment dan secrets", "Monitoring dan alerting infrastruktur"],
            tools=["Docker", "GitHub Actions", "Kubernetes", "Terraform", "Prometheus", "Grafana"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="sari",
            display_name="Sari — Graphic Designer",
            role=AgentRole.GRAPHIC_DESIGNER,
            expertise=["Brand Identity", "UI Design", "Typography", "Color Theory", "Figma", "Adobe Illustrator"],
            tasks=["Desain identitas visual brand", "Pembuatan aset grafis UI", "Panduan gaya visual (style guide)", "Desain materi pemasaran digital"],
            tools=["Figma", "Adobe Illustrator", "Adobe Photoshop", "Canva Pro"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="vino",
            display_name="Vino — Motion Animator",
            role=AgentRole.MOTION_ANIMATOR,
            expertise=["Motion Graphics", "After Effects", "Video Editing", "2D Animation", "Lottie Animation", "Storyboarding"],
            tasks=["Produksi animasi motion graphics", "Editing video konten promosi", "Pembuatan animasi UI (Lottie)", "Storyboard untuk konten video"],
            tools=["Adobe After Effects", "Adobe Premiere Pro", "LottieFiles", "DaVinci Resolve"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="lena",
            display_name="Lena — Content Strategist",
            role=AgentRole.CONTENT_STRATEGIST,
            expertise=["Content Strategy", "Copywriting", "SEO", "Social Media Marketing", "Audience Analysis", "Editorial Planning"],
            tasks=["Strategi konten multi-platform", "Penulisan copy iklan dan landing page", "Perencanaan kalender editorial", "Analisis performa konten"],
            tools=["Notion", "Google Analytics", "Ahrefs", "Buffer", "ChatGPT API"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="riko",
            display_name="Riko — Microstock Specialist",
            role=AgentRole.MICROSTOCK_SPECIALIST,
            expertise=["Stock Photography", "Vector Illustration", "Keyword Research", "Shutterstock", "Adobe Stock", "Earnings Optimization"],
            tasks=["Produksi aset microstock (foto/vektor)", "Riset keyword dan metadata microstock", "Optimasi portofolio di platform stock", "Analisis tren pasar microstock"],
            tools=["Adobe Illustrator", "Adobe Lightroom", "Shutterstock Contributor", "Adobe Stock", "Pond5"],
            availability=AvailabilityStatus.STANDBY,
            registered_at=_utc(2025, 1, 1),
        ),
        _profile(
            wayang_id="doku",
            display_name="Doku — Documentation Writer",
            role=AgentRole.DOCUMENTATION_WRITER,
            expertise=["Technical Writing", "API Documentation", "Markdown", "Docusaurus", "OpenAPI/Swagger", "User Guides"],
            tasks=["Penulisan dokumentasi teknis API", "Pembuatan user guide dan tutorial", "Pemeliharaan changelog dan release notes", "Standarisasi format dokumentasi tim"],
            tools=["Docusaurus", "MkDocs", "Swagger UI", "Markdown", "Notion", "Confluence"],
            availability=AvailabilityStatus.ACTIVE,
            registered_at=_utc(2025, 1, 1),
        ),
    ]

    for profile in profiles:
        directory.register(profile)

    return directory


_DIRECTORY_INSTANCE: WayangDirectory | None = None


def get_directory() -> WayangDirectory:
    """Singleton direktori untuk menghindari overhead rekonstruksi berulang."""
    global _DIRECTORY_INSTANCE
    if _DIRECTORY_INSTANCE is None:
        _DIRECTORY_INSTANCE = build_dalang_directory()
    return _DIRECTORY_INSTANCE
