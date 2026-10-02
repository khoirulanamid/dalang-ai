---
project: Dalang-AI Multi-Agent Automation
version: 1.0.0
last_updated: 2026-09-25T15:30:00Z
orchestrator: Risko (Sang Dalang)
agents:
  - id: risko
    role: Sang Dalang (Master Orchestrator / Technical Lead)
    responsibilities: Task distribution, status reconciliation, ROADMAP execution
  - id: pingot
    role: Wayang Data (Research & Schema Architect)
    responsibilities: Data models, schemas, parsers, domain invariants
  - id: zaki
    role: Wayang Backend (Systems & Logic Engineer)
    responsibilities: API endpoints, business logic, authentication, testing
  - id: lulu
    role: Wayang Visual (Frontend & UX Artisan)
    responsibilities: Web UI, components, accessibility, anti-slop visual design
  - id: mika
    role: Wayang Pujangga (Technical Writer & Documentation)
    responsibilities: API docs, README, architecture guides, code examples
  - id: nova
    role: Wayang Patih (SRE & Infrastructure Specialist)
    responsibilities: Dockerfile, docker-compose, CI/CD, deployment scripts
  - id: kai
    role: Wayang Senopati (Security Architect & Auditor)
    responsibilities: Vulnerability assessment, OWASP audit, security tests, hardening
  - id: ren
    role: Wayang Jaksa (QA Automation & Test Architect)
    responsibilities: End-to-end integration tests, full lifecycle journeys, regression testing
---

# 🎭 Dalang-AI Master Roadmap

## SPRINT 1: User & Token Generator Module ✅
> Goal: Pingot defines data models, Zaki implements JWT token service.

- [x] **T-101**: [Pingot] Create user schema and password hashing utility
  - *Assigned*: pingot
  - *Dependencies*: none
  - *Status*: completed
  - *Artifacts*: `auth_models.py`

- [x] **T-102**: [Zaki] Implement JWT token generator and verify with pytest
  - *Assigned*: zaki
  - *Dependencies*: T-101
  - *Status*: completed
  - *Artifacts*: `token_service.py`, `test_token.py`

---

## SPRINT 2: Documentation ✅
> Goal: Mika membaca kode Sprint 1 lalu menulis dokumentasi lengkap.

- [x] **T-201**: [Mika] Write full API & developer documentation for Sprint 1 modules
  - *Assigned*: mika
  - *Dependencies*: T-101, T-102
  - *Status*: completed
  - *Artifacts*: `README.md`, `docs/auth_models.md`, `docs/token_service.md`

---

## SPRINT 3: Authentication REST API & Integration Tests ✅
> Goal: Zaki builds FastAPI auth router and server using Sprint 1 modules, plus comprehensive test suite.

- [x] **T-301**: [Zaki] Build FastAPI authentication server with /register, /login, /refresh, and /me endpoints
  - *Assigned*: zaki
  - *Dependencies*: T-101, T-102
  - *Status*: completed
  - *Artifacts*: `auth_api.py`, `test_auth_api.py`

---

## SPRINT 4: Frontend Login UI ✅
> Goal: Lulu builds a complete login/register web UI that connects to Zaki's Sprint 3 API.

- [x] **T-401**: [Lulu] Build a single-page HTML/CSS/JS login & register app connecting to the auth API
  - *Assigned*: lulu
  - *Dependencies*: T-301
  - *Status*: completed
  - *Artifacts*: `frontend_auth/index.html`, `frontend_auth/app.js`, `frontend_auth/style.css`

---

## SPRINT 5: DevOps & Containerization ✅
> Goal: Nova creates production-ready Dockerfile, docker-compose, and deployment configs for the full stack.

- [x] **T-501**: [Nova] Create Dockerfile, docker-compose.yml, and environment template for backend + frontend
  - *Assigned*: nova
  - *Dependencies*: T-301, T-401
  - *Status*: completed
  - *Artifacts*: `Dockerfile`, `docker-compose.yml`, `.env.example`, `.dockerignore`

---

## SPRINT 6: Security Audit & Hardening
> Goal: Kai performs full OWASP security audit of all Sprint 1-3 code, produces report with CVSS scores and regression tests.

- [x] **T-601**: [Kai] Security audit of auth_models.py, token_service.py, auth_api.py — produce SECURITY_AUDIT.md and test_security.py
  - *Assigned*: kai
  - *Dependencies*: T-101, T-102, T-301
  - *Status*: completed
  - *Artifacts*: `SECURITY_AUDIT.md`, `test_security.py`

