# [JRN-20260928_123511] Isolasi Path Workspace pada Eksekusi Pytest

- **Tanggal**: 2026-09-28
- **Wayang**: REN
- **Kategori**: qa-automation
- **Tags**: pytest, workspace, cwd, isolation, regression

## 1. Ringkasan Kasus / Konteks
File test di dalam subfolder workspace/ mengasumsikan current working directory berada di workspace/ saat membaca artefak lokal.

## 2. Pitfalls & Jebakan yang Ditemui (What Went Wrong)
- Menjalankan pytest dari root repository langsung tanpa menyetel PYTHONPATH atau CWD membuat FileNotFoundError pada file lokal workspace.

## 3. Solusi & Resolusi Terbaik (What Actually Worked)
Jalankan pytest dengan target spesifik per direktori atau gunakan rootdir konfigurasi eksplisit.

## 4. Pola yang Dapat Dipakai Ulang (Reusable Pattern)

```
cd workspace && pytest test_security.py
```

