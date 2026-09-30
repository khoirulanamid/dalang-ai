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

## 6. Technical SEO & Core Web Vitals Standard (from seo-monster)
- **Metadata Completeness**:
  - Setiap halaman HTML wajib memiliki `<title>` (10-70 karakter deskriptif), `<meta name="description">` (50-160 karakter), dan `<meta name="viewport">` mobile-friendly.
  - Wajib menyematkan `<link rel="canonical" href="...">` untuk mencegah penalti konten duplikat.
- **Social Sharing & OpenGraph**:
  - Wajib menyematkan OpenGraph tags (`og:title`, `og:description`, `og:image`, `og:type`) dan Twitter Card tags agar link preview tampil sempurna di Telegram, X, dan Slack.
- **Resource Preload & Web Vitals Optimization**:
  - Gunakan `<link rel="preload">` untuk critical font (Inter, JetBrains Mono) dan hero asset.
  - Pertahankan CLS (Cumulative Layout Shift) < 0.1 dengan dimensi eksplisit pada gambar dan WebGL container.

- **No Secrets in Client**: Jangan pernah embed JWT secret atau API keys di frontend bundle.
- **Token Storage**: Gunakan `httpOnly` cookie untuk refresh token bila memungkinkan; jika di memory, simpan di closures/state, bukan `localStorage` tanpa enkripsi.
- **Input Sanitization**: Escape semua user-generated content sebelum di-render ke DOM (cegah XSS).

## 7. Curated Design System Palettes (20 Color Combinations for Designers)
Setiap proyek web/UI yang dibangun oleh Lulu wajib mengadopsi salah satu dari 20 kombinasi warna terkurasi ini untuk menjamin konsistensi kontras, estetika anti-slop, dan kecocokan psikologi brand:

1. **Classic Blue & White** (`#2563EB`, `#3B82F6`, `#93C5FD`, `#FBFAFC`) — *Clean, professional, timeless* (Tech, Corporate, B2B SaaS).
2. **Black & Gold** (`#111827`, `#D4AF37`, `#F6D365`, `#FFF8E7`) — *Bold, luxurious, elegant* (Fintech, Luxury, Premium Brands).
3. **Teal & Coral** (`#0F766E`, `#14B8A6`, `#FF6D6B`, `#FFE5E5`) — *Fresh, vibrant, energetic* (Creative, Travel, Lifestyle).
4. **Purple & Pink** (`#7C3AED`, `#A855F7`, `#EC4899`, `#FCE7F3`) — *Modern, stylish, playful* (Consumer Apps, Fashion, Gen-Z).
5. **Earth Tones** (`#2F4F2F`, `#6B8E23`, `#B08968`, `#EADCC8`) — *Natural, calm, balanced* (Wellness, Eco/Sustainability, Outdoor).
6. **Red & Black** (`#EF4444`, `#B91C1C`, `#111827`, `#9CA3AF`) — *Bold, powerful, dramatic* (Gaming, Sports, High-Impact Action).
7. **Pastel Dream** (`#C4B5FD`, `#93C5FD`, `#A7F3D0`, `#FBCFE8`) — *Soft, fresh, friendly* (Healthcare, Kids, Beauty, Soft Lifestyle).
8. **Monochrome Blue** (`#0F172A`, `#3B82F6`, `#93C5FD`, `#E0F2FE`) — *Clean, modern, focused* (Minimalist Tech, Developer Tools, Analytics).
9. **Orange & Navy** (`#F97316`, `#FB923C`, `#1E3A8A`, `#CBD5E1`) — *Energetic, confident, modern* (EdTech, Startups, High-Conversion CTA).
10. **Pink & Beige** (`#F472B6`, `#EC4899`, `#E7D8C9`, `#FAF7F2`) — *Warm, soft, elegant* (Feminine Brands, Fashion, Boutique).
11. **Grey & Blue** (`#374151`, `#64748B`, `#CBD5E1`, `#F1F5F9`) — *Professional, calm, versatile* (UI/UX Dashboards, Cloud Systems, Enterprise).
12. **Yellow & Black** (`#FACC15`, `#EAB308`, `#111827`, `#E5E7EB`) — *Bright, bold, energetic* (Modern Brands, Social Media, Industrial).
13. **Mint & Gray** (`#10B981`, `#6B7280`, `#D1D5DB`, `#F3F4F6`) — *Fresh, clean, modern* (Fintech, Healthtech, Minimalist UI).
14. **Violet & Yellow** (`#7C3AED`, `#A78BFA`, `#FACC15`, `#FEF3C7`) — *Creative, bold, eye-catching* (Education, Creative Studios, Portfolios).
15. **Brown & Cream** (`#4B2E1E`, `#8B5E3C`, `#D6B89C`, `#FFF7ED`) — *Warm, cozy, sophisticated* (F&B, Artisan Coffee, Handmade, Luxury Goods).
16. **Red & Beige** (`#8B5226`, `#FB7171`, `#E7DCC6`, `#FDF7F2`) — *Warm, inviting, stylish* (Culinary, Hospitality, Lifestyle).
17. **Indigo & Turquoise** (`#4F46E5`, `#06B6D4`, `#22D3EE`, `#E0F7FA`) — *Bold, fresh, creative* (Digital Nomads, Modern Web3, Media).
18. **Black & White Accent** (`#111827`, `#6B7280`, `#D1D5DB`, `#10B981`) — *Minimal, clean, impactful* (Engineering Portfolios, Dark UI).
19. **Sand & Teal** (`#E7DCC6`, `#C9A96A`, `#0F766E`, `#134E4A`) — *Calm, premium, architectural* (Interior Architecture, Premium Real Estate).
20. **Vibrant Gradient** (`#8B5CF6`, `#06B6D4`, `#F97316`, `#10B981`) — *Dynamic, futuristic* (Next-Gen AI, Creative Tech Showcase).

