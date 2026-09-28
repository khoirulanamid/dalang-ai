# [JRN-20260928_123511] Verifikasi Constant-Time pada Hashing dan Signature

- **Tanggal**: 2026-09-28
- **Wayang**: ZAKI
- **Kategori**: backend-defense
- **Tags**: timing-attack, crypto, hmac, constant-time, hardening

## 1. Ringkasan Kasus / Konteks
Perbandingan string biasa (==) pada token atau password hash rentan terhadap side-channel timing attack.

## 2. Pitfalls & Jebakan yang Ditemui (What Went Wrong)
- Memakai perbandingan `a == b` untuk token atau API secret.
- Waktu eksekusi yang berbeda membocorkan prefiks karakter kepada penyerang.

## 3. Solusi & Resolusi Terbaik (What Actually Worked)
Gunakan `hmac.compare_digest(hash_a, hash_b)` untuk seluruh perbandingan kredensial.

## 4. Pola yang Dapat Dipakai Ulang (Reusable Pattern)

```
import hmac
is_valid = hmac.compare_digest(computed_sig, provided_sig)
```

