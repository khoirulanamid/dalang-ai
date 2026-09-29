# Changelog

All notable changes to **Dalang-AI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.5.0] - 2026-09-29

### Added
- **Multi-Agent Consensus & Debate Engine (`consensus_engine.py`)**: Peer review protocol requiring a 75% quorum and granting Kai (Security Lead) absolute veto power over security-critical proposals. Generates structured Architecture Decision Records (ADRs).
- **Telemetry & Token Observability Engine (`telemetry_engine.py`)**: Tracks prompt/completion tokens, latency per agent, execution costs, and exports metrics in Prometheus / OpenTelemetry exposition format.
- **Automated Semantic Release Engine (`release_engine.py`)**: Computes SemVer version bumps from Conventional Commits and automatically updates `CHANGELOG.md`.
- **Cloudflare Adversarial Audit Harness (`audit_harness.py`)**: 6-phase vulnerability verification featuring Coverage Ledger mapping and "The Disprover Protocol" (Ren rigorously attempts to refute Kai's vulnerability candidates to eliminate false positives).
- **Pre-Deployment GO/NO-GO Auditor (`deployment_auditor.py`)**: Zero-tolerance release gate inspecting secret leakage, container hardening, and test pass gates.
- **Technical SEO & Core Web Vitals Auditor (`seo_auditor.py`)**: Automated verification for HTML metadata, OpenGraph tags, JSON-LD Schema.org structure, and XML sitemaps.
- **Algorithm Visualizer Flow Tracer (`execution_tracer.py`)**: DAG execution recorder with interactive step-by-step playback scrubber modal in the 3D studio.
- **Cantrik Ephemeral Worker Pool (`cantrik_worker_pool.py`)**: Dynamic sub-agent spawning for high-throughput parallel task execution with automatic memory containment.
- **Triple-Layer Enterprise Defense**:
  - `scope_guard.py`: Filesystem boundary sandbox preventing directory traversal.
  - `llm_guard.py`: Sanitization for OWASP LLM Top 10, indirect prompt injection, and credential leak masking.
  - `db_security_guard.py`: Detection for database misconfigurations, connection string exposure, and multiline SQL injection.
  - `browser_tester.py`: Headless DOM verification and client-side XSS detection.
- **Self-Evolving Field Journal (`field_journal.py`)**: Empirical incident memory recording issues (`JRN-xxxx`) and injecting dynamic pitfall guardrails into agent prompts.
- **Bos Muda Playable 3D Character**: WASD navigation inside the 3D Tech Studio, 3 camera perspectives (Orbit, FPS, TPS), and AABB obstacle collision physics.

### Changed
- Total automated unit test suite expanded to **384 tests passed (100% clean, 0 failures)**.
- Enhanced `real_subagent_runner.py` with dynamic Field Journal pitfall injection and Cantrik toolbox integration.
- Upgraded agent standards (`standards/*.md`) with international specifications (Cloudflare, OWASP LLM 2026, Technical SEO, CIS Docker).

---

## [1.0.0] - 2026-09-25

### Added
- Initial core release of Dalang-AI with 8 Wayang agents (Risko, Pingot, Zaki, Lulu, Mika, Nova, Kai, Ren).
- 3D Isometric Office Studio built with React, Vite, and Three.js.
- FastAPI backend server with SSE event streaming.
- Real sub-agent execution runner with zero mock timers.
- Initial Sprint 1 through 8 implementations (Auth API, Dockerization, OWASP ASVS audit, and E2E testing).
