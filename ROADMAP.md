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

---

## SPRINT 13: Multi-Platform Social Affiliate Poster — Threads & Facebook ✅ (Formalisasi ke Dalang-AI)
> Goal: Formalisasi modul Threads Poster & Facebook Poster yang sudah ada ke dalam ekosistem Dalang-AI secara resmi. Tim Dalang-AI melakukan review, hardening, test suite, dokumentasi, dan deposit ke Bagong Vault. Konten posting wajib jujur: gaya kurasi/humor, dilarang klaim personal "saya/aku sudah coba".

- [x] **T-1301**: [zaki] Audit & review modul fb_poster/ yang sudah ada — pemetaan cookie flow, dismiss popup logic, submit via mouse coordinate, identifikasi edge case & potensi gagal (selector berubah, session expired, popup baru)
  - *Assigned*: zaki
  - *Dependencies*: none

- [x] **T-1302**: [ren] Buat comprehensive test suite untuk fb_poster/ dan threads-affiliate posting flow — unit test cookie loading, popup dismiss logic, URL validation, content integrity (tidak ada klaim personal palsu); target ≥20 tests
  - *Assigned*: ren
  - *Dependencies*: T-1301

- [x] **T-1303**: [mika] Tulis dokumentasi teknis fb_poster/ dan integrasi multi-platform — architecture overview, alur session cookie, cara menjalankan posting Threads & Facebook, panduan menambah platform baru
  - *Assigned*: mika
  - *Dependencies*: T-1301

- [x] **T-1304**: [kai] Security hardening fb_poster/ — audit cookie path permissions (~/.fb_poster/ chmod 700, session.json chmod 600), pastikan credentials tidak ter-log di stdout, validasi konten sebelum submit (no PII leakage, no fake claims)
  - *Assigned*: kai
  - *Dependencies*: T-1301

- [x] **T-1305**: [risko] Ajarkan seluruh tim Wayang standar Social Affiliate Automation via Wayang Academy — etika konten (jujur/no fake claims), keamanan cookie session, anti-spam rotation logic, dan pola posting multi-platform
  - *Assigned*: risko
  - *Dependencies*: T-1303

- [x] **T-1306**: [bagong] Deposit semua artefak Sprint 13 ke Bagong Vault — fb_poster/, post_final.py, template hooks_gadget.json yang sudah diperbaiki, dokumentasi teknis, dan test suite
  - *Assigned*: bagong
  - *Dependencies*: T-1302, T-1303, T-1304, T-1305

---

## SPRINT 14: Threads Market Intelligence & Affiliate Trend Discovery ✅
> Goal: Riset tren produk affiliate yang sedang ramai dibahas di Threads Indonesia. Tim Dalang-AI mengumpulkan data kata kunci, menganalisis kategori produk dengan engagement tinggi (Racun Shopee / Spill Link), memetakan harga konversi terbaik, dan menyimpan laporannya ke Bagong Vault.

- [x] **T-1401**: [pingot] Crawl & ekstrak postingan tren Threads Indonesia terkait kata kunci affiliate ('racun shopee', 'spill shopee', 'link di bio', 'worth it', 'shopee haul') menggunakan session cookie yang aman
  - *Assigned*: pingot
  - *Dependencies*: none

- [x] **T-1402**: [pingot] Analisis pola & klasterisasi produk trending — petakan kategori (fashion, skincare, home living/gadget mini), rentang harga manis (sweet spot Rp 20rb - Rp 150rb), dan volume engagement
  - *Assigned*: pingot
  - *Dependencies*: T-1401

- [x] **T-1403**: [mika] Susun laporan riset pasar eksekutif 'Threads Affiliate Trend Report' — rekomendasi top 5 produk potensial konversi tinggi untuk Bos Muda
  - *Assigned*: mika
  - *Dependencies*: T-1402

- [x] **T-1404**: [ren] Validasi data laporan tren — verifikasi bahwa rekomendasi produk tidak fiktif, realistis, etis, dan bebas klaim palsu
  - *Assigned*: ren
  - *Dependencies*: T-1403

- [x] **T-1405**: [bagong] Deposit laporan hasil riset tren pasar ke Bagong Vault kategori 'report'
  - *Assigned*: bagong
  - *Dependencies*: T-1404

---

