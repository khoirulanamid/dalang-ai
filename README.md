<div align="center">

# 🎭 Dalang-AI

**Multi-Agent Autonomous Studio — dengan filosofi Wayang Nusantara**

[![Tests](https://img.shields.io/badge/tests-155%20passed-22c55e?style=flat-square&logo=pytest)](./workspace/)
[![Python](https://img.shields.io/badge/python-3.11%2B-3b82f6?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%20+%20Three.js-61dafb?style=flat-square&logo=react)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-CIS%20Hardened-2496ed?style=flat-square&logo=docker)](./workspace/Dockerfile)
[![Security](https://img.shields.io/badge/Security%20Audit-Grade%20B%2B-f59e0b?style=flat-square&logo=owasp)](./workspace/SECURITY_AUDIT.md)
[![Anti-Slop](https://img.shields.io/badge/Anti--AI--Slop-enforced-ef4444?style=flat-square)](https://github.com/miqdadbadjuber/anti-slop)
[![License](https://img.shields.io/badge/license-MIT-a855f7?style=flat-square)](./LICENSE)

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
1. Tulis ROADMAP.md
   └─ Tentukan tasks, dependencies, dan agent yang bertanggung jawab

2. Jalankan orkestrasi
   └─ POST /orchestrate/start → Risko mengambil alih

3. Lihat dashboard
   └─ Buka http://localhost:5173 → Wayang bergerak di Kelir 3D

4. Selesai
   └─ Semua artifact, kode, dan dokumen tersimpan di workspace/
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

# Backend
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

### 3. Jalankan Backend

```bash
cd dalang-ai
uvicorn backend.main:app --host 0.0.0.0 --port 8765 --reload
```

### 4. Jalankan Dashboard

```bash
cd frontend
npm install
npm run dev
```

Dashboard tersedia di: **http://localhost:5173**

### 5. Tulis Roadmap & Mulai Lakon

Edit `ROADMAP.md`, lalu:

```bash
python3 run_sprint.py
```

Atau via API:

```bash
curl -X POST http://localhost:8765/orchestrate/start?max_cycles=5
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
| Testing | pytest, httpx (155 tests, 100% pass) |
| CI/CD | GitHub Actions (5 stages) |
| Container | Docker, Docker Compose, nginx |
| LLM | OpenAI-compatible endpoint (lokal atau cloud) |

---

## Test Suite

```
workspace/
├── test_token.py          # 33 unit tests — JWT & token service
├── test_auth_api.py       # 33 integration tests — REST endpoints
├── test_security.py       # 13 regression tests — OWASP ASVS
├── test_e2e_flow.py       # 64 E2E scenarios — full auth flow
└── test_bva_standards.py  # 12 tests — Boundary Value Analysis

Total: 155 / 155 tests passed ✅
```

---

## Struktur Proyek

```
dalang-ai/
├── ROADMAP.md                  # Single source of truth
├── risko_orchestrator.py       # Sang Dalang — engine utama
├── real_subagent_runner.py     # Sub-agent runner & LLM client
├── agent_tools.py              # Tool belt tiap wayang
├── run_sprint.py               # CLI launcher
│
├── backend/                    # FastAPI API server
│   └── main.py
│
├── frontend/                   # 3D Isometric Dashboard
│   └── src/App.jsx             # Three.js + React
│
├── standards/                  # Knowledge base standar per agent
│   ├── zaki_backend_standards.md
│   ├── lulu_frontend_standards.md
│   ├── kai_security_standards.md
│   └── ...
│
└── workspace/                  # Output artifact para wayang
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
3. Pastikan semua 155 tests masih passing: `pytest workspace/test_*.py -q`
4. Tidak ada AI slop di output kamu

---

## Lisensi

MIT License — bebas digunakan, dimodifikasi, dan didistribusikan.

---

<div align="center">

**Dibuat dengan filosofi Wayang Nusantara 🎭**

*Kamu Sang Dalang. Mereka para Wayang. Lakon berjalan sendiri.*

---

[⭐ Star repo ini](https://github.com/khoirulanamid/dalang-ai) · [🐛 Laporkan bug](https://github.com/khoirulanamid/dalang-ai/issues) · [💡 Request fitur](https://github.com/khoirulanamid/dalang-ai/discussions)

</div>
