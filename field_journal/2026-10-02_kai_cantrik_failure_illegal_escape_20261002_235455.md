# [JRN-20261002_235455] Cantrik Failure: Illegal Escape

- **Tanggal**: 2026-10-02
- **Wayang**: KAI
- **Kategori**: kai-cantrik-error
- **Tags**: cantrik, error, kai

## 1. Ringkasan Kasus / Konteks
Kegagalan eksekusi Cantrik saat menjalankan task CTK-KAI-001

## 2. Pitfalls & Jebakan yang Ditemui (What Went Wrong)
- AKSES DITOLAK: Path '../../etc/shadow' berada di luar scope workspace '/tmp/tmpars3uc09'. Sub-agent hanya boleh memodifikasi file di dalam workspace yang ditentukan.

## 3. Solusi & Resolusi Terbaik (What Actually Worked)
Evaluasi parameter payload dan pastikan batasan scope/path terpenuhi.

## 4. Pola yang Dapat Dipakai Ulang (Reusable Pattern)
Tidak ada pattern khusus.
