# Quality Assurance & Testing Standards
**Reference:** ISTQB Certified Tester Advanced Level · Google Testing Blog · Test Pyramid (Martin Fowler) · AAA Pattern · ISO/IEC/IEEE 29119

## 1. Test Pyramid Strategy
```
       /  E2E  \       5-10% (Whole system journey, slow)
      / Integration \   20-30% (API routes, db contracts)
     /      Unit     \  60-70% (Fast, isolated functions, mock I/O)
```
- **Unit Tests**: Test logic isolated dari network, disk, atau DB. Harus jalan dalam < 10ms per test.
- **Integration Tests**: Test kontrak antara modul (misal: `auth_api` panggil `token_service`).
- **E2E Tests**: Test complete user journey dari `TestClient`/browser view (misal: Register → Login → Refresh → Call `/me` → Invalidate).

## 2. AAA Pattern (Arrange-Act-Assert) — Mandatory
Semua test function **wajib** mengikuti struktur ini:
```python
def test_example():
    # 1. ARRANGE: Siapkan data dan dependencies
    user_payload = {"username": "alice", "password": "SecurePassword123!"}
    
    # 2. ACT: Panggil method/endpoint yang diuji
    response = client.post("/register", json=user_payload)
    
    # 3. ASSERT: Verifikasi kondisi ekspektasi
    assert response.status_code == 201
    assert response.json()["username"] == "alice"
```

## 3. Boundary Value Analysis (BVA) & Equivalence Partitioning
Setiap field input harus diuji pada 5 titik batas:
- `Minimum valid`: min_len = 8 → test 8 chars (harus pass)
- `Just below minimum`: min_len = 8 → test 7 chars (harus fail)
- `Nominal`: nilai tipikal di tengah range
- `Just above maximum`: max_len = 100 → test 101 chars (harus fail)
- `Maximum valid`: max_len = 100 → test 100 chars (harus pass)

## 4. Concurrent & Edge-Case Testing
Setiap sistem autentikasi harus punya test case untuk:
- **Race conditions**: Dua user register dengan username yang sama bersamaan.
- **Clock drift**: Token yang `exp` tepat 1 detik yang lalu (pastikan strictly expired).
- **Type confusion**: Kirim array saat string diekspektasikan, null payload, empty JSON.
- **Case sensitivity**: Username `Alice` vs `alice` (apakah dianggap sama atau beda).

## Anti-AI-Slop Code Hygiene (from antislop-code)
- **No Decorative Banners**: DILARANG `# =====`, `# -----`, `/* **** */` sebagai section separator.
- **No Obvious Comments**: DILARANG komentar yang restates the code (`# set timeout to 30` di atas `timeout = 30`).
- **No Emoji**: DILARANG emoji di komentar/docstring (`# 🚀`, `# ✅`, `# 💥`). Profesional saja.
- **Why, Not What**: Komentar hanya untuk menjelaskan keputusan non-obvious, bukan apa yang kode lakukan.

## 5. Test Quality Metrics
- **Assertion Density**: Minimal 2 meaningful assertions per test function.
- **No Flaky Tests**: Test yang kadang pass kadang fail karena timing adalah bug prioritas tinggi. Gunakan `freezegun` untuk manipulasi waktu, jangan `time.sleep()`.
- **Descriptive Naming**: `test_<target>_<scenario>_<expected_result>`  
  Contoh: `test_login_with_expired_token_returns_401`

## 6. Security & Tamper Regression Verification (Evidence-Based Testing)
Reference: Reverse-Skill Case Review & Verification Pattern

### A. Translating Security Findings into Pytest Assertions
Setiap temuan audit dari Kai wajib dibuatkan test case regresi oleh Ren:
- **Tamper Tests**: Verifikasi bahwa manipulasi 1 byte saja pada token atau signature menghasilkan response `401 Unauthorized`.
- **Replay Tests**: Verifikasi bahwa pengiriman ulang payload dengan timestamp kedaluwarsa atau nonce yang sudah dipakai ditolak dengan `400 Bad Request`.
- **Algorithm Confusion Tests**: Verifikasi bahwa token yang di-forge dengan header `{"alg": "none"}` langsung ditolak oleh middleware.
- **Side-Channel Timing Invariance**: Verifikasi bahwa waktu verifikasi untuk user yang tidak ada sama dengan user yang ada tetapi password salah.

### B. Evidence Chain & Reproducibility
- Test harus bersifat self-contained dan deterministic (100% reproducible di CI).
- Lampirkan ID temuan (misal: `# Ref: Kai-AUDIT-F001`) pada docstring test function.

## 7. Headless Browser Automation & E2E DOM Discipline (from reverse-skill/browser-automation)
- **DOM Structural Integrity**:
  - Verifikasi bahwa build bundle memiliki root mounting point (`#root`), asset JS/CSS terikat, dan WebGL `<canvas>` elemen aktif.
- **Client-Side Security & XSS Resistance**:
  - Validasi bahwa data dinamis dari backend yang dirender ke DOM di-escape secara aman oleh React (dilarang penggunaan `dangerouslySetInnerHTML` tanpa sanitasi DOMPurify).
- **Hermetic Headless Verification**:
  - Gunakan Playwright / Chromium headless untuk memverifikasi load time, network error HTTP 4xx/5xx di console, dan visual layout tanpa memerlukan tampilan grafis desktop.

## 8. Adversarial Candidate Validation — Uji Sangkal Lawan (from cloudflare/security-audit-skill)
- **Phase 3: The Disprover Protocol**:
  - Saat Kai mengajukan kandidat bug, peran Ren BUKAN sekadar mengonfirmasi, melainkan **secara aktif berusaha membantah/menyangkalnya (try to disprove it)**.
  - Cari kontrol mitigasi tersembunyi: Apakah tipe data sudah divalidasi Pydantic? Apakah framework sudah auto-escape? Apakah path terlindungi auth middleware?
- **Tri-State Verdict Mutlak**:
  - `confirmed`: Hanya jika uji sangkal gagal membantah dan bukti reproduksi 100% konsisten.
  - `rejected`: Jika terbukti ada mekanisme mitigasi yang menggugurkan kerentanan (Zero False Positive).
  - `needs_validation`: Jika ada fakta lingkungan yang belum konklusif (dilarang menebak).


