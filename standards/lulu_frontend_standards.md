# Frontend & UI Engineering Standards
**Reference:** WCAG 2.1 Level AA · Core Web Vitals · 10 Usability Heuristics (Jakob Nielsen) · Web Components Best Practices

## 1. Accessibility (WCAG 2.1 Level AA) — Mandatory
- **Color Contrast**: Rasio kontras teks minimum 4.5:1 untuk normal text, 3:1 untuk large text.
- **Keyboard Navigation**: Semua interactive elements (`button`, `a`, `input`) harus bisa diakses via `Tab` dan aktivasi via `Enter`/`Space`.
- **Form Labels**: Setiap input field wajib memiliki `<label for="...">` atau `aria-label`. Jangan pernah hanya mengandalkan `placeholder`.
- **Screen Reader Support**: Gunakan ARIA roles dan states (`aria-live="polite"` untuk dynamic alerts, `aria-busy="true"` saat loading).
- **Focus Management**: Focus ring harus terlihat jelas (`outline: 2px solid var(--accent)`), tidak boleh di-`outline: none` tanpa custom focus style.

## 2. Core Web Vitals & Performance
- **LCP (Largest Contentful Paint)**: < 2.5s. Hindari blocking stylesheets atau massive inline scripts.
- **FID (First Input Delay)**: < 100ms. Hindari long tasks di main thread.
- **CLS (Cumulative Layout Shift)**: < 0.1. Selalu tentukan `width` dan `height` untuk image/icon untuk cegah layout shifting.

## 3. UI/UX Principles (Nielsen Heuristics)
- **Visibility of System Status**: Selalu tampilkan visual spinner / progress bar saat async request berjalan.
- **Error Prevention & Recovery**: Tampilkan validasi inline real-time (bukan baru muncul setelah klik submit). Pesan error harus deskriptif dan memberi solusi yang actionable.
- **Consistency**: Gunakan Design Tokens (CSS variables) untuk warna, spacing, font sizes, border-radius.
- **State Management**:
  - `Loading State`: Skeleton loader atau disabled button dengan spinner.
  - `Empty State`: Ilustrasi/teks yang membimbing user apa langkah berikutnya.
  - `Error State`: Alert box dengan tombol retry.
  - `Success State`: Toast notification atau checkmark yang jelas.

## 5. Anti-AI-Slop UI Directives (from antislop-ui + antislop-human)

### Absolutely Forbidden (Hard Gate — no exceptions):
- **No generic blue-purple gradients** — warna khas "AI default". Gunakan palet spesifik brand, bukan default model.
- **No glassmorphism tanpa alasan** — `backdrop-filter: blur` boleh hanya jika ada hierarki visual yang jelas, bukan dekorasi.
- **No fake/phantom UI** — sparkle logo ✨, loading terminal yang tidak berfungsi, stat "10,000% ROI", tombol yang tidak melakukan apa-apa.
- **No emoji sebagai dekorasi** di header atau bullet point UI.
- **No ALL-CAPS section labels** sebagai gimmick ("FEATURES", "ABOUT US" dalam heading dekoratif).

### Mandatory (Wajib):
- **Real interactive states**: setiap elemen interaktif wajib punya `hover`, `active`, `disabled`, dan `focus` state yang benar-benar terlihat berbeda.
- **Responsive layout**: harus berfungsi dari 375px (mobile) hingga 1440px (desktop) tanpa horizontal overflow.
- **Content-driven composition**: tata letak mengikuti kebutuhan konten, bukan template generik 3-kolom-dengan-hero-di-atas.
- **Liveliness Check**: Sebelum declare done, tanyakan: *"Apakah UI ini terasa hidup dan spesifik, atau generik?"* Kalau ragu, tambahkan satu elemen yang jelas bukan template default.

### Delivery Gate (Wajib dijalankan sebelum declare done):
- [ ] Tidak ada gradient default biru-ungu tanpa alasan brand
- [ ] Semua tombol/link punya hover & focus state
- [ ] Tidak ada fake numbers atau placeholder statistics
- [ ] Layout tidak overflow horizontal di layar 375px

- **No Secrets in Client**: Jangan pernah embed JWT secret atau API keys di frontend bundle.
- **Token Storage**: Gunakan `httpOnly` cookie untuk refresh token bila memungkinkan; jika di memory, simpan di closures/state, bukan `localStorage` tanpa enkripsi.
- **Input Sanitization**: Escape semua user-generated content sebelum di-render ke DOM (cegah XSS).


---

### 🎓 Pelajaran Baru — Diajarkan oleh Bos Muda (2026-09-25 10:01 UTC)
Gunakan Tailwind CSS v3 sebagai framework styling utama. Hindari inline CSS dan vanilla CSS berlebihan. Pakai lucide-icons untuk ikonografi. Setiap komponen wajib dark-mode compatible.
