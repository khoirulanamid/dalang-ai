# [JRN-20260928_123511] Rotasi Sendi Three.js Sumbu X Avatar Humanoid Duduk

- **Tanggal**: 2026-09-28
- **Wayang**: LULU
- **Kategori**: 3d-kinematics
- **Tags**: threejs, kinematics, clipping, avatar, rotation

## 1. Ringkasan Kasus / Konteks
Sendi bahu dan paha avatar Three.js yang duduk di meja kerja menghadap -Z. Tanda minus pada rotation.x memutar anggota tubuh ke belakang menembus kursi.

## 2. Pitfalls & Jebakan yang Ditemui (What Went Wrong)
- Menggunakan rotation.x negatif pada bahu membuat tangan mencuat ke belakang sandaran kursi.
- Menggunakan rotation.x negatif pada pinggul membuat paha mencuat ke belakang kursi bukan ke kolong meja.

## 3. Solusi & Resolusi Terbaik (What Actually Worked)
Gunakan sudut rotasi positif (+Math.PI/2 untuk paha, +0.65 rad untuk bahu) agar anggota tubuh menekuk ke depan ke arah meja.

## 4. Pola yang Dapat Dipakai Ulang (Reusable Pattern)

```
leftLeg.hipPivot.rotation.x = Math.PI / 2;
leftShoulder.rotation.x = 0.65;
```