---

## SPRINT 7: Remediation + CI/CD + E2E Tests ✅
> Goal: Zaki fixes security findings from Kai, Nova adds GitHub Actions CI/CD, Ren writes full E2E integration tests.

- [x] **T-701**: [Zaki] Security remediation — fix F-001 (bind host via HOST env var) and F-002 (enforce strong JWT secret, reject default)
  - *Assigned*: zaki
  - *Dependencies*: T-601
  - *Status*: completed

- [x] **T-702**: [Nova] CI/CD pipeline — create `.github/workflows/ci.yml` (lint, pytest, bandit, docker build)
  - *Assigned*: nova
  - *Dependencies*: T-501
  - *Status*: completed

- [x] **T-703**: [Ren] End-to-end integration tests — `test_e2e_flow.py` covering full user lifecycle
  - *Assigned*: ren
  - *Dependencies*: T-301, T-401
  - *Status*: completed

---

## SPRINT 8: International Standards Certification & Uplift ✅
> Goal: Ujian sertifikasi standar internasional untuk seluruh 7 sub-agent. Setiap agent meng-upgrade komponen sistem sesuai standard internasional role-nya.

- [x] **T-801**: [Pingot] Data Contract & DDD — Enforce ISO 8601 UTC timestamps, UserInDB vs UserPublic DTO projection, strict domain invariants
  - *Assigned*: pingot
  - *Dependencies*: T-701
  - *Status*: completed

- [x] **T-802**: [Zaki] Clean Architecture & SOLID — Decouple route handlers from service layer, implement UserRepository abstraction
  - *Assigned*: zaki
  - *Dependencies*: T-701, T-801
  - *Status*: completed

- [x] **T-803**: [Lulu] WCAG 2.1 AA Accessibility Uplift — Audit & fix frontend_auth for color contrast, keyboard tab order, aria-live alerts
  - *Assigned*: lulu
  - *Dependencies*: T-401
  - *Status*: completed

- [x] **T-804**: [Mika] Diátaxis Documentation Architecture — Write docs/ARCHITECTURE.md (Explanation) and docs/QUICKSTART.md (Tutorial) per Google Doc Style
  - *Assigned*: mika
  - *Dependencies*: T-201, T-702
  - *Status*: completed

- [x] **T-805**: [Nova] CIS Docker Hardening — Audit Dockerfile/compose against CIS benchmarks, drop Linux capabilities, enforce non-root verification
  - *Assigned*: nova
  - *Dependencies*: T-702
  - *Status*: completed

- [x] **T-806**: [Kai] OWASP ASVS v4.0 Level 2 Verification — Audit against ASVS V2/V3/V6, produce ASVS compliance matrix in SECURITY_AUDIT.md
  - *Assigned*: kai
  - *Dependencies*: T-601, T-701
  - *Status*: completed

- [x] **T-807**: [Ren] Boundary Value Analysis & AAA Test Suite — Write test_bva_standards.py enforcing AAA pattern strictly on all field boundaries
  - *Assigned*: ren
  - *Dependencies*: T-703
  - *Status*: completed

---

## SPRINT 9: Reverse-Skill Engine & Self-Evolving Memory ✅
> Goal: Mengadopsi arsitektur reverse-skill tingkat lanjut untuk memori empiris mandiri, toolchain hermetis, dan penjaga batas operasi.

- [x] **T-901**: [Risko] Field Journal & Self-Evolving Memory Engine (`field_journal.py`) — Mencatat insiden teknis (JRN-xxxx) dan menginjeksi pitfall relevan ke sub-agent prompt.
- [x] **T-902**: [Kai] Scope Guard Boundary Enforcer (`scope_guard.py`) — Mengisolasi akses file agen ke workspace dan memblokir traversal/escape.
- [x] **T-903**: [Ren] Zero-Hallucination Evidence Tracker (`evidence_tracker.py`) — Rantai bukti verifikasi temuan keamanan berbasis CVSS v3.1.
- [x] **T-904**: [Mika] Executive Security Reporter (`security_reporter.py`) — Generator laporan audit Diátaxis dengan status kesehatan sistem.
- [x] **T-905**: [Nova] On-Demand Toolchain Bootstrapper (`toolchain_bootstrap.py`) — Audit ketersediaan binary tool developer secara hermetis.

---

