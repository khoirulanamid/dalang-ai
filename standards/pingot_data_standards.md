# Data Modeling & Schema Standard (DDD & Data Contracts)
**Standard Reference:** Domain-Driven Design (Eric Evans) · RFC 7946 · ISO 8601 · Data Contract Spec

## 1. Domain Modeling (DDD)
- **Ubiquitous Language**: Semua nama class, field, dan method harus mencerminkan domain bisnis nyata (bukan istilah teknis database).
- **Entities vs Value Objects**:
  - `Entity`: Punya identitas unik yang bertahan seiring waktu (contoh: `User` dengan UUID).
  - `Value Object`: Bersifat immutable, tidak punya identitas, hanya dibedakan dari nilai (contoh: `EmailAddress`, `HashedPassword`).
- **Invariants**: Validasi integritas data harus terjadi di dalam model saat inisialisasi, bukan di luar model.

## 2. Security-by-Design in Data Layer
- **No Raw Secrets**: Model data tidak boleh menyimpan plaintext credentials dalam bentuk apa pun.
- **Explicit Projection**: Selalu pisahkan model penyimpanan (`UserInDB`) dengan model eksposur API (`UserPublic`). Jangan gunakan auto-serialize tanpa whitelist fields.
- **Salt & Hash Isolation**: Salt harus cryptographically random (minimum 16 bytes dari `os.urandom`) dan disimpan bersama hash dengan format standardized (e.g. `$algo$rounds$salt$hash`).

## 4. Anti-AI-Slop Code Hygiene Standard (from antislop-code)
- **No Decorative Banner Comments**: DILARANG membuat komentar hiasan berbasis karakter berulang (`# ====================`, `# --------------------`, `/* ******* */`).
- **No Stating the Obvious**: DILARANG menulis komentar yang hanya mengulang nama variabel/fungsi (contoh: `# user email` di atas `email: str`, atau `# Initialize class` di atas `__init__`).
- **No Emoji in Code**: DILARANG menyisipkan emoji di komentar kode atau docstrings (`# 🚀 Initialize engine`, `# ✅ Validation success`). Kode harus profesional.
- **Explain 'Why', Not 'What'**: Tulis komentar HANYA jika ada keputusan arsitektur atau business rule yang tidak jelas dari membaca kode itu sendiri.