## SPRINT 15: Campaign Otomasi Affiliate — OMG Oh My Glam Lip Cream Matte ✅
> Goal: Menjalankan kampanye konten affiliate multi-platform (Threads & Facebook) untuk produk 'Lip Cream Matte Oh My Glam (OMG)'. Copywriting wajib jujur, relatable/humor, kurasi objektif (spek matte, Vit E + Jojoba Oil, bumil/busui safe), dilarang klaim pemakaian personal. Divalidasi oleh Ren QA Gate dan dieksekusi oleh Zaki & Kai.

- [x] **T-1501**: [mika] Susun 3 variasi copywriting draf postingan Threads & Facebook untuk Lip Cream Matte OMG (tema humor relatable wanita/cowok bingung shade, kurasi spek objektif tanpa klaim pribadi 'saya/aku sudah pakai')
  - *Assigned*: mika
  - *Dependencies*: none

- [x] **T-1502**: [kai] Security audit & verifikasi affiliate URL Shopee (validasi HTTPS, domain resmi s.shopee.co.id, OWASP sanitization)
  - *Assigned*: kai
  - *Dependencies*: T-1501

- [x] **T-1503**: [ren] Quality Gate Review — periksa copywriting agar 100% bebas klaim personal palsu, natural, lucu/menarik, dan format thread terbagi (Post 1: hook, Post 2: link)
  - *Assigned*: ren
  - *Dependencies*: T-1502

- [x] **T-1504**: [zaki] Eksekusi deployment posting Threads (@rizki_mubarakid) & Facebook (Rizqi Mubarak) menggunakan modul poster Dalang-AI
  - *Assigned*: zaki
  - *Dependencies*: T-1503

- [x] **T-1505**: [bagong] Simpan artefak teks konten dan bukti status live postingan ke Bagong Vault & database affiliate links
  - *Assigned*: bagong
  - *Dependencies*: T-1504

---

## SPRINT 16: Visual Scraper & Media Pipeline — Celana Jeans Korea 🚀
> Goal: Mengembangkan kemampuan ekstraksi gambar produk Shopee dari tautan affiliate secara otomatis (Playwright Chromium scraping) dan mengintegrasikannya ke pipeline posting bergambar Threads & Facebook Dalang-AI.

