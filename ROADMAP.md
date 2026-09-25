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
