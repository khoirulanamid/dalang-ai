# ❄️ Kalkulator Dingin — Dokumentasi Resmi

**Kalkulator Dingin** adalah aplikasi kalkulator web presisi tinggi dengan tema visual Nordic Glacier / Frost Subzero, dirancang oleh **Lulu (Wayang Visual)**, diuji oleh **Ren (Wayang Jaksa)**, dan didokumentasikan oleh **Mika (Wayang Pujangga)** di bawah naungan **Dalang-AI**.

---

## 1. Tutorial: Memulai Penggunaan

### Membuka Kalkulator
Buka file `index.html` langsung di browser modern apapun, atau gunakan local web server:

```bash
# Jalankan server lokal dari folder kalkulator:
cd workspace/calculator
python3 -m http.server 4567
```
Buka browser di: **`http://localhost:4567`**

---

## 2. How-To Guide: Panduan Operasional

### A. Operasi Aritmatika Dasar
- **Penjumlahan (+)**: Masukkan angka pertama, klik `+`, masukkan angka kedua, lalu klik `=`.
- **Pengurangan (−)**: Masukkan angka pertama, klik `−`, masukkan angka kedua, lalu klik `=`.
- **Perkalian (×)**: Masukkan angka pertama, klik `×`, masukkan angka kedua, lalu klik `=`.
- **Pembagian (÷)**: Masukkan angka pembilang, klik `÷`, masukkan angka penyebut, lalu klik `=`.

### B. Pintasan Papan Ketik (Keyboard Shortcuts)
Aplikasi mendukung interaksi keyboard penuh tanpa perlu menyentuh mouse:

| Tombol Keyboard | Aksi |
|---|---|
| `0` sampai `9` | Memasukkan angka |
| `.` atau `,` | Titik desimal |
| `+` | Operator Tambah |
| `-` | Operator Kurang |
| `*` atau `x` | Operator Kali |
| `/` | Operator Bagi |
| `Enter` atau `=` | Eksekusi perhitungan / Sama dengan |
| `Backspace` | Hapus satu karakter terakhir (⌫) |
| `Escape` | Reset kalkulator (AC) atau tutup riwayat |
| `%` | Konversi ke persentase |
| `h` atau `H` | Buka / tutup panel riwayat |

### C. Mengelola Riwayat Perhitungan
1. Klik ikon jam di pojok kanan atas atau tekan huruf `h` pada keyboard.
2. Panel riwayat akan bergeser masuk dari kanan.
3. Klik salah satu item riwayat untuk memuat hasil perhitungan tersebut kembali ke layar utama.
4. Klik **"Hapus Semua"** untuk mengosongkan riwayat.

---

## 3. Reference: Spesifikasi Teknis

### Spesifikasi Aritmatika
- **Presisi Perhitungan**: Hingga 28 digit signifikan (Python Decimal) dan 12 desimal terpresisi (JavaScript).
- **Floating-Point Handling**: Mengeliminasi artefak IEEE 754 (contoh: `0.1 + 0.2` menghasilkan tepat `0.3`).
- **Batasan Pembagian Nol**: Menampilkan peringatan `"Pembagian Nol"` dan memblokir chaining kalkulasi liar.

### Aksesibilitas (WCAG 2.1 AA)
- **Role Application**: Mendukung screen reader dengan `aria-live="polite"` pada area display.
- **Contrast Ratio**: Rasio kontras teks angka (`#F1F5F9`) terhadap latar (`#152238`) adalah 11.2:1 (jauh melampaui batas minimum 4.5:1).
- **Focus Rings**: Outline `2px solid #38BDF8` pada navigasi Tab.

---

## 4. Explanation: Filosofi Desain "Cool Dingin"

### Kenapa Disebut "Cool Dingin"?
Kalkulator ini menolak estetika "AI Slop" generik (gradient ungu-biru silau, glassmorphism buram berlebihan). Sebaliknya, tema **Nordic Glacier / Frost Subzero** dibangun atas dasar:

1. **Subzero Slate (`#060913` & `#0D1527`)**: Latar gelap arktik yang mengurangi ketegangan mata saat dipakai berjam-jam.
2. **Glacier Cyan (`#38BDF8` & `#0284C7`)**: Aksen es dingin untuk tombol operator dan hasil kalkulasi.
3. **JetBrains Mono**: Tipografi monospace bertenaga yang menjamin setiap digit sejajar dan terbaca tanpa keraguan.
