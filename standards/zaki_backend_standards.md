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