## SPRINT 10: Cantrik Worker Pool & Advanced Guardrails ✅
> Goal: Skalabilitas pekerja paralel sementara (*Cantrik*) dan pertahanan multi-vektor OWASP LLM serta database.

- [x] **T-1001**: [Risko] Cantrik Ephemeral Worker Pool (`cantrik_worker_pool.py`) — Sub-agent asisten sementara untuk offloading tugas batch paralel.
- [x] **T-1002**: [Kai] OWASP LLM Top 10 & ASI 2026 Guard (`llm_guard.py`) — Sanitasi prompt injection, masking rahasia kredensial, dan filter wewenang berlebih.
- [x] **T-1003**: [Pingot] Database Security & Misconfiguration Guard (`db_security_guard.py`) — Audit connection string, penegakan TLS, dan pencegahan SQLi multiline.
- [x] **T-1004**: [Ren] Headless DOM & Web Verifier (`browser_tester.py`) — Verifikasi struktur DOM dan deteksi celah XSS bundle frontend.

---

## SPRINT 11: Enterprise Production & Observability Suite ✅
> Goal: Standar produksi Cloudflare, visualisasi alur eksekusi DAG, Technical SEO, konsensus teknis, dan telemetri.

- [x] **T-1101**: [Risko & Lulu] Algorithm Visualizer Execution Flow DAG Tracer (`execution_tracer.py`) — Perekam transisi state machine agen dengan modal playback interaktif di 3D studio.
- [x] **T-1102**: [Lulu & Mika] Technical SEO & Core Web Vitals Auditor (`seo_auditor.py`) — Validator Schema.org JSON-LD, OpenGraph audit, dan sitemap generator.
- [x] **T-1103**: [Nova & Kai] Pre-Deployment GO/NO-GO Gate (`deployment_auditor.py`) — Inspeksi kesiapan rilis produksi berprinsip zero-tolerance blocker.
- [x] **T-1104**: [Kai & Ren] Cloudflare Adversarial Audit Harness (`audit_harness.py`) — Coverage Ledger dan Protokol Uji Sangkal Lawan (The Disprover Protocol).
- [x] **T-1105**: [Risko & Seluruh Wayang] Multi-Agent Consensus & Debate Engine (`consensus_engine.py`) — Musyawarah teknis, hak veto Kai, dan generator ADR otomatis.
- [x] **T-1106**: [Nova] Telemetry & Token Observability Engine (`telemetry_engine.py`) — Pemantau token prompt/completion, latensi, biaya, dan Prometheus exporter.
- [x] **T-1107**: [Nova & Mika] Semantic Release & Changelog Engine (`release_engine.py`) — Kalkulator SemVer 2.0.0 dan pembuat rilis CHANGELOG.md otomatis.


---

## SPRINT 12: Threads Affiliate Integration — Audit, Upgrade & Integrasi Penuh ✅
> Goal: Tim Dalang-AI mengaudit, menganalisis, memperkuat, dan mengintegrasikan proyek threads-affiliate ke dalam ekosistem kantor Bos Muda. Brownfield codebase di workspace/threads-affiliate/.

- [x] **T-1201** Audit arsitektur dan keamanan proyek threads-affiliate — pemetaan semua file, dependency, alur poster.py dan cookie_manager.py, deteksi potensi celah keamanan session cookie
  - *Dependencies*: none

- [x] **T-1202** Review kode content_generator.py dan dedup.py — analisis kualitas hook templates Indonesian, similarity detection algorithm, dan rotation logic; rekomendasikan perbaikan
  - *Dependencies*: none

- [x] **T-1203** Tulis dokumentasi teknis lengkap threads-affiliate untuk tim Dalang-AI — architecture overview, data flow diagram teks, integration guide, dan cara Dalang-AI bisa dispatch posting task
  - *Dependencies*: T-1201

- [x] **T-1204** Buat comprehensive test suite untuk threads-affiliate — unit tests content_generator, dedup logic, database operations, dan CLI exit codes; target ≥15 tests
  - *Dependencies*: T-1201, T-1202

- [x] **T-1205** Upgrade hook templates — tambah 3 kategori baru (fashion, gadget, food) dengan 9 hook styles per kategori masing-masing 3 varian, sesuai konvensi bahasa Indonesia gen-Z casual
  - *Dependencies*: T-1202

- [x] **T-1206** Security hardening threads-affiliate — audit cookie storage path, validasi input affiliate link, tambah rate limiting guard, dan pastikan .gitignore sudah benar lindungi semua secret
  - *Dependencies*: T-1201

