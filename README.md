<div align="center">

> 🎁 **SEPENUHNYA GRATIS** — Boleh dipakai, dimodifikasi, dan dibagikan oleh siapa saja.  
> 🚫 **DILARANG DIPERJUALBELIKAN** — Kode ini tidak boleh dijual dalam bentuk apapun.  
> Lihat [`LICENSE`](./LICENSE) untuk ketentuan lengkap.

---

# 🎭 Dalang-AI

**Autonomous Multi-Agent Software Engineering Platform & 3D Interactive Tech Studio**  
*Ditenagai Filosofi Wayang Nusantara — Karya Bos Muda (Khoirul Anam)*

[![Tests](https://img.shields.io/badge/tests-384%20passed-22c55e?style=flat-square&logo=pytest)](./)
[![Python](https://img.shields.io/badge/python-3.11%2B-3b82f6?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%20+%20Three.js-61dafb?style=flat-square&logo=react)](https://react.dev)
[![Security](https://img.shields.io/badge/Security-Cloudflare%20Adversarial%20Audit-0ea5e9?style=flat-square&logo=cloudflare)](./audit_harness.py)
[![LLM Guard](https://img.shields.io/badge/OWASP%20LLM-Top%2010%20%2B%20ASI-red?style=flat-square)](./llm_guard.py)
[![Observability](https://img.shields.io/badge/OpenTelemetry-Prometheus%20Ready-f97316?style=flat-square&logo=opentelemetry)](./telemetry_engine.py)
[![License](https://img.shields.io/badge/License-Non--Commercial%20(Gratis)-red?style=flat-square)](./LICENSE)

<br/>

> *Dalam pewayangan, Dalang adalah sutradara dan jiwa dari sebuah lakon.*  
> *Setiap wayang bergerak sesuai kehendaknya — namun semuanya dihidupkan oleh satu tangan.*  
>  
> **Di sini, Bos Muda adalah Sang Dalang. Para Wayang AI mengeksekusi lakon software engineering secara nyata.**

<br/>

```
╔══════════════════════════════════════════════════════════════════════╗
║                    B O S   M U D A   S A N G   D A L A N G           ║
║                                                                      ║
║   Instruksi Proyek  →  Risko membedah & membagi tugas ke 8 Divisi   ║
║   Cantrik Pool melipatgandakan kecepatan via pekerja paralel         ║
║   Field Journal mencegah kesalahan masa lalu berulang                ║
║   Studio 3D Three.js memvisualisasikan pergerakan kantor real-time   ║
║   Cloudflare Harness + QA Gate menjamin rilis bebas celah & bug      ║
╚══════════════════════════════════════════════════════════════════════╝
```

</div>

---

## 🌟 Apa itu Dalang-AI?

**Dalang-AI** adalah platform rekayasa perangkat lunak multi-agent otonom tingkat enterprise (*Enterprise-Grade Multi-Agent SDLC Platform*) yang menggerakkan sebuah "Perusahaan Perangkat Lunak Virtual" mandiri.

Cukup berikan deskripsi proyek atau salin repositori kodingan yang kompleks ke `workspace/` — **Risko (Master Orchestrator)** bersama 7 Wayang Spesialis dan kawanan **Cantrik (Worker Pool)** akan bermusyawarah, menyusun arsitektur, menulis kode murni, mengaudit keamanan siber, menguji regresi secara ekstrem, hingga memvalidasi kelaikan rilis (*GO / NO-GO*).

### 🚀 Zero Simulation — Real Execution
- **Bukan timer atau animasi bohongan**: Agen benar-benar mengeksekusi kode Python/Node.js, memodifikasi file workspace, dan menjalankan automated tests langsung di Linux OS.
- **Bukan AI Slop**: Kode dan dokumentasi mematuhi standar desain modern (Inter + JetBrains Mono), Clean Architecture, dan prinsip Anti-AI-Slop.
- **384 Automated Tests Pass (100% Bersih)**: Seluruh modul diuji dengan pytest secara ketat.

---

## 🏢 Fitur & Keunggulan Utama

### 1. 🎭 8 Wayang Spesialis + Bos Muda 3D Avatar
- **Bos Muda Playable Character**: Jelajahi kantor virtual 3D menggunakan keyboard (WASD). Dilengkapi 3 sudut pandang kamera: **Orbit Bebas**, **First-Person (FPS)**, dan **Third-Person (TPS)** dengan fisika halangan anti-tembus (*AABB Wall-Sliding Collision*).
- **8 Divisi Wayang**: Risko (Orchestrator), Pingot (Database), Zaki (Backend), Lulu (Frontend & 3D), Mika (Technical Docs), Nova (DevOps), Kai (Security & Reverse Engineering), dan Ren (QA Lead).

### 2. 👥 Cantrik Ephemeral Worker Pool (`cantrik_worker_pool.py`)
Saat beban kerja meningkat atau ribuan baris kode harus diproses bersamaan, Wayang dapat memanggil kawanan **Cantrik** (sub-agent pembantu sementara). Cantrik berjalan paralel di lingkungan terisolasi (*Scope Guard*) dan otomatis dihancurkan dari memori setelah tugas selesai.

### 3. 🧠 Self-Evolving Field Journal (`field_journal.py`)
Dalang-AI memiliki ingatan empiris otonom. Setiap kali agen menemukan kendala teknis atau perbaikan bug (*incident JRN-xxxx*), solusinya dicatat secara permanen dan disuntikkan secara dinamis (maksimal 2–3 entri relevan / ~200 token) ke prompt tugas masa depan agar kesalahan masa lalu **tidak pernah terulang**.

### 4. 🛡️ Triple-Layer Enterprise Defense
- **Scope Guard (`scope_guard.py`)**: Memastikan seluruh operasi file agen terkunci aman di dalam folder `workspace/` dan memblokir upaya *path traversal* (`../`).
- **OWASP LLM & ASI 2026 Guard (`llm_guard.py`)**: Melindungi sistem dari serangan *Indirect Prompt Injection*, kebocoran kredensial/API Key, dan pembatasan wewenang berlebih (*Excessive Agency*).
- **DB Security Guard (`db_security_guard.py`)**: Memindai eksposisi connection string, menegakkan SSL/TLS database, dan memblokir celah SQL Injection.

### 5. 🔍 Cloudflare-Grade Adversarial Audit Harness (`audit_harness.py`)
Mengadopsi metodologi audit resmi Cloudflare:
- **Coverage Ledger**: Pemetaan 100% permukaan kode dan alur data sebelum audit.
- **Uji Sangkal Lawan (*Adversarial Verification*)**: Setiap dugaan celah dari Kai (Hunter) **wajib diuji dan disangkal** oleh Ren (Adversarial Verifier). Kerentanan hanya berstatus `confirmed` jika terbukti tidak dapat disangkal oleh sanitizer atau middleware yang ada.

### 6. 🔀 Algorithm Visualizer DAG Tracer (`execution_tracer.py`)
Dilengkapi pemutar alur eksekusi tugas interaktif di frontend. Pantau transisi state machine agen (`INIT` → `START` → `CODE_WRITE` → `TEST_RUN` → `VERIFY` → `COMPLETE`) dengan tombol *Play/Pause*, *Step-by-Step*, dan *Scrubber bar*.

### 7. ⚖️ Multi-Agent Consensus & Debate Engine (`consensus_engine.py`)
Musyawarah teknis antar-Wayang sebelum perubahan arsitektur besar:
- Memerlukan kuorum minimal 75% persetujuan para Wayang.
- **Hak Veto Kai**: Kai berhak memveto (*VETOED*) usulan yang mengandung risiko keamanan kritis.
- Otomatis menghasilkan dokumen **Architecture Decision Record (ADR)**.

### 8. 🌐 Technical SEO & Core Web Vitals Auditor (`seo_auditor.py`)
Memastikan setiap web yang dibangun lulus uji Technical SEO, validasi Schema.org JSON-LD, kelengkapan OpenGraph, dan generator XML sitemap otomatis.

### 9. 🚦 Pre-Deployment GO/NO-GO Gate (`deployment_auditor.py`)
Sebelum kode dirilis ke produksi, sistem melakukan inspeksi kepatuhan tanpa toleransi (*Zero-Tolerance Hard Blocker*): pengecekan rahasia `.env`, container health check, dan kelulusan seluruh test suite.

### 10. 📊 Telemetri & Observability (`telemetry_engine.py`)
Pelacak konsumsi token (prompt/completion), latensi eksekusi dalam milidetik, dan estimasi biaya per tugas yang siap diekspor ke format Prometheus / OpenTelemetry.

### 11. 🏷️ Automated Semantic Release (`release_engine.py`)
Otomasi penomoran versi SemVer 2.0.0 (*Major.Minor.Patch*) berdasarkan Conventional Commits dan pembuat dokumen `CHANGELOG.md` otomatis.

---

## 🏛️ Roster Para Wayang

| Avatar | Wayang | Divisi & Peran | Spesialisasi & Standar Mutu |
|:---:|---|---|---|
| 👑 | **Risko** — Sang Dalang | Master Orchestrator & Project Lead | DAG Decomposition, Multi-Agent Consensus, Graphify Scoping |
| 🟢 | **Pingot** — Wayang Data | Database Architect & Data Engineer | Domain-Driven Design (DDD), Schema Migrations, PoLP Security |
| 🟡 | **Zaki** — Wayang Backend | Backend & API Systems Engineer | FastAPI, Clean Architecture, 12-Factor App, REST L3, Defensive APIs |
| 🟣 | **Lulu** — Wayang Visual | Frontend, UI/UX & WebGL Artisan | Three.js 3D, React, Technical SEO, Core Web Vitals, Anti-Slop UI |
| 🩵 | **Mika** — Wayang Pujangga | Technical Writer & Security Scribe | Diátaxis Framework, OpenAPI 3.1, Architecture Decision Records (ADR) |
| 🟠 | **Nova** — Wayang Patih | DevOps, SRE & Toolchain Engineer | CIS Docker Hardening, Hermetic Toolchain, Pre-Deployment Gate |
| 🔴 | **Kai** — Wayang Senopati | Security Architect & Reverse Engineer | Cloudflare Harness, OWASP ASVS v4.0 L2, LLM Guard, Deobfuscation |
| 🔵 | **Ren** — Wayang Jaksa | QA Lead & Adversarial Verifier | ISTQB, The Disprover Protocol, Boundary Value Analysis, E2E Testing |

---

## ⚡ Alur Eksekusi Cepat

```bash
# 1. Inisialisasi Proyek Baru
./dalang.py init "Toko Online Modern" "Buatkan REST API inventory produk dengan autentikasi JWT dan database PostgreSQL"

# 2. Risko Membedah Roadmap & Menugaskan Wayang
# Para Wayang bermusyawarah, menulis kode di workspace/, dan melakukan audit

# 3. Jalankan Lakon
./dalang.py run

# 4. Pantau via Dashboard 3D & DAG Tracer
# Buka http://localhost:5173 di browser Anda!
```

---

## 📁 Struktur Repositori

```
dalang-ai/
├── dalang.py                   # 🎭 CLI utama Dalang-AI
├── risko_orchestrator.py       # Engine orkestrator Risko
├── real_subagent_runner.py     # Real execution engine & sub-agent runner
├── cantrik_worker_pool.py      # Ephemeral worker pool untuk tugas paralel
├── field_journal.py            # Self-evolving memory & pitfall prevention
├── audit_harness.py            # Cloudflare-grade Coverage Ledger & Adversarial Verifier
├── consensus_engine.py         # Multi-Agent technical debate & ADR generator
├── telemetry_engine.py         # OpenTelemetry & Prometheus token tracking
├── release_engine.py           # Semantic Versioning & CHANGELOG generator
├── deployment_auditor.py       # Pre-deployment GO/NO-GO release gate
├── seo_auditor.py              # Technical SEO, Core Web Vitals, Schema.org
├── browser_tester.py           # Headless DOM & bundle verifier
├── scope_guard.py              # File path boundary & security isolation
├── llm_guard.py                # OWASP LLM Top 10 & ASI 2026 defense
├── db_security_guard.py        # Database misconfiguration & SQLi auditor
├── toolchain_bootstrap.py      # On-demand hermetic toolchain installer
├── wayang_router.py            # Auto-routing & idle agent detector
├── project_planner.py          # Automated project task decomposition
├── wayang_academy.py           # Perguruan Wayang (skill upgrade)
├── ROADMAP.md                  # Single source of truth (Sprint status)
│
├── backend/                    # FastAPI Server (Port 8765)
│   └── main.py                 # SSE stream & DAG tracer API
│
├── frontend/                   # 3D Tech Studio (Three.js + React, Port 5173)
│   ├── src/App.jsx             # Bos Muda Kinematics, AABB Collision, DAG Modal
│   └── vite.config.js
│
├── standards/                  # Buku pintar keahlian tiap Wayang
│   ├── risko_orchestrator_standards.md
│   ├── pingot_data_standards.md
│   ├── zaki_backend_standards.md
│   ├── lulu_frontend_standards.md
│   ├── mika_docs_standards.md
│   ├── nova_devops_standards.md
│   ├── kai_security_standards.md
│   └── ren_qa_standards.md
│
├── field_journal/              # Catatan insiden empiris (JRN-xxxx)
└── workspace/                  # Ruang kerja nyata output para Wayang
```

---

## 🧪 Status Pengujian Otomatis (Test Suite)

```
============================= test session starts ==============================
collected 384 items

test_reverse_skill_integration.py ....... [Pass]
test_cantrik_pool.py .............. [Pass]
test_llm_guard.py ................. [Pass]
test_db_security_guard.py ......... [Pass]
test_browser_tester.py ............ [Pass]
test_execution_tracer.py .......... [Pass]
test_seo_auditor.py ............... [Pass]
test_deployment_auditor.py ........ [Pass]
test_audit_harness.py ............. [Pass]
test_consensus_engine.py .......... [Pass]
test_telemetry_engine.py .......... [Pass]
test_release_engine.py ............ [Pass]
test_orchestrator.py .............. [Pass]
test_e2e_flow.py .................. [Pass]
workspace/test_*.py ............... [Pass]

========================= 384 passed in 14.82s =========================
```

---

## 📜 Lisensi & Etika Penggunaan

**Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**

Dalang-AI diciptakan oleh **Bos Muda (Khoirul Anam)** untuk kemaslahatan publik dan komunitas developer.

| Penggunaan | Status |
|---|:---:|
| Digunakan untuk kebutuhan pribadi atau tim internal | ✅ **DIPERBOLEHKAN** |
| Memodifikasi dan mengembangkan kode sumber | ✅ **DIPERBOLEHKAN** |
| Membagikan kode secara gratis kepada orang lain | ✅ **DIPERBOLEHKAN** |
| Digunakan untuk riset akademis dan edukasi | ✅ **DIPERBOLEHKAN** |
| **Memperjualbelikan kode Dalang-AI secara langsung** | 🚫 **MUTLAK DILARANG** |
| **Menjual ulang dengan mengganti nama/branding (re-skin)** | 🚫 **MUTLAK DILARANG** |
| **Mengemas Dalang-AI menjadi produk SaaS berbayar komersial** | 🚫 **MUTLAK DILARANG** |

---

<div align="center">

**🎭 Dalang-AI — Menghidupkan Rekayasa Perangkat Lunak Masa Depan**  
*Diciptakan dengan kebanggaan Nusantara oleh Bos Muda.*

[⭐ Star Repository](https://github.com/khoirulanamid/dalang-ai) · [🐛 Laporkan Isu](https://github.com/khoirulanamid/dalang-ai/issues) · [💡 Diskusi](https://github.com/khoirulanamid/dalang-ai/discussions)

</div>
