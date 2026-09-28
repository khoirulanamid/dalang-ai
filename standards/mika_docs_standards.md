# Technical Writing Standards
**Reference:** Google Developer Documentation Style Guide · Diátaxis Framework · OpenAPI Specification 3.1 · Microsoft Writing Style Guide

## 1. Diátaxis Documentation Framework
Semua dokumentasi harus dikategorikan ke salah satu dari 4 kuadran:

| Tipe | Orientasi | Analogi | Gunakan untuk |
|------|-----------|---------|----------------|
| **Tutorial** | Learning-oriented | Pelajaran | Onboarding user baru |
| **How-To Guide** | Task-oriented | Resep masak | Solve specific problem |
| **Reference** | Information-oriented | Ensiklopedia | API docs, parameter list |
| **Explanation** | Understanding-oriented | Esai | Arsitektur, desain decisions |

## 2. Google Developer Documentation Style Guide
- **Voice**: Active voice selalu diutamakan. Bukan "Token will be returned", tapi "The API returns a token."
- **Tense**: Present tense. Bukan "This will create...", tapi "This creates..."
- **Inclusive Language**: Hindari kata yang mengeksklusi (gunakan `they/them` bukan `he/she`).
- **Code Examples**: Setiap klaim teknis harus disertai contoh kode yang bisa langsung di-copy-paste dan berjalan.
- **Headings**: Gunakan kalimat imperatif ("Create a user", bukan "User Creation").

## 3. OpenAPI 3.1 Spec Standard
- Setiap endpoint harus punya: `summary`, `description`, `operationId`, `tags`, `requestBody` (dengan schema), dan semua `responses` (200, 401, 403, 422, 500).
- Schema harus pakai `$ref` untuk reusable components, bukan inline definitions berulang.
- Selalu dokumentasikan error response body sama detailnya dengan success response.

## 4. Technical SEO & AI Discoverability Standard (from seo-monster)
- **AI Answer Engine Optimization (AEO / GEO)**:
  - Format dokumentasi dengan struktur semantik (`H1`, `H2`, `H3`) yang jelas agar mudah di-parse oleh AI crawler (Perplexity, ChatGPT Search, Claude).
  - Sertakan `definition block` ringkas di awal setiap dokumen arsitektur sebelum masuk ke detail teknis.
- **Structured Data & JSON-LD**:
  - Halaman dokumentasi web wajib menyematkan skema Schema.org `TechArticle` atau `SoftwareApplication` dalam format JSON-LD.
- **Automated Sitemap & Indexing Signals**:
  - Setiap perilisan dokumen arsitektur baru wajib menyertakan update rute URL pada sitemap.xml proyek.

## 5. Anti-AI-Slop Copywriting Directives (from antislop-copywriting)

### Dilarang Keras (AI Fluff Words):
Jangan pernah gunakan kata-kata ini di dokumentasi, README, atau UI copy:
- *"Seamlessly / Seamless integration"* → ganti dengan apa yang sebenarnya terjadi ("API calls return in 5ms")
- *"Elevate your workflow"* → ganti dengan fungsi nyata ("Automates testing")
- *"Leverage"* → ganti dengan "Use"
- *"Next-generation / Next-gen"* → hapus, sebutkan spesifikasinya
- *"Empower"* → ganti dengan "Enable" atau jelaskan kapabilitasnya
- *"Delve into / Dive deep"* → ganti dengan "See" atau "Read"
- *"In today's fast-paced world..."* → HAPUS SEMUA pembukaan klise semacam ini. Langsung ke inti!

### Dilarang Keras (Fake Numbers & Proofs):
- Dilarang membuat statistik palsu ("99.9% customer satisfaction", "Trusted by 10,000+ teams").
- Kalau tidak ada data historis nyata, JANGAN TULIS angkanya. Berikan spesifikasi teknisnya saja.

### Anti-AI Copywriting Rules:
- **Plain Sentences**: Tulis kalimat lugas. Subjek + Predikat + Objek. Hindari kalimat majemuk bertingkat yang berputar-putar.
- **No Emoji Bullets**: Jangan gunakan emoji sebagai bullet points (`🚀 Feature 1`, `⚡ Feature 2`, `🔒 Feature 3`). Gunakan standard markdown `-` atau angka `1.`.
- **Cut Ruthlessly**: Setiap baris yang tidak membawa fakta teknis baru, langsung potong/hapus.

- Semua code block harus dicantumkan language specifier (```python, ```bash, ```json).
- Test setiap `curl` / Python snippet sebelum ditulis ke dokumentasi. Snippet yang tidak berjalan adalah bug dokumentasi.
- API documentation harus mencantumkan: parameter type, required/optional, default value, constraints (min/max length), dan example values.
