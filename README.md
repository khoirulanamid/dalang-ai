<div align="center">

> 🎁 **SEPENUHNYA GRATIS** — Boleh dipakai, dimodifikasi, dan dibagikan oleh siapa saja.
> 🚫 **DILARANG DIPERJUALBELIKAN** — Kode ini tidak boleh dijual dalam bentuk apapun.
> Lihat [`LICENSE`](./LICENSE) untuk ketentuan lengkap.

---

# 🎭 Dalang-AI

**Multi-Agent Autonomous Studio — dengan filosofi Wayang Nusantara**

[![Tests](https://img.shields.io/badge/tests-182%20passed-22c55e?style=flat-square&logo=pytest)](./)
[![Python](https://img.shields.io/badge/python-3.11%2B-3b82f6?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%20+%20Three.js-61dafb?style=flat-square&logo=react)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-CIS%20Hardened-2496ed?style=flat-square&logo=docker)](./workspace/Dockerfile)
[![Security](https://img.shields.io/badge/Security%20Audit-Grade%20B%2B-f59e0b?style=flat-square&logo=owasp)](./workspace/SECURITY_AUDIT.md)
[![Anti-Slop](https://img.shields.io/badge/Anti--AI--Slop-enforced-ef4444?style=flat-square)](https://github.com/miqdadbadjuber/anti-slop)
[![License](https://img.shields.io/badge/License-Non--Commercial%20(Gratis)-red?style=flat-square)](./LICENSE)

<br/>

> *Dalam pewayangan, Dalang adalah sutradara dan jiwa dari sebuah lakon.*
> *Setiap wayang bergerak sesuai kehendaknya — namun semuanya dihidupkan oleh satu tangan.*
>
> **Di sini, kamu adalah Sang Dalang. Para Wayang AI menjalankan tugasnya sendiri.**

<br/>

```
╔══════════════════════════════════════════════════════╗
║           K A M U   S A N G   D A L A N G           ║
║                                                      ║
║   Pegang  ROADMAP.md  →  Risko mengatur segalanya   ║
║   Wayang bekerja paralel, melapor secara real-time   ║
║   Dashboard 3D isometrik memvisualisasikan lakon     ║
╚══════════════════════════════════════════════════════╝
```

</div>

---

## Apa itu Dalang-AI?

Dalang-AI adalah platform **orkestrasi multi-agent** yang bekerja seperti sebuah tim pegawai otonom. Kamu cukup menulis `ROADMAP.md` berisi daftar tugas — Risko (Sang Dalang) akan membagi-bagikan pekerjaan ke 8 sub-agent spesialis, menjalankannya secara paralel, dan melaporkan hasilnya secara real-time di dashboard 3D.

**Tidak ada intervensi manual. Tidak ada prompt berulang. Lakon berjalan sendiri.**

---

## Arsitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                      DALANG-AI STUDIO                           │
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │            KELIR  (3D Isometric Dashboard)               │  │
│   │     React + Three.js · SSE real-time · WebSocket         │  │
│   └─────────────────────────┬────────────────────────────────┘  │
│                             │ Events                            │
│   ┌─────────────────────────▼────────────────────────────────┐  │
│   │              GAMELAN  (FastAPI Backend)                   │  │
│   │      /orchestrate · /agents/status · /events/log         │  │
│   └─────────────────────────┬────────────────────────────────┘  │
│                             │                                   │
│   ┌─────────────────────────▼────────────────────────────────┐  │
│   │                RISKO  (Sang Dalang)                       │  │
│   │        Membaca ROADMAP.md · Mendelegasikan task           │  │
│   │        Graphify context scoping · Asyncio dispatch        │  │
│   └──┬─────────┬────────┬────────┬────────┬────────┬─────────┘  │
│      │         │        │        │        │        │            │
│   ┌──▼──┐  ┌───▼──┐ ┌───▼──┐ ┌──▼───┐ ┌──▼──┐ ┌──▼───┐       │
│   │PING │  │ ZAKI │ │ LULU │ │ MIKA │ │ NOVA│ │ KAI  │ [REN] │
│   │Data │  │Back  │ │Front │ │ Docs │ │DevOp│ │ Sec  │  QA   │
│   └─────┘  └──────┘ └──────┘ └──────┘ └─────┘ └──────┘       │
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                  ROADMAP.md                              │  │
│   │           Single Source of Truth — YAML                  │  │
│   └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Roster Para Wayang

| Tokoh | Nama | Peran | Standar |
|:---:|---|---|---|
| 🟣 | **Risko** — Sang Dalang | Master Orchestrator & Project Lead | ROADMAP-driven, Graphify scoping |
| 🟢 | **Pingot** — Wayang Data | Data Engineer & DDD Architect | DDD, Data Contracts, ISO 8601 UTC |
| 🟡 | **Zaki** — Wayang Backend | Backend & API Developer | SOLID, Clean Arch, 12-Factor, REST L3 |
| 🩷 | **Lulu** — Wayang Visual | Frontend & UX Engineer | WCAG 2.1 AA, Core Web Vitals, Anti-Slop UI |
| 🩵 | **Mika** — Wayang Pujangga | Technical Writer | Diátaxis, Google Dev Style, OpenAPI 3.1 |
| 🟠 | **Nova** — Wayang Patih | DevOps & Infrastructure | CIS Docker Benchmark, Google SRE, DORA |
| 🔴 | **Kai** — Wayang Senopati | Security Auditor | OWASP ASVS v4.0 L2, NIST SP 800-63B, CVSS v3.1 |
| 🔵 | **Ren** — Wayang Jaksa | QA & E2E Automation | ISTQB, Test Pyramid, AAA Pattern, BVA |

Setiap wayang memiliki **knowledge base standar internasional** yang diinjeksikan langsung ke system prompt sebelum runtime. Mereka bukan sekedar AI generik — mereka spesialis.

---

## Cara Kerja

```
1. Buat Proyek (Cukup Satu Kalimat!)
   └─ ./dalang.py init "Nama Proyek" "Deskripsi apa yang ingin dibangun"
   └─ Risko memecah tugas, memilih Wayang yang tepat, sisanya DIAM (idle)

2. Jalankan Lakon
   └─ ./dalang.py run   (atau via Dashboard 3D: http://localhost:5173)
   └─ Wayang bekerja paralel, saling menunggu dependensi secara tertib

3. Ajari Skill Baru Kapan Saja
   └─ ./dalang.py teach <wayang> "Gunakan Tailwind CSS v3 / SQLAlchemy 2.0"
   └─ Wayang langsung pintar dan menerapkan skill itu di proyek berikutnya!

4. Selesai
   └─ Kode, UI, dokumen, dan pengujian otomatis tersimpan di workspace/
```

---

## Quickstart

### Prasyarat
- Python 3.11+
- Node.js 20+
- LLM endpoint (OpenAI-compatible API)

### 1. Clone & Setup

```bash
git clone https://github.com/khoirulanamid/dalang-ai.git
cd dalang-ai

python3 -m venv .venv
source .venv/bin/activate
pip install -r workspace/requirements.txt
```

### 2. Konfigurasi `.env`

```bash
cp workspace/.env.example workspace/.env
```

Edit `workspace/.env`:

```env
OPENAI_BASE_URL=http://your-llm-endpoint/v1
OPENAI_API_KEY=your-api-key
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(64))")
```

### 3. Jalankan Backend & Dashboard

```bash
# Terminal 1 — Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8765

# Terminal 2 — Dashboard 3D
cd frontend && npm install && npm run dev
```

Dashboard: **http://localhost:5173**

### 4. Mulai Proyek Pertamamu

```bash
# Cukup deskripsikan proyekmu — Risko yang urus sisanya
./dalang.py init "Aplikasi Todo" "Aplikasi todo list web dengan tampilan bersih, bisa tambah, edit, hapus tugas, dan ada unit test"

# Lihat apa yang Risko rencanakan
./dalang.py status

# Mulai lakon!
./dalang.py run
```

---

## Perintah CLI Dalang-AI

```bash
./dalang.py init "Proyek" "Deskripsi"   # Buat proyek baru (Risko auto-plan)
./dalang.py run [--cycles N]            # Mulai lakon orkestrasi
./dalang.py status                      # Lihat progress ROADMAP
./dalang.py roster                      # Lihat semua Wayang & keahlian
./dalang.py teach <wayang> "skill"      # Ajarkan skill baru ke Wayang
./dalang.py skills [--wayang <id>]      # Lihat ringkasan keahlian Wayang
```

### Contoh Perintah `teach`

```bash
# Ajari Lulu pakai Tailwind CSS
./dalang.py teach lulu "Gunakan Tailwind CSS v3. Hindari inline CSS. Pakai lucide-icons."

# Ajari Zaki pakai SQLAlchemy async
./dalang.py teach zaki "Gunakan SQLAlchemy 2.0 async ORM. Pisahkan session factory dari business logic."

# Ajari Nova deploy ke Railway
./dalang.py teach nova "Target deployment: Railway.app. Sertakan railway.json di setiap proyek."

# Lihat apa yang sudah dipelajari Lulu
./dalang.py skills --wayang lulu
```

---

## Format ROADMAP.md

```yaml
project: "Nama Project Kamu"
version: "1.0.0"

tasks:
  - id: T-001
    title: "Buat REST API endpoint untuk user management"
    agent: zaki
    priority: high
    done: false

  - id: T-002
    title: "Desain halaman dashboard dengan aksesibilitas WCAG"
    agent: lulu
    depends_on: [T-001]
    done: false

  - id: T-003
    title: "Tulis dokumentasi teknis QUICKSTART"
    agent: mika
    done: false
```

---

## Standar Internasional

Setiap agent **diwajibkan** memenuhi standar kelas dunia:

| Domain | Standar |
|---|---|
| Security | OWASP ASVS v4.0 L2, NIST SP 800-63B, CVSS v3.1 |
| Frontend | WCAG 2.1 AA, Core Web Vitals, Nielsen Heuristics |
| Backend | SOLID, Clean Architecture, 12-Factor App, REST L3 |
| Data | Domain-Driven Design, Data Contracts, ISO 8601 UTC |
| DevOps | CIS Docker Benchmark, Google SRE, DORA Metrics |
| Docs | Diátaxis Framework, Google Developer Style Guide |
| QA | ISTQB, Test Pyramid, AAA Pattern, Boundary Value Analysis |

---

## Anti-AI-Slop 🚫

Dalang-AI menerapkan filter [anti-slop](https://github.com/miqdadbadjuber/anti-slop) untuk memastikan output bebas dari:

- ❌ Gradient buta & glassmorphism dekoratif (UI)
- ❌ AI buzzwords: *"seamlessly", "elevate", "leverage"* (Copywriting)
- ❌ Comment banner dekoratif `# ===` / `// ---` (Kode)
- ❌ Filler phrase generic tanpa makna konkret

Output Dalang-AI adalah output yang **jujur, padat, dan bisa langsung digunakan.**

---

## Stack Teknologi

| Layer | Teknologi |
|---|---|
| Orchestration | Python 3.11, asyncio, httpx (SSE streaming) |
| Backend API | FastAPI, Uvicorn, Pydantic v2 |
| Frontend | React 18, Three.js, Vite |
| Auth | JWT (python-jose), bcrypt |
| Testing | pytest, httpx (182 tests, 100% pass) |
| CI/CD | GitHub Actions (5 stages) |
| Container | Docker, Docker Compose, nginx |
| LLM | OpenAI-compatible endpoint (lokal atau cloud) |

---

## Test Suite

```
test_wayang_router.py     # 9 tests  — Risko auto-routing & wayang idle
test_project_planner.py   # 9 tests  — Auto-decomposition dari deskripsi bebas
test_wayang_academy.py    # 9 tests  — Perguruan wayang & skill upgrade
workspace/
├── test_token.py         # 33 tests — JWT & token service
├── test_auth_api.py      # 33 tests — REST endpoints
├── test_security.py      # 13 tests — OWASP ASVS regression
├── test_e2e_flow.py      # 64 tests — Full lifecycle E2E scenarios
└── test_bva_standards.py # 12 tests — Boundary Value Analysis

Total: 182 / 182 tests passed ✅ (0 failures)
```

---

## Struktur Proyek

```
dalang-ai/
├── dalang.py                   # 🎭 CLI utama Sang Dalang
├── wayang_router.py            # Modul auto-routing & deteksi wayang idle
├── project_planner.py          # Modul perencana proyek (auto-decompose)
├── wayang_academy.py           # Perguruan wayang (teach & upgrade skill)
├── ROADMAP.md                  # Naskah lakon (single source of truth)
├── risko_orchestrator.py       # Engine orkestrator Risko
├── real_subagent_runner.py     # Sub-agent runner & LLM client
├── agent_tools.py              # Tool belt tiap wayang
│
├── backend/                    # FastAPI server (Gamelan)
│   └── main.py
│
├── frontend/                   # 3D Isometric Dashboard (Kelir)
│   └── src/App.jsx             # Three.js + React
│
├── standards/                  # Buku pintar keahlian tiap wayang
│   ├── zaki_backend_standards.md
│   ├── lulu_frontend_standards.md
│   ├── kai_security_standards.md
│   └── ...
│
└── workspace/                  # Output hasil kerja para wayang
    ├── auth_api.py
    ├── token_service.py
    ├── docs/
    ├── .github/workflows/ci.yml
    └── test_*.py
```

---

## Security Audit

Kai (Wayang Senopati) telah melakukan audit menyeluruh berdasarkan **OWASP ASVS v4.0 Level 2**:

- ✅ JWT verification — algoritma explicit, reject `alg:none`
- ✅ Password hashing — bcrypt dengan cost factor optimal
- ✅ Bind host — dikonfigurasi via environment variable
- ✅ Secret key — reject default secret di production
- ✅ CORS — explicit origin whitelist
- 📄 Laporan lengkap: [`workspace/SECURITY_AUDIT.md`](./workspace/SECURITY_AUDIT.md)

**Security Grade: B+**

---

## Kontribusi

Pull request terbuka untuk siapa saja. Sebelum membuka PR, pastikan:

1. Tambahkan task baru di `ROADMAP.md`
2. Jalankan `python3 run_sprint.py` — biarkan wayang yang mengerjakan
3. Pastikan semua 182 tests masih passing: `pytest test_*.py workspace/test_*.py -q`
4. Tidak ada AI slop di output kamu

---

## Lisensi

**Non-Commercial Public License** — Bebas digunakan dan dibagikan, **DILARANG DIPERJUALBELIKAN.**

| Tindakan | Status |
|---|:---:|
| Pakai untuk proyek pribadi | ✅ Boleh |
| Modifikasi kode | ✅ Boleh |
| Bagikan ke orang lain (gratis) | ✅ Boleh |
| Dipakai untuk riset / edukasi | ✅ Boleh |
| Fork dan kembangkan sendiri | ✅ Boleh |
| Dijual / dikomersialisasikan | 🚫 **TIDAK BOLEH** |
| Dijual ulang dengan nama lain | 🚫 **TIDAK BOLEH** |
| Dikemas sebagai SaaS berbayar | 🚫 **TIDAK BOLEH** |

Lihat [`LICENSE`](./LICENSE) untuk teks hukum lengkap.

---

<div align="center">

**Dibuat dengan filosofi Wayang Nusantara 🎭**

*Kamu Sang Dalang. Mereka para Wayang. Lakon berjalan sendiri.*

---

[⭐ Star repo ini](https://github.com/khoirulanamid/dalang-ai) · [🐛 Laporkan bug](https://github.com/khoirulanamid/dalang-ai/issues) · [💡 Request fitur](https://github.com/khoirulanamid/dalang-ai/discussions)

</div>
