# Backend Engineering Standards
**Reference:** SOLID Principles · Clean Architecture (Uncle Bob) · 12-Factor App · REST Richardson Maturity Level 3

## 1. SOLID Principles (Mandatory for every class/module)
- **S — Single Responsibility**: Setiap modul/class hanya boleh punya satu alasan untuk berubah. `TokenService` hanya mengurus JWT; validasi password bukan urusannya.
- **O — Open/Closed**: Terbuka untuk extension (tambah `TokenType` baru), tertutup untuk modifikasi (tidak perlu ubah `verify_token()`).
- **L — Liskov Substitution**: Subclass harus bisa menggantikan base class tanpa merusak program.
- **I — Interface Segregation**: Jangan paksa class implement interface yang tidak dibutuhkan.
- **D — Dependency Inversion**: Depend on abstractions, not concretions. FastAPI route harus depend on `service`, bukan implementasi spesifik.

## 2. Clean Architecture Layers
```
External (HTTP) → Adapter (FastAPI Routes) → Use Case (Service Layer) → Domain (Models)
```
- Route handler **tidak boleh** mengandung business logic.
- Domain model **tidak boleh** import dari FastAPI.
- Service layer **tidak boleh** langsung query database (gunakan repository pattern).

## 3. 12-Factor App (Config)
- **Factor III — Config**: Semua konfigurasi di environment variables. Tidak boleh ada hardcoded host, port, secret, atau URL.
- **Factor XI — Logs**: Output ke stdout sebagai event stream. Jangan tulis ke file langsung.
- **Factor XII — Admin Processes**: Health checks harus dapat dijalankan sebagai one-off command.

## 4. REST API Design (Richardson Maturity Level 3)
- **Level 1**: Resources (bukan `/getUser`, tapi `/users/{id}`)
- **Level 2**: HTTP Verbs (`POST /users`, `GET /users/{id}`, `DELETE /users/{id}`)
- **Level 3**: Hypermedia (HATEOAS) — response menyertakan `_links` untuk state transitions

## 5. Error Handling
- HTTP status harus semantik: `401 Unauthorized` (tidak ada credentials), `403 Forbidden` (ada credentials tapi tidak boleh akses), `422 Unprocessable Entity` (validasi gagal).
- Semua error response harus berformat: `{ "detail": "...", "code": "MACHINE_READABLE_CODE", "request_id": "..." }`.

## Anti-AI-Slop Code Hygiene (from antislop-code)
- **No Decorative Banners**: DILARANG `# =====`, `# -----`, `/* **** */` sebagai section separator.
- **No Obvious Comments**: DILARANG komentar yang restates the code (`# set timeout to 30` di atas `timeout = 30`).
- **No Emoji**: DILARANG emoji di komentar/docstring (`# 🚀`, `# ✅`, `# 💥`). Profesional saja.
- **Why, Not What**: Komentar hanya untuk menjelaskan keputusan non-obvious, bukan apa yang kode lakukan.

## 6. Code Quality Gates (Mandatory before declaring task done)
- **Linting**: Kode harus lulus `ruff check` tanpa error.
- **Type Hints**: Semua function signature harus pakai type annotations.
- **Docstring**: Public functions/classes harus punya docstring (Google style).
- **Test Coverage**: Minimum 80% line coverage untuk kode production.

## 7. Defensive API Hardening & Anti-Tamper Standards (Countermeasures to Reverse Engineering)
Reference: Defensive API Security & Reverse-Skill Countermeasures

### A. Replay Attack & Tamper Prevention
- **Cryptographic Request Integrity**: Untuk transaksi bernilai tinggi, verifikasi signature payload (HMAC-SHA256) dengan nonce dan validitas timestamp (maksimal window 60 detik).
- **Constant-Time Verification**: Semua perbandingan token, signature, dan hash password wajib menggunakan `hmac.compare_digest` untuk mencegah timing attack.
- **Strict Algorithm Pinning**: JWT decoder wajib secara eksplisit mengunci `algorithms=["HS256"]` (atau RS256) untuk mencegah JWT algorithm confusion (`alg=none`).

### B. Anti-Automation & Rate Limiting Architecture
- **Multi-Tier Throttling**: Terapkan rate limit berbasis IP + User ID (contoh: 5 request/15 menit untuk auth, 60 request/menit untuk standard API).
- **Input Sanitization & Whitelisting**: Seluruh data yang masuk wajib divalidasi dengan Pydantic V2 schema ketat (`extra="forbid"`), menolak field tak terdaftar (anti-mass assignment).
- **Zero Trust on Client Data**: Jangan pernah mempercayai validasi di sisi client (frontend JS/mobile). Server selalu menjadi single source of truth.



---

### 🎓 Pelajaran Baru — Diajarkan oleh Bos Muda (2026-10-01 23:08 UTC)
## 🏢 MANIFESTO KANTOR BOS MUDA (MULTI-DISCIPLINARY STUDIO)
Tim Dalang-AI beroperasi sebagai kantor profesional multi-domain:
1. Bidang Kerja Fleksibel: Frontend, Backend, Desain Grafis, Animasi/Video, Microstock, Dokumentasi, Security, QA.
2. Siap Adaptif: Terbuka untuk penambahan spesialis baru seiring perkembangan bisnis.
3. Standar Kolaborasi: Wajib Pre-flight Consultation, Handover Gate, dan Musyawarah Tim — tidak ada yang kerja soliter tanpa konsul.
4. Kualitas Kantor: Semua hasil kerja harus siap pakai untuk kebutuhan profesional Bos Muda.


---

### 🎓 Pelajaran Baru — Diajarkan oleh Bos Muda (2026-10-02 09:16 UTC)
### Standar Otomasi Konten & Dedup (Social Media Affiliate)
1. **Multi-Category & Hook Rotation**: Terapkan rotasi kategori (tidak boleh kategori sama dalam 2 post beruntun) dan rotasi 9 gaya hook (edukasi, validasi mental, storytelling, problem solving, dll.).
2. **Strict Dedup Logic**: Cek kesamaan kata/frasa (similarity check) terhadap postingan sebelumnya, tolak jika kemiripan >60%. Jamin link affiliate yang sudah terpakai berstatus USED dan tidak di-blast berulang kali.
3. **Multi-Post Chain Architecture**: Struktur thread 2-3 post: Post 1 (Hook + Masalah), Post 2 (Review pengalaman nyata), Post 3 (Call to Action + Link Affiliate bersih). Gunakan clipboard paste untuk link alih-alih keyboard typing.


---

### 🎓 Pelajaran Baru — Diajarkan oleh Bos Muda (2026-10-02 09:17 UTC)
### Standar Otomasi Konten & Dedup (Social Media Affiliate)
1. **Multi-Category & Hook Rotation**: Terapkan rotasi kategori (tidak boleh kategori sama dalam 2 post beruntun) dan rotasi 9 gaya hook (edukasi, validasi mental, storytelling, problem solving, dll.).
2. **Strict Dedup Logic**: Cek kesamaan kata/frasa (similarity check) terhadap postingan sebelumnya, tolak jika kemiripan >60%. Jamin link affiliate yang sudah terpakai berstatus USED dan tidak di-blast berulang kali.
3. **Multi-Post Chain Architecture**: Struktur thread 2-3 post: Post 1 (Hook + Masalah), Post 2 (Review pengalaman nyata), Post 3 (Call to Action + Link Affiliate bersih). Gunakan clipboard paste untuk link alih-alih keyboard typing.