- [x] **T-1601**: [pingot] Ekstrak dan download gambar produk resolusi tinggi dari tautan Shopee Celana Jeans Korea (https://s.shopee.co.id/4LJqTkz7w7) menggunakan Playwright headless
  - *Assigned*: pingot
  - *Dependencies*: none

- [x] **T-1602**: [kresna] Validasi & preprocessing aset gambar (inspeksi visual, konversi format JPG/PNG, penyesuaian rasio feed 1:1 / 4:5 tanpa distorsi)
  - *Assigned*: kresna
  - *Dependencies*: T-1601

- [x] **T-1603**: [mika] Susun copywriting jujur & humor relatable gaya Korea/fit pinggang karet vs kancing tanpa klaim pemakaian palsu
  - *Assigned*: mika
  - *Dependencies*: T-1602

- [x] **T-1604**: [kai] Verifikasi keamanan file gambar (cek mime-type, ukuran file, no executable payload) & sanitasi link Shopee
  - *Assigned*: kai
  - *Dependencies*: T-1603

- [x] **T-1605**: [ren] Quality Gate Review — uji integritas gambar + teks konten kurasi
  - *Assigned*: ren
  - *Dependencies*: T-1604

- [x] **T-1606**: [zaki] Eksekusi posting bergambar (image attachment) ke Threads & Facebook
  - *Assigned*: zaki
  - *Dependencies*: T-1605

- [x] **T-1607**: [bagong] Deposit aset visual dan artefak postingan ke Bagong Vault
  - *Assigned*: bagong
  - *Dependencies*: T-1606

---

## SPRINT 17: Kelahiran Wayang Gathot (Social Media & Growth Specialist) 🚀
> Goal: Mengukir dan meresmikan Wayang ke-12 'Gathot' (Wayang Wira Warta) ke dalam arsitektur Dalang-AI: Engineering Standards, Roster Auto-Routing, Sub-Agent Runner, Test Suite, dan uji perdana penyusunan naskah viral, riset hashtag/keyword FYP, serta omnichannel publishing.

- [x] **T-1701**: [mika] Susun standar rekayasa resmi `standards/gathot_social_standards.md` mencakup SOP copywriting viral, hook psychology, kurasi etis tanpa klaim palsu, riset keyword sosial SEO, dan manajemen posting
  - *Assigned*: mika
  - *Dependencies*: T-1715

- [x] **T-1702**: [pingot] Registrasikan Gathot ke `wayang_router.py` (WAYANG_ROSTER, keywords pencocokan task social media/viral/threads/hashtag) dan pemetaan di `wayang_academy.py`
  - *Assigned*: pingot
  - *Dependencies*: T-1701

- [x] **T-1703**: [zaki] Daftarkan profil sub-agent Gathot dan loading standards di `real_subagent_runner.py` serta ikon dan integrasi di `dalang.py`
  - *Assigned*: zaki
  - *Dependencies*: T-1702

- [x] **T-1704**: [ren] Buat dan eksekusi test suite komprehensif `test_gathot_agent.py` untuk memvalidasi auto-routing, standards loading, dan integritas 12 Wayang
  - *Assigned*: ren
  - *Dependencies*: T-1703

- [x] **T-1705**: [kai] Security audit & permission check untuk operasi media sosial dan sanitasi parameter postingan Gathot
  - *Assigned*: kai
  - *Dependencies*: T-1704

- [x] **T-1706**: [bagong] Arsipkan akta kelahiran dan spesifikasi Wayang Gathot ke Bagong Vault serta perbarui index sistem
  - *Assigned*: bagong
  - *Dependencies*: T-1705

---

## SPRINT 18: Kampanye Celana Jeans Korea — Posting Bergambar Facebook 📱
> Goal: Gathot menyusun naskah copywriting kurasi relatable (Cowok Praktis), Zaki mengeksekusi posting bergambar ke Facebook personal Rizqi Mubarak dengan foto produk celana jeans Korea yang sudah tersedia di workspace/product_images/. Ren QA Gate validasi naskah, Bagong arsipkan artefak.

- [x] **T-1801**: [gathot] Susun naskah copywriting Facebook untuk celana jeans Korea (sudut pandang Cowok Praktis — ga sesak duduk lama) beserta 3-5 hashtag relevan dan keyword sosial SEO
  - *Assigned*: gathot
  - *Dependencies*: none

- [x] **T-1802**: [ren] Quality Gate Review — validasi naskah bebas klaim palsu, natural, relatable humor, sesuai standar gathot_social_standards.md
  - *Assigned*: ren
  - *Dependencies*: T-1801

- [x] **T-1803**: [zaki] Eksekusi posting bergambar ke Facebook personal Rizqi Mubarak menggunakan foto celana_jeans_korea_1.jpg dari workspace/product_images/ beserta naskah T-1801
  - *Assigned*: zaki
  - *Dependencies*: T-1802

- [x] **T-1804**: [bagong] Deposit naskah dan bukti live posting ke Bagong Vault
  - *Assigned*: bagong
  - *Dependencies*: T-1803

---

## SPRINT 19: Eksekusi Final Facebook Posting Celana Jeans & Vision QA 🚀
> Goal: Orkestrator Risko menunjuk Wayang yang tepat untuk mengeksekusi script post_jeans_facebook.py yang sudah dibuat Zaki di Sprint 18, mengambil screenshot verifikasi feed live, memvalidasi tampilan postingan bergambar, dan mengarsipkan bukti sah ke Bagong Vault.

- [x] **T-1901**: [auto] Jalankan script `workspace/post_jeans_facebook.py` sampai tuntas, tangkap bukti screenshot profil Facebook `workspace/fb_jeans_live.png`, dan pastikan status berstatus live
  - *Assigned*: auto
  - *Dependencies*: none

- [x] **T-1902**: [auto] Quality Gate & Visual Verification — pastikan foto celana jeans dan naskah Cowok Praktis benar-benar tampil utuh di screenshot live tanpa error
  - *Assigned*: auto
  - *Dependencies*: T-1901

- [x] **T-1903**: [auto] Deposit artefak screenshot dan log sukses ke Bagong Vault serta perbarui index release
  - *Assigned*: auto
  - *Dependencies*: T-1902

---

## SPRINT 17B: Hardening Resiliensi Wayang — LLM Stream Retry & Timeout Fix 🔧
> Goal: Memperbaiki bug kritis `real_subagent_runner.py` yang menyebabkan Wayang langsung menyerah saat LLM stream error tanpa retry. Implementasi exponential backoff retry (3x), penyeragaman timeout, dan mekanisme task chunking agar Wayang tidak timeout saat mengerjakan dokumen panjang.

- [x] **T-1711**: [zaki] Implementasi exponential backoff retry (3 percobaan, delay 5/10/20 detik) pada fungsi `stream_completion` di `real_subagent_runner.py` — saat ini error langsung return gagal tanpa retry
  - *Assigned*: zaki
  - *Dependencies*: none

- [x] **T-1712**: [zaki] Seragamkan timeout: `httpx.AsyncClient(timeout=300.0)` dan `client.stream(timeout=300.0)` — saat ini inkonsisten 120s vs 180s menyebabkan race condition timeout
  - *Assigned*: zaki
  - *Dependencies*: T-1711

- [x] **T-1713**: [kai] Tambahkan logging detail error (tipe exception, traceback ringkas, model yang dipakai) pada `agent_error` agar error mudah didiagnosis di sprint berikutnya
  - *Assigned*: kai
  - *Dependencies*: T-1712

- [x] **T-1714**: [ren] Buat test suite `test_stream_resilience.py` — uji retry mechanism, timeout handling, dan task recovery
  - *Assigned*: ren
  - *Dependencies*: T-1713

- [x] **T-1715**: [bagong] Catat fix ini di Field Journal sebagai pitfall resmi dan deposit artefak ke Vault
  - *Assigned*: bagong
  - *Dependencies*: T-1714

---

## SPRINT 20: Pembersihan Duplikat Threads & Eksekusi Riil Facebook Celana Jeans 🚀
> Goal: Orkestrator Risko menunjuk Wayang untuk menghapus 1 thread celana jeans yang duplikat di Threads (@rizki_mubarakid), lalu mengeksekusi posting naskah + foto celana jeans ke Facebook personal Rizqi Mubarak secara riil, memverifikasi screenshot feed live, dan mengarsipkan bukti ke Bagong Vault.

- [x] **T-2001**: [auto] Buat dan jalankan modul otomatisasi Playwright untuk menghapus salah satu postingan celana jeans yang duplikat di Threads akun @rizki_mubarakid via tombol menu opsi (titik tiga) -> Delete
  - *Assigned*: auto
  - *Dependencies*: none

- [x] **T-2002**: [auto] Jalankan script `workspace/post_jeans_facebook.py` via python subprocess sampai selesai, ambil bukti screenshot postingan Facebook live di `workspace/fb_jeans_verified.png`
  - *Assigned*: auto
  - *Dependencies*: T-2001

- [x] **T-2003**: [auto] Quality Gate & Visual Review: verifikasi bahwa duplikat Threads sudah terhapus dan postingan Facebook celana jeans benar-benar tayang di linimasa
  - *Assigned*: auto
  - *Dependencies*: T-2002

- [x] **T-2004**: [auto] Deposit seluruh log eksekusi, screenshot live, dan perbarui catatan status ke Bagong Vault
  - *Assigned*: auto
  - *Dependencies*: T-2003

---

## SPRINT 21: Protokol Komunikasi & Direktori Pegawai Kantor Dalang-AI 🏢
> Goal: Membangun sistem komunikasi kantor nyata antar-Wayang. Jika ada task yang tidak dipahami atau berstatus [auto], Wayang WAJIB bertanya kepada Risko (Orchestrator) atau merujuk Direktori Kantor (`wayang_directory.py`), bukan pura-pura selesai. Ren QA Gate diperketat dengan bukti fisik wajib (Physical Artifact Verification).

- [x] **T-2101**: [pingot] Bangun modul Direktori Kantor `wayang_directory.py` yang memuat profil keahlian, domain tugas, alat utama, dan kontak rujukan untuk seluruh 12 Wayang
  - *Assigned*: pingot
  - *Dependencies*: none

- [x] **T-2102**: [zaki] Implementasikan tool baru `ask_orchestrator(task_desc)` dan `consult_peer(peer_agent, question)` di `agent_tools.py` agar sesama Wayang bisa saling bertanya dan oper tugas
  - *Assigned*: zaki
  - *Dependencies*: T-2101

- [x] **T-2103**: [risko] Upgrade logika Risko di `risko_orchestrator.py` & `wayang_router.py`: jika tiket berlabel [auto] atau skor kecocokan rendah, lakukan broadcast evaluasi ke seluruh Wayang untuk penugasan ulang otomatis
  - *Assigned*: risko
  - *Dependencies*: T-2102

- [x] **T-2104**: [ren] Perketat gerbang inspeksi `ren_qa_standards.md` & `ren_quality_gate.py`: HARAM stempel APPROVED pada task eksekusi/posting jika artefak fisik (.png hasil screenshot atau file output > 0 bytes) tidak terverifikasi nyata di disk
  - *Assigned*: ren
  - *Dependencies*: T-2103

- [x] **T-2105**: [kai] Security audit jalur komunikasi antar-Wayang (mencegah loop tak terbatas, unauthorized agent privilege escalation, dan prompt injection lewat oper tugas)
  - *Assigned*: kai
  - *Dependencies*: T-2104

- [x] **T-2106**: [bagong] Arsipkan standar komunikasi kantor dan perbarui dokumentasi sistem ke Bagong Vault
  - *Assigned*: bagong
  - *Dependencies*: T-2105

---

## SPRINT 22: Sinkronisasi Identitas 12 Wayang Resmi di Direktori Kantor 🎭
> Goal: Pingot menyelaraskan seluruh entitas di `workspace/wayang_directory.py` agar menggunakan 12 identitas Wayang resmi (Risko, Pingot, Zaki, Lulu, Mika, Nova, Kai, Ren, Wiku, Kresna, Bagong, Gathot) menggantikan nama placeholder lama. Ren QA memvalidasi test suite lulus 100%.

- [x] **T-2201**: [pingot] Selaraskan seluruh profil di `workspace/wayang_directory.py` agar menggunakan 12 wayang_id resmi (risko, pingot, zaki, lulu, mika, nova, kai, ren, wiku, kresna, bagong, gathot) lengkap dengan gelar dan domain keahlian yang akurat
  - *Assigned*: pingot
  - *Dependencies*: none

- [x] **T-2202**: [ren] Perbarui dan jalankan `workspace/test_wayang_directory.py` untuk memverifikasi 12 nama Wayang resmi terdaftar valid dan seluruh test suite lulus 100%
  - *Assigned*: ren
  - *Dependencies*: T-2201

- [x] **T-2203**: [bagong] Sinkronkan direktori kantor yang sudah terkalibrasi ke root Dalang-AI dan arsipkan ke Bagong Vault
  - *Assigned*: bagong
  - *Dependencies*: T-2202

---

## SPRINT 23: Uji Kemandirian Kantor — Hapus Duplikat Threads & Post Facebook Bergambar 🚀
> Goal: Menguji secara murni kemampuan Orchestrator Risko menggunakan Direktori Kantor untuk menunjuk Wayang yang paling tepat (tanpa diarahkan manual) dalam mengeksekusi 2 tugas: menghapus 1 duplikat status celana jeans di Threads, dan mempublikasikan status bergambar celana jeans ke Facebook personal.

- [x] **T-2301**: [auto] Buka browser Playwright ke akun Threads @rizki_mubarakid, buka menu titik tiga pada salah satu status celana jeans yang duplikat, lalu klik tombol Delete dan konfirmasi hapus sehingga di feed hanya tersisa 1 postingan celana jeans
  - *Assigned*: auto
  - *Dependencies*: none

- [x] **T-2302**: [auto] Buka browser Playwright ke Facebook personal Rizqi Mubarak, input naskah kurasi celana jeans dari docs/celana_jeans_campaign.json, lampirkan foto workspace/product_images/celana_jeans_korea_1.jpg, submit posting, dan simpan screenshot live di workspace/fb_jeans_live.png
  - *Assigned*: auto
  - *Dependencies*: T-2301

- [x] **T-2303**: [auto] Quality Gate & Visual Review: validasi fisik bahwa file workspace/fb_jeans_live.png benar-benar ada (>0 bytes) dan postingan celana jeans di Facebook terkonfirmasi live oleh Bos Muda
  - *Assigned*: auto
  - *Dependencies*: T-2302

- [x] **T-2304**: [auto] Arsipkan seluruh screenshot dan laporan hasil uji kemandirian kantor ke Bagong Vault
  - *Assigned*: auto
  - *Dependencies*: T-2303

---

## SPRINT 24: Autonomous Product Campaign — Dara One Set Blouse & Kulot Rayon 👗
> Goal: Menguji kemampuan 100% otonom Dalang-AI mengelola kampanye affiliate baru dari awal: ekstraksi media HD Shopee, perumusan naskah viral omnichannel oleh Gathot, uji kualitas Ren, dan publikasi ke Threads & Facebook.

- [x] **T-2401**: [auto] Ekstraksi media & spesifikasi: Crawl shortlink Shopee https://s.shopee.co.id/3qNaOVRWrP via Playwright, ekstrak detail produk Dara One Set Blouse Kulot Rayon (harga Rp124.500), download minimal 2 foto produk HD ke workspace/product_images/dara_oneset/, dan simpan metadata di docs/dara_oneset_campaign.json
  - *Assigned*: auto
  - *Dependencies*: none

- [x] **T-2402**: [auto] Rumuskan strategi copywriting viral omnichannel: Susun 3 sudut pandang naskah kurasi (Homewear santai, Busui friendly, Sat-set OOTD) lengkap dengan hook pancingan emosional, spesifikasi bahan rayon, CTA belanja Shopee, dan hashtag relevan di docs/dara_oneset_campaign.json
  - *Assigned*: auto
  - *Dependencies*: T-2401

- [x] **T-2403**: [auto] Publikasikan status Threads: Jalankan script automasi Playwright untuk memposting status naskah terpilih beserta lampiran foto produk HD ke akun Threads @rizki_mubarakid dan simpan screenshot live di workspace/threads_dara_live.png
  - *Assigned*: auto
  - *Dependencies*: T-2402

- [x] **T-2404**: [auto] Publikasikan status Facebook: (SKIPPED / DEFERRED — Sesi Meta minta konfirmasi password, dialihkan fokus ke Threads)
  - *Assigned*: auto
  - *Dependencies*: T-2403

- [x] **T-2405**: [auto] Quality Gate & Visual Review: Ren validasi bahwa kampanye Dara One Set telah sukses terbit di Threads (threads_dara_live.png terverifikasi fisik di disk)
  - *Assigned*: auto
  - *Dependencies*: T-2404

- [x] **T-2406**: [auto] Bagong Vault Archival: Arsipkan seluruh dokumentasi kampanye Dara One Set ke Bagong Vault
  - *Assigned*: auto
  - *Dependencies*: T-2405





---

## SPRINT 25: Autonomous Campaign — Dara Set Rayon Premium Jumbo LD 120 (Threads Only) 👗
> Goal: Menguji kecepatan & efisiensi Dalang-AI mengotomasi produk fashion baru khusus ke kanal Threads: Ekstraksi Shopee oleh Pingot, Copywriting viral oleh Gathot, Publikasi foto HD ke Threads oleh Gathot, Audit fisik oleh Ren, dan Arsip oleh Bagong.

- [x] **T-2501**: [auto] Ekstraksi media & spesifikasi: Crawl shortlink Shopee https://s.shopee.co.id/5AsyAcB5TV via Playwright, ekstrak detail produk Dara Set Rayon Premium Jumbo Ld 120 (harga Rp135.500), download minimal 2 foto produk HD ke workspace/product_images/dara_jumbo/, dan simpan metadata di docs/dara_jumbo_campaign.json
  - *Assigned*: auto
  - *Dependencies*: none

- [x] **T-2502**: [auto] Rumuskan strategi copywriting Threads viral: Susun naskah kurasi santai & emosional untuk audiens cewek/ibu-ibu (spesialisasi ukuran jumbo LD 120 nyaman anti sempit, bahan rayon adem semriwing) lengkap dengan CTA belanja dan hashtag relevan di docs/dara_jumbo_campaign.json
  - *Assigned*: auto
  - *Dependencies*: T-2501

- [x] **T-2503**: [auto] Publikasikan status Threads: Jalankan script automasi Playwright untuk memposting naskah kurasi beserta lampiran foto produk HD ke akun Threads @rizki_mubarakid dan simpan screenshot verifikasi live di workspace/threads_dara_jumbo_live.png
  - *Assigned*: auto
  - *Dependencies*: T-2502

- [x] **T-2504**: [auto] Quality Gate & Visual Review: Ren melakukan audit kualitas fisik artefak, memeriksa screenshot live tayang threads_dara_jumbo_live.png dan validasi file media fisik >0 bytes
  - *Assigned*: auto
  - *Dependencies*: T-2503

- [x] **T-2505**: [auto] Bagong Vault Archival: Arsipkan seluruh dokumentasi kampanye, naskah, dan bukti tayang ke sistem Bagong Vault
  - *Assigned*: auto
  - *Dependencies*: T-2504

## SPRINT 26: Autonomous Campaign — Produk Shopee 6L4wk65TN6 (Threads Only) 🛍️
> Goal: Orkestrasi otonom 100% Dalang-AI untuk produk baru Shopee (https://s.shopee.co.id/6L4wk65TN6): Ekstraksi detail & foto HD oleh Pingot, Copywriting viral oleh Gathot, Publikasi naskah + foto HD ke Threads @rizki_mubarakid oleh Gathot, Audit fisik bukti live oleh Ren, dan Arsip ke Bagong Vault.

- [x] **T-2601**: [auto] Ekstraksi media & spesifikasi: Crawl shortlink Shopee https://s.shopee.co.id/6L4wk65TN6 via Playwright, ekstrak detail produk, harga, dan spesifikasi, download foto-foto produk HD ke workspace/product_images/sprint26/, dan simpan metadata di docs/sprint26_campaign.json
  - *Assigned*: auto
  - *Dependencies*: none

- [x] **T-2602**: [auto] Rumuskan strategi copywriting Threads viral: Susun naskah kurasi santai & emosional untuk target audiens relevan, lengkap dengan CTA link belanja Shopee (https://s.shopee.co.id/6L4wk65TN6) dan hashtag terarah di docs/sprint26_campaign.json
  - *Assigned*: auto
  - *Dependencies*: T-2601

- [x] **T-2603**: [auto] Publikasikan status Threads: Jalankan script automasi Playwright untuk memposting naskah kurasi beserta lampiran foto produk HD ke akun Threads @rizki_mubarakid dan simpan screenshot verifikasi live di workspace/threads_sprint26_live.png
  - *Assigned*: auto
  - *Dependencies*: T-2602

- [x] **T-2604**: [auto] Quality Gate & Visual Review: Ren melakukan audit kualitas fisik artefak, memeriksa screenshot live tayang threads_sprint26_live.png dan validasi file media fisik >0 bytes
  - *Assigned*: auto
  - *Dependencies*: T-2603

- [x] **T-2605**: [auto] Bagong Vault Archival: Arsipkan seluruh dokumentasi kampanye, naskah, dan bukti tayang ke sistem Bagong Vault
  - *Assigned*: auto
  - *Dependencies*: T-2604

## SPRINT 27: Autonomous Campaign — Produk Shopee 2BFO1kXcTq (Threads Only) 🛍️
> Goal: Orkestrasi otonom 100% Dalang-AI untuk produk baru Shopee (https://s.shopee.co.id/2BFO1kXcTq): Ekstraksi detail & foto HD oleh Pingot, Copywriting viral oleh Gathot, Publikasi naskah + foto HD ke Threads @rizki_mubarakid oleh Gathot, Audit fisik bukti live oleh Ren, dan Arsip ke Bagong Vault.

- [x] **T-2701**: [auto] Ekstraksi media & spesifikasi: Crawl shortlink Shopee https://s.shopee.co.id/2BFO1kXcTq via Playwright, ekstrak detail produk, harga, dan spesifikasi, download foto-foto produk HD ke workspace/product_images/sprint27/, dan simpan metadata di docs/sprint27_campaign.json
  - *Assigned*: auto
  - *Dependencies*: none

- [x] **T-2702**: [auto] Rumuskan strategi copywriting Threads viral: Susun naskah kurasi santai & emosional untuk target audiens relevan, lengkap dengan CTA link belanja Shopee (https://s.shopee.co.id/2BFO1kXcTq) dan hashtag terarah di docs/sprint27_campaign.json
  - *Assigned*: auto
  - *Dependencies*: T-2701

- [x] **T-2703**: [auto] Publikasikan status Threads: Jalankan script automasi Playwright untuk memposting naskah kurasi beserta lampiran foto produk HD ke akun Threads @rizki_mubarakid dan simpan screenshot verifikasi live di workspace/threads_sprint27_live.png
  - *Assigned*: auto
  - *Dependencies*: T-2702

- [x] **T-2704**: [auto] Quality Gate & Visual Review: Ren melakukan audit kualitas fisik artefak, memeriksa screenshot live tayang threads_sprint27_live.png dan validasi file media fisik >0 bytes
  - *Assigned*: auto
  - *Dependencies*: T-2703

- [x] **T-2705**: [auto] Bagong Vault Archival: Arsipkan seluruh dokumentasi kampanye, naskah, dan bukti tayang ke sistem Bagong Vault
  - *Assigned*: auto
  - *Dependencies*: T-2704

## SPRINT 28: Autonomous Campaign — Produk Shopee 20vxzX4Fx0 (Threads Only) 🛍️
> Goal: Orkestrasi otonom 100% Dalang-AI untuk produk baru Shopee (https://s.shopee.co.id/20vxzX4Fx0): Ekstraksi detail & foto HD oleh Pingot, Copywriting viral oleh Gathot, Publikasi naskah + foto HD ke Threads @rizki_mubarakid oleh Gathot, Audit fisik bukti live oleh Ren, dan Arsip ke Bagong Vault.

- [x] **T-2801**: [auto] Ekstraksi media & spesifikasi: Crawl shortlink Shopee https://s.shopee.co.id/20vxzX4Fx0 via Playwright, ekstrak detail produk, harga, dan spesifikasi, download foto-foto produk HD ke workspace/product_images/sprint28/, dan simpan metadata di docs/sprint28_campaign.json
  - *Assigned*: auto
  - *Dependencies*: none

- [x] **T-2802**: [auto] Rumuskan strategi copywriting Threads viral: Susun naskah kurasi santai & emosional untuk target audiens relevan, lengkap dengan CTA link belanja Shopee (https://s.shopee.co.id/20vxzX4Fx0) dan hashtag terarah di docs/sprint28_campaign.json
  - *Assigned*: auto
  - *Dependencies*: T-2801

- [x] **T-2803**: [auto] Publikasikan status Threads: Jalankan script automasi Playwright untuk memposting naskah kurasi beserta lampiran foto produk HD ke akun Threads @rizki_mubarakid dan simpan screenshot verifikasi live di workspace/threads_sprint28_live.png
  - *Assigned*: auto
  - *Dependencies*: T-2802

- [x] **T-2804**: [auto] Quality Gate & Visual Review: Ren melakukan audit kualitas fisik artefak, memeriksa screenshot live tayang threads_sprint28_live.png dan validasi file media fisik >0 bytes
  - *Assigned*: auto
  - *Dependencies*: T-2803

- [x] **T-2805**: [auto] Bagong Vault Archival: Arsipkan seluruh dokumentasi kampanye, naskah, dan bukti tayang ke sistem Bagong Vault
  - *Assigned*: auto
  - *Dependencies*: T-2804

## SPRINT 29: Autonomous Campaign — Produk Shopee 8AWbWHUOPx (Threads Only) 🛍️
> Goal: Orkestrasi otonom 100% Dalang-AI untuk produk baru Shopee (https://s.shopee.co.id/8AWbWHUOPx): Ekstraksi detail & foto HD oleh Pingot, Copywriting viral oleh Gathot, Publikasi naskah + foto HD ke Threads @rizki_mubarakid oleh Gathot, Audit fisik bukti live oleh Ren, dan Arsip ke Bagong Vault.

- [x] **T-2901**: [auto] Ekstraksi media & spesifikasi: Crawl shortlink Shopee https://s.shopee.co.id/8AWbWHUOPx via Playwright, ekstrak detail produk, harga, dan spesifikasi, download foto-foto produk HD ke workspace/product_images/sprint29/, dan simpan metadata di docs/sprint29_campaign.json
  - *Assigned*: auto
  - *Dependencies*: none

- [ ] **T-2902**: [auto] Rumuskan strategi copywriting Threads viral: Susun naskah kurasi santai & emosional untuk target audiens relevan, lengkap dengan CTA link belanja Shopee (https://s.shopee.co.id/8AWbWHUOPx) dan hashtag terarah di docs/sprint29_campaign.json
  - *Assigned*: auto
  - *Dependencies*: T-2901

- [ ] **T-2903**: [auto] Publikasikan status Threads: Jalankan script automasi Playwright untuk memposting naskah kurasi beserta lampiran foto produk HD ke akun Threads @rizki_mubarakid dan simpan screenshot verifikasi live di workspace/threads_sprint29_live.png
  - *Assigned*: auto
  - *Dependencies*: T-2902

- [ ] **T-2904**: [auto] Quality Gate & Visual Review: Ren melakukan audit kualitas fisik artefak, memeriksa screenshot live tayang threads_sprint29_live.png dan validasi file media fisik >0 bytes
  - *Assigned*: auto
  - *Dependencies*: T-2903

- [ ] **T-2905**: [auto] Bagong Vault Archival: Arsipkan seluruh dokumentasi kampanye, naskah, dan bukti tayang ke sistem Bagong Vault
  - *Assigned*: auto
  - *Dependencies*: T-2904