### 4 Golden Rules of Application:
- **60-30-10 Rule**: 1 warna netral/dominan (60%), 1 warna sekunder (30%), 1–2 warna aksen fokus (10%).
- **Contrast Integrity**: Pastikan rasio kontras teks terhadap latar memenuhi WCAG 2.1 AA (minimal 4.5:1).
- **Scale Testing**: Uji palet pada elemen mikro (tag, badge, favicon) dan elemen makro (hero section, full banner).
- **Brand Mood Congruence**: Selaraskan emosi warna dengan psikologi industri pengguna akhir.



---

## 8. Dark Mode Native Form Controls & Contrast Integrity (Anti-Invisible Dropdown Bug)
**Critical Pitfall & Rule (Diajarkan oleh Bos Muda):**
Pada tema dark-mode, elemen form native seperti `<select>`, `<option>`, dan `<datalist>` memiliki perilaku browser/OS rendering yang berbahaya jika hanya di-style dengan semi-transparent background (seperti `rgba(...)`). Browser (Chrome, Safari, Edge) sering merender dropdown menu popup dengan latar belakang putih/terang default, sehingga teks option yang berwarna putih menjadi **100% tidak terlihat (white-on-white / unreadable)**.

### Mandatory Rules for Dark Theme Form Controls:
1. **Solid Opaque Background**: Jangan gunakan `rgba()` transparan murni pada `<select>`. Wajib berikan warna latar solid gelap (misal `#18191b` atau `#0f1011`).
2. **Explicit Option Styling**: Wajib deklarasikan style eksplisit untuk anak elemen `<option>`:
   ```css
   select.control-select {
     background-color: #18191b;
     color: #f7f8f8;
     appearance: none;
     -webkit-appearance: none;
     background-image: url("data:image/svg+xml,...chevron...");
     background-repeat: no-repeat;
     background-position: right 10px center;
     padding-right: 28px;
   }
   select.control-select option {
     background-color: #18191b;
     color: #f7f8f8;
     padding: 8px 10px;
   }
   ```
3. **Delivery Gate Verification**: Saat membuat form dropdown di dark mode, pastikan kontras teks pilihan menu opsi selalu terbaca jelas (rasio kontras > 4.5:1) di seluruh browser dan OS.

---

### 🎓 Pelajaran Baru — Diajarkan oleh Bos Muda (2026-09-25 10:01 UTC)
Gunakan Tailwind CSS v3 sebagai framework styling utama. Hindari inline CSS dan vanilla CSS berlebihan. Pakai lucide-icons untuk ikonografi. Setiap komponen wajib dark-mode compatible.
