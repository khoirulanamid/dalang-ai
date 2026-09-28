# [JRN-20260928_123511] Mitigasi JWT Algorithm Confusion dan Key Confusion

- **Tanggal**: 2026-09-28
- **Wayang**: KAI
- **Kategori**: security-audit
- **Tags**: jwt, auth, token, algorithm-confusion, asvs

## 1. Ringkasan Kasus / Konteks
Library JWT sering rentan terhadap serangan downgrade 'alg: none' atau verifikasi HMAC menggunakan public key RSA.

## 2. Pitfalls & Jebakan yang Ditemui (What Went Wrong)
- Tidak menyetel parameter algorithms secara eksplisit saat memanggil jwt.decode().
- Menerima token tanpa validasi claim wajib (iss, aud, exp, jti).

## 3. Solusi & Resolusi Terbaik (What Actually Worked)
Wajib kunci parameter algorithms=['HS256'] secara eksplisit dan verifikasi kehadiran jti serta exp claim.

## 4. Pola yang Dapat Dipakai Ulang (Reusable Pattern)

```
jwt.decode(token, SECRET_KEY, algorithms=['HS256'], options={'require': ['exp', 'jti']})
```

