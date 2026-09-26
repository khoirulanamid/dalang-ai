import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { Sparkles, Coffee, Users, Laptop, Send, PlusCircle, Eye, Crown, ArrowUp, ArrowDown, ArrowLeft, ArrowRight } from "lucide-react";

// 8 Para Wayang Roster & Detailed Office Profiles
const AGENT_MINGLE_DIALOGUES = {
  risko: {
    greeting: "Selamat datang di lantai engineering, Bos Muda!",
    quote: "Semua orkestrasi 8 wayang berjalan optimal dengan LLM tools nyata di workspace. Ada blueprint arsitektur atau keputusan teknis baru yang ingin Bos Muda arahkan?",
    tip: "Risko adalah Tech Lead & Dalang yang mengorkestrasi pembagian tugas lintas agen secara otomatis.",
  },
  pingot: {
    greeting: "Siang Bos Muda. Senang melihat Anda berkeliling.",
    quote: "Integritas data dan validasi skema database 100% konsisten. Semua invariant runtime dan state agen tersinkronisasi tanpa ada data anomali.",
    tip: "Pingot menjaga konsistensi schema, data model, dan state flow antarsistem.",
  },
  zaki: {
    greeting: "Halo Bos Muda! Santai sejenak atau mau cek backend?",
    quote: "Backend FastAPI lagi ngacir, zero downtime. Tadi saya baru nyeduh espresso pakai La Marzocco di pantry, mau saya racikkan secangkir?",
    tip: "Zaki mengeksekusi implementasi backend, database CRUD, dan runner tools inti.",
  },
  lulu: {
    greeting: "Hai Bos Muda! Senang banget Bos Muda jalan-jalan ke sini!",
    quote: "Gimana tampilan pencahayaan PBR dan lantai terrazzo kantor barunya? Keren banget kan estetikanya! Shaders, lighting, dan UI Linear berjalan mulus di 60 FPS.",
    tip: "Lulu bertanggung jawab atas visual 3D Three.js dan estetika sistem antislop.",
  },
  mika: {
    greeting: "Salam hormat Bos Muda. Terima kasih sudah menyapa.",
    quote: "Seluruh dokumentasi arsitektur, spesifikasi endpoint API, dan log audit sistem telah terdokumentasi rapi dan siap dipelajari tim.",
    tip: "Mika menyusun dokumentasi teknis, API specs, dan panduan arsitektur.",
  },
  nova: {
    greeting: "Siap Bos Muda! Ada instruksi terkait infrastruktur?",
    quote: "Pipeline build hijau semua, monitoring resource stabil, dan container deployment berjalan mulus tanpa downtime!",
    tip: "Nova mengelola otomatisasi CI/CD, build pipelines, dan container deployment.",
  },
  kai: {
    greeting: "Lapor Bos Muda! Keamanan sistem dalam kondisi siaga penuh.",
    quote: "Audit keamanan sistem dan verifikasi celah OWASP berjalan ketat. Seluruh akses tools diisolasi aman di dalam workspace.",
    tip: "Kai memindai vulnerability, sanitasi input, dan audit keamanan berlapis.",
  },
  ren: {
    greeting: "Halo Bos Muda! Semuanya berjalan sesuai standar kualitas tinggi.",
    quote: "329 test suite otomatis kita (security, architecture, AAA, BVA, ASVS) semuanya lulus 100% tanpa error sama sekali!",
    tip: "Ren memastikan seluruh unit, integrasi, dan regression tests lulus sempurna.",
  },
};

const AGENTS = {
  risko: {
    name: "Risko",
    role: "Sang Dalang",
    title: "Master Orchestrator",
    color: 0x312e81, // Indigo Navy Blazer
    hex: "#4f46e5",
    accentColor: 0x818cf8,
    skinColor: 0xf5d0b5,
    hairColor: 0x1e1b4b,
    hairStyle: "pompadour",
    pos: [0, 0, 0],
    screenColor: 0x818cf8,
    action: "Memimpin orkestrasi & evaluasi lakon",
    hasGlasses: true,
    hasLanyard: true,
    personality: "Visioner, berwibawa, analitis tinggi",
    typingStyle: "commanding", // Ketukan mantap, sesekali jeda berpikir, anggukan kepala arsitektur
    speedFactor: 1.0,
  },
  pingot: {
    name: "Pingot",
    role: "Wayang Data",
    title: "Data Architect",
    color: 0x064e3b, // Forest Green Flannel
    hex: "#10b981",
    accentColor: 0x34d399,
    skinColor: 0xfcd34d,
    hairColor: 0x27272a,
    hairStyle: "fade",
    pos: [-3.8, 0, -2.5],
    screenColor: 0x34d399,
    action: "Audit skema & pipeline data",
    hasGlasses: true,
    hasLanyard: true,
    personality: "Metodis, tenang, kalkulatif & rapi",
    typingStyle: "methodical", // Ritmik stabil seperti metronom, tangan kiri di numpad, sesekali benerin kacamata
    speedFactor: 0.9,
  },
  zaki: {
    name: "Zaki",
    role: "Wayang Backend",
    title: "API & System Engineer",
    color: 0x78350f, // Warm Amber Hoodie
    hex: "#f59e0b",
    accentColor: 0xfbbf24,
    skinColor: 0xf5caa8,
    hairColor: 0x451a03,
    hairStyle: "curls",
    pos: [3.8, 0, -2.5],
    screenColor: 0xfbbf24,
    action: "Mengembangkan endpoint FastAPI & worker",
    hasHeadphones: true,
    hasLanyard: true,
    personality: "Enerjik, beat-driven, hacker sejati",
    typingStyle: "furious", // Mengetik super kilat, kepala mengangguk santai ikut irama lagu di headphone
    speedFactor: 1.45,
  },
  lulu: {
    name: "Lulu",
    role: "Wayang Visual",
    title: "UI/UX & 3D Designer",
    color: 0x831843, // Rose Burgundy Blouse
    hex: "#ec4899",
    accentColor: 0xf472b6,
    skinColor: 0xffedd5,
    hairColor: 0x4c0519,
    hairStyle: "ponytail",
    pos: [-3.8, 0, 3],
    screenColor: 0xf472b6,
    action: "Merancang antarmuka & estetika visual",
    hasGlasses: false,
    hasLanyard: true,
    personality: "Perfeksionis, estetik, peka mikro-interaksi",
    typingStyle: "perfectionist", // Tangan kanan sering bergerak luwes seperti pegang mouse/stylus pen
    speedFactor: 1.1,
  },
  mika: {
    name: "Mika",
    role: "Wayang Pujangga",
    title: "Technical Writer",
    color: 0x164e63, // Deep Cyan Cardigan
    hex: "#06b6d4",
    accentColor: 0x38bdf8,
    skinColor: 0xfde047,
    hairColor: 0x0f172a,
    hairStyle: "bob",
    pos: [3.8, 0, 3],
    screenColor: 0x38bdf8,
    action: "Menulis dokumentasi & standar sistem",
    hasGlasses: true,
    hasLanyard: true,
    personality: "Puitis, terstruktur, cermat merangkai kata",
    typingStyle: "poetic", // Ketukan mengalir lembut bergantian jemari, sesekali menengadah mencari diksi terbaik
    speedFactor: 0.95,
  },
  nova: {
    name: "Nova",
    role: "Wayang Patih",
    title: "DevOps & CI/CD",
    color: 0x7c2d12, // Rust Terracotta Polo
    hex: "#f97316",
    accentColor: 0xfb923c,
    skinColor: 0xf87171,
    hairColor: 0x18181b,
    hairStyle: "buzz",
    pos: [0, 0, -5.5],
    screenColor: 0xfb923c,
    action: "Pipeline CI/CD & deployment cloud",
    hasSmartwatch: true,
    hasLanyard: true,
    personality: "Tegas, gesit, waspada latensi server",
    typingStyle: "frantic", // Mengetik cepat dalam burst kilat, sering melirik smartwatch di pergelangan tangan
    speedFactor: 1.35,
  },
  kai: {
    name: "Kai",
    role: "Wayang Senopati",
    title: "Security Auditor",
    color: 0x7f1d1d, // Dark Crimson Bomber
    hex: "#ef4444",
    accentColor: 0xf87171,
    skinColor: 0xfcd34d,
    hairColor: 0x09090b,
    hairStyle: "sidepart",
    pos: [-7.2, 0, 0],
    screenColor: 0xf87171,
    action: "Audit keamanan OWASP & token gate",
    hasGlasses: false,
    hasLanyard: true,
    personality: "Waspada, tajam, pemburu celah vulnerabilitas",
    typingStyle: "hyperfocused", // Badan membungkuk intens mendekati layar, tatapan tajam, ketukan tajam terarah
    speedFactor: 1.2,
  },
  ren: {
    name: "Ren",
    role: "Wayang Jaksa",
    title: "QA & Test Automation",
    color: 0x4c1d95, // Deep Violet Denim
    hex: "#8b5cf6",
    accentColor: 0xa78bfa,
    skinColor: 0xfed7aa,
    hairColor: 0x1e1b4b,
    hairStyle: "parted",
    pos: [7.2, 0, 0],
    screenColor: 0xa78bfa,
    action: "Menjalankan 182 test suite otomatis",
    hasGlasses: true,
    hasLanyard: true,
    personality: "Kritis, teliti, zero-tolerance bug",
    typingStyle: "rhythmic", // Mengetik dengan ritme audit tegas, sesekali mengangguk saat assertion pass
    speedFactor: 1.15,
  },
};

// ==========================================
// 🏢 HIGH-TECH PROCEDURAL TEXTURES (Silicon Valley Enterprise Standard)
// ==========================================

// 1. Polished Architectural Terrazzo Concrete Floor
function createTerrazzoFloorTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 1024;
  const ctx = canvas.getContext("2d");

  // Deep Obsidian / Slate Micro-Cement Base
  ctx.fillStyle = "#121418";
  ctx.fillRect(0, 0, 1024, 1024);

  // Micro stone aggregates & quartz specks
  const speckColors = ["#1a1d24", "#252932", "#2e3440", "#384152", "#475569", "#1e222b"];
  for (let i = 0; i < 2800; i++) {
    const rx = Math.random() * 1024;
    const ry = Math.random() * 1024;
    const size = Math.random() * 2.8 + 0.8;
    ctx.fillStyle = speckColors[Math.floor(Math.random() * speckColors.length)];
    ctx.beginPath();
    ctx.arc(rx, ry, size, 0, Math.PI * 2);
    ctx.fill();
  }

  // 256x256 Large Architectural Tile Grid & Expansion Seams
  const tileSize = 256;
  ctx.lineWidth = 1.5;
  for (let x = 0; x <= 1024; x += tileSize) {
    ctx.strokeStyle = "rgba(255, 255, 255, 0.055)";
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, 1024);
    ctx.stroke();

    ctx.strokeStyle = "rgba(0, 0, 0, 0.5)";
    ctx.beginPath();
    ctx.moveTo(x + 1, 0);
    ctx.lineTo(x + 1, 1024);
    ctx.stroke();
  }

  for (let y = 0; y <= 1024; y += tileSize) {
    ctx.strokeStyle = "rgba(255, 255, 255, 0.055)";
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(1024, y);
    ctx.stroke();

    ctx.strokeStyle = "rgba(0, 0, 0, 0.5)";
    ctx.beginPath();
    ctx.moveTo(0, y + 1);
    ctx.lineTo(1024, y + 1);
    ctx.stroke();
  }

  // Brass Inlay Crosses at Tile Intersections
  for (let x = tileSize; x < 1024; x += tileSize) {
    for (let y = tileSize; y < 1024; y += tileSize) {
      ctx.fillStyle = "rgba(212, 175, 55, 0.55)";
      ctx.fillRect(x - 4, y - 1, 9, 2);
      ctx.fillRect(x - 1, y - 4, 2, 9);
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(2, 2);
  return texture;
}

// 2. Vertical Walnut Acoustic Slat Baffle Texture
function createWalnutSlatTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  // Acoustic black felt backing
  ctx.fillStyle = "#0a0b0e";
  ctx.fillRect(0, 0, 512, 512);

  const slatW = 20;
  const gap = 8;
  const total = slatW + gap;

  for (let x = 0; x < 512; x += total) {
    // Slat wood gradient
    const grad = ctx.createLinearGradient(x, 0, x + slatW, 0);
    grad.addColorStop(0, "#2d1c13");
    grad.addColorStop(0.3, "#3d271b");
    grad.addColorStop(0.7, "#482e20");
    grad.addColorStop(1, "#281810");
    ctx.fillStyle = grad;
    ctx.fillRect(x, 0, slatW, 512);

    // Subtle natural wood grain lines
    ctx.strokeStyle = "rgba(0, 0, 0, 0.15)";
    ctx.lineWidth = 1;
    for (let i = 0; i < 4; i++) {
      const gx = x + 3 + i * 4;
      ctx.beginPath();
      ctx.moveTo(gx, 0);
      ctx.lineTo(gx + (Math.sin(gx) * 2), 512);
      ctx.stroke();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(4, 1);
  return texture;
}

// 3. 42U Data Center Server Rack Faceplate Texture
function createServerRackTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 1024;
  const ctx = canvas.getContext("2d");

  // Matte Black Steel Rack Frame
  ctx.fillStyle = "#0c0d10";
  ctx.fillRect(0, 0, 512, 1024);

  // Outer Rack Rails
  ctx.fillStyle = "#1e2229";
  ctx.fillRect(0, 0, 36, 1024);
  ctx.fillRect(512 - 36, 0, 36, 1024);

  // Rack Unit Mounting Holes
  ctx.fillStyle = "#07080a";
  for (let y = 16; y < 1024; y += 22) {
    ctx.fillRect(14, y, 8, 8);
    ctx.fillRect(512 - 22, y, 8, 8);
  }

  // 1U, 2U, and 4U Server Blades
  let curY = 20;
  while (curY < 1000) {
    const uHeight = [24, 48, 72, 96][Math.floor(Math.random() * 4)];
    if (curY + uHeight > 1000) break;

    // Server chassis front
    const serverGrad = ctx.createLinearGradient(40, curY, 512 - 40, curY);
    serverGrad.addColorStop(0, "#15181f");
    serverGrad.addColorStop(0.5, "#1f242d");
    serverGrad.addColorStop(1, "#15181f");
    ctx.fillStyle = serverGrad;
    ctx.fillRect(40, curY, 512 - 80, uHeight - 2);

    // Bevel edge
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.strokeRect(40, curY, 512 - 80, uHeight - 2);

    // Ventilation honeycomb mesh on left
    ctx.fillStyle = "rgba(0, 0, 0, 0.65)";
    ctx.fillRect(48, curY + 4, 160, uHeight - 10);

    // Drive bays or telemetry LED cluster on right
    const ledX = 512 - 120;
    const ledCount = Math.floor((uHeight - 10) / 10);
    for (let l = 0; l < ledCount; l++) {
      const ly = curY + 6 + l * 10;
      // Activity LEDs (mostly green/cyan, occasional amber/blue)
      const colors = ["#10b981", "#06b6d4", "#10b981", "#3b82f6", "#f59e0b"];
      ctx.fillStyle = colors[(l + curY) % colors.length];
      ctx.fillRect(ledX, ly, 6, 4);
      ctx.fillRect(ledX + 12, ly, 6, 4);
      ctx.fillRect(ledX + 24, ly, 6, 4);
    }

    curY += uHeight + 2;
  }

  return new THREE.CanvasTexture(canvas);
}

// 4. Frosted Dusted Crystal Glass Privacy Band (Standard in Apple/Stripe HQs)
function createPrivacyFilmTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 256;
  const ctx = canvas.getContext("2d");

  // Transparent clear glass background
  ctx.clearRect(0, 0, 512, 256);

  // Center frosted gradient band
  const bandGrad = ctx.createLinearGradient(0, 0, 0, 256);
  bandGrad.addColorStop(0, "rgba(210, 230, 255, 0.0)");
  bandGrad.addColorStop(0.2, "rgba(210, 230, 255, 0.35)");
  bandGrad.addColorStop(0.5, "rgba(210, 230, 255, 0.65)");
  bandGrad.addColorStop(0.8, "rgba(210, 230, 255, 0.35)");
  bandGrad.addColorStop(1, "rgba(210, 230, 255, 0.0)");
  ctx.fillStyle = bandGrad;
  ctx.fillRect(0, 0, 512, 256);

  // Micro dot-matrix architectural pattern inside band
  ctx.fillStyle = "rgba(255, 255, 255, 0.45)";
  for (let x = 8; x < 512; x += 16) {
    for (let y = 64; y < 192; y += 16) {
      ctx.beginPath();
      ctx.arc(x, y, 1.8, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.repeat.set(6, 1);
  return texture;
}

// 5. Procedural Tech Acoustic Area Rug Texture
function createRugTexture(baseColorHex, patternColorHex) {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = baseColorHex;
  ctx.fillRect(0, 0, 512, 512);

  // Minimalist technical grid & borders
  ctx.strokeStyle = patternColorHex;
  ctx.lineWidth = 1.5;
  for (let i = 0; i <= 512; i += 64) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i, 512);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, i);
    ctx.lineTo(512, i);
    ctx.stroke();
  }

  ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
  ctx.lineWidth = 6;
  ctx.strokeRect(6, 6, 500, 500);

  return new THREE.CanvasTexture(canvas);
}

// 4. Procedural 75" 4K Presentation Display Texture for Meeting Room
function createMeetingScreenTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 576;
  const ctx = canvas.getContext("2d");

  // Deep tech gradient background
  const bgGrad = ctx.createLinearGradient(0, 0, 1024, 576);
  bgGrad.addColorStop(0, "#090d16");
  bgGrad.addColorStop(1, "#0f172a");
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, 1024, 576);

  // Grid
  ctx.strokeStyle = "rgba(56, 189, 248, 0.08)";
  ctx.lineWidth = 1;
  for (let x = 0; x < 1024; x += 40) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, 576);
    ctx.stroke();
  }
  for (let y = 0; y < 576; y += 40) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(1024, y);
    ctx.stroke();
  }

  // Top header bar
  ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
  ctx.fillRect(36, 24, 952, 68);
  ctx.strokeStyle = "rgba(56, 189, 248, 0.35)";
  ctx.lineWidth = 2;
  ctx.strokeRect(36, 24, 952, 68);

  ctx.fillStyle = "#38bdf8";
  ctx.font = "bold 28px system-ui, sans-serif";
  ctx.fillText("🎭 DALANG-AI • SPRINT ALL-HANDS SYNC", 60, 68);

  ctx.fillStyle = "#10b981";
  ctx.font = "bold 17px system-ui, sans-serif";
  ctx.fillText("● LIVE IN MEETING ROOM", 730, 68);

  // Left card: Sprint metrics
  ctx.fillStyle = "rgba(30, 41, 59, 0.75)";
  ctx.fillRect(36, 110, 460, 430);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
  ctx.strokeRect(36, 110, 460, 430);

  ctx.fillStyle = "#f8fafc";
  ctx.font = "bold 22px system-ui, sans-serif";
  ctx.fillText("Sprint 8: Full Autonomous", 60, 150);

  ctx.fillStyle = "#94a3b8";
  ctx.font = "16px system-ui, sans-serif";
  ctx.fillText("Status: v1.0.0 Stable Deployment", 60, 185);
  ctx.fillText("Velocity: 98.4% (Optimal Output)", 60, 215);
  ctx.fillText("Active Wayang: 8 Agents Ready", 60, 245);
  ctx.fillText("Unit Tests: 182 / 182 Passing (100%)", 60, 275);
  ctx.fillText("Security: Zero-Defect Enforced", 60, 305);

  // Progress Bar
  ctx.fillStyle = "#1e293b";
  ctx.fillRect(60, 345, 410, 26);
  ctx.fillStyle = "#38bdf8";
  ctx.fillRect(60, 345, 395, 26);
  ctx.fillStyle = "#0f172a";
  ctx.font = "bold 13px system-ui, sans-serif";
  ctx.fillText("96.5% SPRINT BURNDOWN REACHED", 140, 363);

  // Quote
  ctx.fillStyle = "#cbd5e1";
  ctx.font = "italic 14px system-ui, sans-serif";
  ctx.fillText('"Karya Anak Bangsa — Bebas Modif & Non-Komersial"', 60, 420);
  ctx.fillStyle = "#64748b";
  ctx.font = "13px system-ui, sans-serif";
  ctx.fillText("Dalang Master Orchestrator • Auto Router • Academy", 60, 450);

  // Right card: Agenda & Speaker
  ctx.fillStyle = "rgba(30, 41, 59, 0.75)";
  ctx.fillRect(520, 110, 468, 430);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
  ctx.strokeRect(520, 110, 468, 430);

  ctx.fillStyle = "#f8fafc";
  ctx.font = "bold 22px system-ui, sans-serif";
  ctx.fillText("Agenda Rapat & Diskusi", 545, 150);

  const items = [
    "1. Risko (Dalang): Evaluasi Lakon & Roadmap",
    "2. Lulu: Review Visual 3D Isometrik & Humanoid",
    "3. Zaki: Optimasi Frontend 60FPS Three.js Loop",
    "4. Nova: Pipeline Docker & Pre-commit Lint Guard",
    "5. Kai: Security Penetration & OWASP Review",
    "6. Ren: QA Regression & 182 Passing Tests",
    "7. Sesi Tanya Jawab & Coffee Break di Pantry",
  ];
  items.forEach((item, idx) => {
    ctx.fillStyle = idx === 0 ? "#38bdf8" : "#cbd5e1";
    ctx.font = (idx === 0 ? "bold " : "") + "15px system-ui, sans-serif";
    ctx.fillText(item, 545, 195 + idx * 36);
  });

  const texture = new THREE.CanvasTexture(canvas);
  texture.anisotropy = 16;
  return texture;
}

// 5. Office Waypoints and Key Location Coordinates
const DESK_SPOTS = {
  risko: { pos: [0, 0, 0.58], rotY: 0 },
  pingot: { pos: [-3.8, 0, -1.92], rotY: 0 },
  zaki: { pos: [3.8, 0, -1.92], rotY: 0 },
  lulu: { pos: [-3.8, 0, 3.58], rotY: 0 },
  mika: { pos: [3.8, 0, 3.58], rotY: 0 },
  nova: { pos: [0, 0, -4.92], rotY: 0 },
  kai: { pos: [-7.2, 0, 0.58], rotY: 0 },
  ren: { pos: [7.2, 0, 0.58], rotY: 0 },
};

const LOCATION_SPOTS = {
  WORK: DESK_SPOTS,
  DESK: DESK_SPOTS,
  MEETING: {
    risko: { pos: [14.5, 0, -3.4], rotY: Math.PI },
    pingot: { pos: [12.9, 0, -4.8], rotY: -Math.PI / 2 },
    zaki: { pos: [12.9, 0, -6.5], rotY: -Math.PI / 2 },
    lulu: { pos: [12.9, 0, -8.2], rotY: -Math.PI / 2 },
    mika: { pos: [16.1, 0, -4.8], rotY: Math.PI / 2 },
    nova: { pos: [16.1, 0, -6.5], rotY: Math.PI / 2 },
    kai: { pos: [16.1, 0, -8.2], rotY: Math.PI / 2 },
    ren: { pos: [14.5, 0, -9.6], rotY: 0 },
  },
  LOUNGE: {
    risko: { pos: [7.2, 0, 7.1], rotY: 0 },
    lulu: { pos: [8.5, 0, 7.1], rotY: 0 },
    pingot: { pos: [9.7, 0, 7.1], rotY: 0 },
    zaki: { pos: [9.8, 0, 5.7], rotY: -Math.PI / 2 },
    mika: { pos: [6.4, 0, 6.0], rotY: Math.PI / 4 },
    nova: { pos: [10.8, 0, 7.7], rotY: -Math.PI / 3 },
    kai: { pos: [7.6, 0, 5.2], rotY: Math.PI },
    ren: { pos: [8.8, 0, 5.2], rotY: Math.PI },
  },
  PANTRY: {
    risko: { pos: [-11.2, 0, -5.8], rotY: 0 },
    pingot: { pos: [-12.8, 0, -5.8], rotY: 0 },
    lulu: { pos: [-13.4, 0, -5.8], rotY: 0 },
    zaki: { pos: [-10.2, 0, -5.8], rotY: 0 },
    mika: { pos: [-14.2, 0, -5.8], rotY: 0 },
    nova: { pos: [-9.6, 0, -5.8], rotY: 0 },
    kai: { pos: [-12.0, 0, -4.6], rotY: 0 },
    ren: { pos: [-13.2, 0, -4.6], rotY: 0 },
  },
};

function getWaypoints(startPos, endPos) {
  const wps = [];
  const sx = startPos.x;
  const sz = startPos.z;
  const ex = endPos.x;
  const ez = endPos.z;

  // Clear vertical aisle lines:
  // -5.4 (West), -1.8 (Mid-West), 1.8 (Mid-East), 5.5 (East), 10.5 (Meeting corridor)
  const AISLES_X = [-5.4, -1.8, 1.8, 5.5, 10.5];
  const findAisle = (x) => {
    let best = AISLES_X[0];
    let minD = Math.abs(x - best);
    for (let i = 1; i < AISLES_X.length; i++) {
      const d = Math.abs(x - AISLES_X[i]);
      if (d < minD) { minD = d; best = AISLES_X[i]; }
    }
    return best;
  };

  const isStartInMeeting = sx > 12.0;
  const isEndInMeeting = ex > 12.0;

  // 1. Moving OUT of Meeting Room to Main Office
  if (isStartInMeeting && !isEndInMeeting) {
    // Walk to conference doorway corridor
    wps.push(new THREE.Vector3(14.5, 0, -1.5));
    wps.push(new THREE.Vector3(14.5, 0, 0));
    wps.push(new THREE.Vector3(11.5, 0, 0)); // Through sliding doorway

    const targetAisleX = findAisle(ex);
    wps.push(new THREE.Vector3(targetAisleX, 0, 0));
    // Walk down vertical aisle to target row, then step into target chair
    if (Math.abs(ez) > 0.4) {
      wps.push(new THREE.Vector3(targetAisleX, 0, ez > 0 ? ez + 0.6 : ez - 0.6));
    }
    wps.push(new THREE.Vector3(ex, 0, ez));
    return wps;
  }

  // 2. Moving INTO Meeting Room from Main Office
  if (!isStartInMeeting && isEndInMeeting) {
    const startAisleX = findAisle(sx);
    // Step back from desk/chair into aisle
    if (Math.abs(sz) > 0.4) {
      wps.push(new THREE.Vector3(sx, 0, sz > 0 ? sz + 0.6 : sz - 0.6));
    }
    wps.push(new THREE.Vector3(startAisleX, 0, sz > 0 ? sz + 0.6 : sz - 0.6));
    wps.push(new THREE.Vector3(startAisleX, 0, 0)); // Main horizontal hallway
    wps.push(new THREE.Vector3(11.5, 0, 0));        // Doorway threshold
    wps.push(new THREE.Vector3(14.5, 0, 0));        // Inside meeting room
    wps.push(new THREE.Vector3(14.5, 0, -1.5));
    // Final seat approach
    wps.push(new THREE.Vector3(ex, 0, ez));
    return wps;
  }

  // 3. Main Office internal movement (e.g. Desk <-> Lounge <-> Pantry)
  const startAisleX = findAisle(sx);
  const targetAisleX = findAisle(ex);

  // Step back from current station
  if (Math.abs(sz) > 0.4) {
    wps.push(new THREE.Vector3(sx, 0, sz > 0 ? sz + 0.6 : sz - 0.6));
  }
  wps.push(new THREE.Vector3(startAisleX, 0, sz > 0 ? sz + 0.6 : sz - 0.6));
  wps.push(new THREE.Vector3(startAisleX, 0, 1.8)); // Cross corridor
  wps.push(new THREE.Vector3(targetAisleX, 0, 1.8));

  if (Math.abs(ez - 1.8) > 0.5) {
    wps.push(new THREE.Vector3(targetAisleX, 0, ez > 1.8 ? ez + 0.5 : ez - 0.5));
  }
  wps.push(new THREE.Vector3(ex, 0, ez));
  return wps;
}


// Procedural Whiteboard Diagram Texture
function createWhiteboardTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, 1024, 512);

  // Grid
  ctx.strokeStyle = "#f1f5f9";
  ctx.lineWidth = 1;
  for (let x = 0; x < 1024; x += 32) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, 512);
    ctx.stroke();
  }
  for (let y = 0; y < 512; y += 32) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(1024, y);
    ctx.stroke();
  }

  // Header Title
  ctx.fillStyle = "#0f172a";
  ctx.font = "bold 32px system-ui, sans-serif";
  ctx.fillText("🎭 DALANG-AI • SYSTEM ARCHITECTURE & ROADMAP", 48, 64);

  // Diagram Boxes
  const drawBox = (x, y, w, h, title, subtitle, color) => {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 3;
    ctx.strokeRect(x, y, w, h);
    ctx.fillStyle = "#0f172a";
    ctx.font = "bold 18px system-ui, sans-serif";
    ctx.fillText(title, x + 16, y + 32);
    ctx.font = "14px system-ui, sans-serif";
    ctx.fillStyle = "#475569";
    ctx.fillText(subtitle, x + 16, y + 54);
  };

  drawBox(48, 120, 220, 80, "SANG DALANG", "Master Orchestrator", "#e0e7ff");
  drawBox(310, 120, 220, 80, "AUTO PLANNER", "Freeform Decomposer", "#dcfce7");
  drawBox(570, 120, 220, 80, "WAYANG ROUTER", "Autonomous Dispatcher", "#fef3c7");
  drawBox(830, 120, 160, 80, "ACADEMY", "Skill Upgrades", "#fce7f3");

  // Connectors
  ctx.strokeStyle = "#6366f1";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(268, 160);
  ctx.lineTo(310, 160);
  ctx.moveTo(530, 160);
  ctx.lineTo(570, 160);
  ctx.moveTo(790, 160);
  ctx.lineTo(830, 160);
  ctx.stroke();

  // Kanban / Sticky Notes
  const drawSticky = (x, y, text, color) => {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, 110, 75);
    ctx.strokeStyle = "rgba(0,0,0,0.15)";
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, 110, 75);
    ctx.fillStyle = "#1e293b";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.fillText(text, x + 10, y + 42);
  };

  drawSticky(48, 260, "182 TESTS PASS", "#fef08a");
  drawSticky(178, 260, "NON-COMMERCIAL", "#bbf7d0");
  drawSticky(310, 260, "FASTAPI :8765", "#bae6fd");
  drawSticky(440, 260, "THREE.JS :5173", "#fed7aa");
  drawSticky(570, 260, "NO VNC READY", "#fbcfe8");
  drawSticky(700, 260, "ARMBIAN VPS", "#e9d5ff");

  // Bottom notes
  ctx.fillStyle = "#334155";
  ctx.font = "italic 16px system-ui, sans-serif";
  ctx.fillText("✓ Autonomous Multi-Agent System | Karya Anak Bangsa | Lisensi Bebas Non-Komersial", 48, 440);

  return new THREE.CanvasTexture(canvas);
}

export default function App() {
  const [officeMode, setOfficeMode] = useState("WORK");
  useEffect(() => { window.__officeMode = officeMode; }, [officeMode]);
  const [agentModes, setAgentModes] = useState({
    risko: "WORK",
    pingot: "WORK",
    zaki: "WORK",
    lulu: "WORK",
    mika: "WORK",
    nova: "WORK",
    kai: "WORK",
    ren: "WORK",
  });
  const agentNavRef = useRef(null);

  const mountRef = useRef(null);
  const [events, setEvents] = useState([]);
  const [agentStatus, setAgentStatus] = useState({});
  const [activeTask, setActiveTask] = useState(null);
  const [connected, setConnected] = useState(false);
  const [workingMap, setWorkingMap] = useState({});

    const [taskInput, setTaskInput] = useState("");
  const [targetAgent, setTargetAgent] = useState("auto");
  const [isDispatching, setIsDispatching] = useState(false);
  const [selectedAgentDetail, setSelectedAgentDetail] = useState(null);
  const [cameraMode, setCameraMode] = useState("player"); // 'player' | 'orbit'
  const cameraModeRef = useRef("player");
  const [nearAgent, setNearAgent] = useState(null);
  const nearAgentRef = useRef(null);
  const [mingleModalAgent, setMingleModalAgent] = useState(null);
  const playerRef = useRef(null);
  const keysPressedRef = useRef({ w: false, a: false, s: false, d: false, up: false, down: false, left: false, right: false, shift: false });
  const activeWayangCount = Object.values(workingMap).filter(Boolean).length;
  const sceneRef = useRef(null);
  const agentMeshesRef = useRef({});

  // 1. Setup Three.js Cinematic Studio
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0e1320);
    scene.fog = new THREE.FogExp2(0x0e1320, 0.012);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(24, 25, 29);
    camera.lookAt(1.5, 1.2, 0);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance",
      preserveDrawingBuffer: true,
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.18;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    // GLTF Model Loader for Real 3D Characters
    // GLTF Loader ready
    // const gltfLoader = new GLTFLoader();
    const mixers = [];
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2.15;
    controls.minDistance = 8;
    controls.maxDistance = 60;
    controls.target.set(0, 1.2, 0);

    // ==========================================
    // 💡 THREE-POINT CINEMATIC PBR LIGHTING
    // ==========================================
    // 1. Warm Golden Daylight Sun (Key Light)
    const sunLight = new THREE.DirectionalLight(0xfff5e6, 2.5);
    sunLight.position.set(22, 34, 20);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 1024;
    sunLight.shadow.mapSize.height = 1024;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 80;
    sunLight.shadow.camera.left = -25;
    sunLight.shadow.camera.right = 25;
    sunLight.shadow.camera.top = 25;
    sunLight.shadow.camera.bottom = -25;
    sunLight.shadow.bias = -0.0003;
    scene.add(sunLight);

    // 2. Soft Ambient Fill
    const ambientLight = new THREE.AmbientLight(0xdbeafe, 1.05);
    scene.add(ambientLight);

    // 3. Cool Edge Backlight
    const rimLight = new THREE.DirectionalLight(0x7dd3fc, 0.85);
    rimLight.position.set(-22, 18, -20);
    scene.add(rimLight);

    // 4. Warm Interior Pendants (Cozy Office Glow)
    const interiorGlow = new THREE.PointLight(0xfef08a, 1.3, 22);
    interiorGlow.position.set(0, 6.5, 0);
    scene.add(interiorGlow);

    // ==========================================
    // 🏢 REAL MODERN OFFICE ROOM (Complete Architectural Studio)
    // ==========================================
    const roomGroup = new THREE.Group();

    // 1. High-Tech Polished Terrazzo Concrete Floor
    const terrazzoTexture = createTerrazzoFloorTexture();
    const floorGeo = new THREE.PlaneGeometry(32, 28);
    const floorMat = new THREE.MeshStandardMaterial({
      map: terrazzoTexture,
      roughness: 0.38,
      metalness: 0.08,
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    roomGroup.add(floor);

    // 2. Central Engineering Acoustic Felt Inlay / Rug
    const rugTexture = createRugTexture("#111317", "rgba(99, 102, 241, 0.16)");
    const rugGeo = new THREE.PlaneGeometry(18, 14);
    const rugMat = new THREE.MeshStandardMaterial({
      map: rugTexture,
      roughness: 0.95,
      metalness: 0.0,
    });
    const rug = new THREE.Mesh(rugGeo, rugMat);
    rug.rotation.x = -Math.PI / 2;
    rug.position.set(0, 0.015, 0);
    rug.receiveShadow = true;
    roomGroup.add(rug);

    // 2B. Conference Room Smoked Walnut Floor Inlay
    const confFloorGeo = new THREE.PlaneGeometry(7.8, 11.6);
    const confFloorMat = new THREE.MeshStandardMaterial({
      color: 0x1a120d,
      roughness: 0.45,
      metalness: 0.05,
    });
    const confFloor = new THREE.Mesh(confFloorGeo, confFloorMat);
    confFloor.rotation.x = -Math.PI / 2;
    confFloor.position.set(14.5, 0.012, -6.5);
    confFloor.receiveShadow = true;
    roomGroup.add(confFloor);

    // 3. Back Wall with Architectural Walnut Acoustic Slat Baffles
    const slatTexture = createWalnutSlatTexture();
    const backWallGeo = new THREE.BoxGeometry(32, 5.8, 0.4);
    const slatWallMat = new THREE.MeshStandardMaterial({
      map: slatTexture,
      roughness: 0.65,
      metalness: 0.02,
    });
    const backWall = new THREE.Mesh(backWallGeo, slatWallMat);
    backWall.position.set(0, 2.9, -14);
    backWall.receiveShadow = true;
    roomGroup.add(backWall);

    // Architectural Recessed LED Cove Lighting (Washes down the walnut slats)
    const coveLightGeo = new THREE.BoxGeometry(31.6, 0.05, 0.22);
    const coveLightMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: 0xfff7ed,
      emissiveIntensity: 2.2,
      roughness: 0.2,
    });
    const coveLight = new THREE.Mesh(coveLightGeo, coveLightMat);
    coveLight.position.set(0, 5.68, -13.7);
    roomGroup.add(coveLight);

    // Soft cove downlight wash
    [-10, 0, 10].forEach((lx) => {
      const washLight = new THREE.PointLight(0xfef3c7, 0.75, 7, 2);
      washLight.position.set(lx, 5.5, -13.5);
      roomGroup.add(washLight);
    });

    // Left Wall with Industrial Curtain Wall Daylight Windows
    const leftWallMat = new THREE.MeshStandardMaterial({ color: 0x0f1115, roughness: 0.85 });
    const leftWallGeo = new THREE.BoxGeometry(0.4, 5.8, 28);
    const leftWall = new THREE.Mesh(leftWallGeo, leftWallMat);
    leftWall.position.set(-16, 2.9, 0);
    leftWall.receiveShadow = true;
    roomGroup.add(leftWall);

    // Baseboards (Matte Black Anodized Aluminum)
    const baseboardGeo = new THREE.BoxGeometry(32, 0.2, 0.45);
    const baseboardMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.85, roughness: 0.2 });
    const baseboard = new THREE.Mesh(baseboardGeo, baseboardMat);
    baseboard.position.set(0, 0.1, -13.8);
    roomGroup.add(baseboard);

    // Large Daylight Windows on Left Wall
    const windowFrameGeo = new THREE.BoxGeometry(0.3, 3.4, 12);
    const windowFrameMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.85, roughness: 0.25 });
    const windowFrame = new THREE.Mesh(windowFrameGeo, windowFrameMat);
    windowFrame.position.set(-15.8, 3.3, 0);
    roomGroup.add(windowFrame);

    const glassPaneGeo = new THREE.PlaneGeometry(11.6, 3.0);
    const glassPaneMat = new THREE.MeshStandardMaterial({
      color: 0xbae6fd,
      emissive: 0x38bdf8,
      emissiveIntensity: 0.65,
      roughness: 0.08,
    });
    const glassPane = new THREE.Mesh(glassPaneGeo, glassPaneMat);
    glassPane.rotation.y = Math.PI / 2;
    glassPane.position.set(-15.7, 3.3, 0);
    roomGroup.add(glassPane);

    // ==========================================
    // 🌐 4. GLASS-ENCLOSED SERVER ROOM & DATA CENTER CORE (High-Tech Feature)
    // ==========================================
    const serverCoreGroup = new THREE.Group();
    serverCoreGroup.position.set(-11.5, 0, -11.8);

    // Glass Enclosure Partitions for Server Room
    const serverGlassMat = new THREE.MeshPhysicalMaterial({
      color: 0x06b6d4,
      transmission: 0.82,
      opacity: 0.45,
      transparent: true,
      roughness: 0.1,
      metalness: 0.1,
      ior: 1.5,
    });

    // Server room front glass wall
    const sFrontGlass = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.4, 0.06), serverGlassMat);
    sFrontGlass.position.set(0, 2.7, 2.2);
    serverCoreGroup.add(sFrontGlass);

    // Server room side glass partition
    const sSideGlass = new THREE.Mesh(new THREE.BoxGeometry(0.06, 5.4, 4.4), serverGlassMat);
    sSideGlass.position.set(2.1, 2.7, 0);
    serverCoreGroup.add(sSideGlass);

    // Black Steel Structural Corner Posts
    const postMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.88, roughness: 0.2 });
    [[-2.1, 2.2], [2.1, 2.2], [2.1, -2.2]].forEach(([px, pz]) => {
      const pMesh = new THREE.Mesh(new THREE.BoxGeometry(0.12, 5.5, 0.12), postMat);
      pMesh.position.set(px, 2.75, pz);
      serverCoreGroup.add(pMesh);
    });

    // 42U Server Racks (2 Units side by side)
    const serverRackTex = createServerRackTexture();
    const rackMat = new THREE.MeshStandardMaterial({
      map: serverRackTex,
      metalness: 0.85,
      roughness: 0.25,
    });

    [-0.75, 0.75].forEach((rx) => {
      const rack = new THREE.Mesh(new THREE.BoxGeometry(1.05, 2.35, 1.1), rackMat);
      rack.position.set(rx, 1.175, 0);
      rack.castShadow = true;
      serverCoreGroup.add(rack);

      // Top exhaust cooling fan unit
      const fanTop = new THREE.Mesh(
        new THREE.BoxGeometry(0.95, 0.08, 1.0),
        new THREE.MeshStandardMaterial({ color: 0x1e2229, metalness: 0.9 })
      );
      fanTop.position.set(rx, 2.39, 0);
      serverCoreGroup.add(fanTop);
    });

    // Overhead Cable Ladder Raceway & Fiber Optic Duct
    const cableTray = new THREE.Mesh(
      new THREE.BoxGeometry(3.8, 0.1, 0.45),
      new THREE.MeshStandardMaterial({ color: 0xeab308, metalness: 0.5, roughness: 0.3 }) // Yellow fiber tray
    );
    cableTray.position.set(0, 3.8, 0);
    serverCoreGroup.add(cableTray);

    // Steel Ladder Bridge running into office
    const ladderBridge = new THREE.Mesh(
      new THREE.BoxGeometry(0.4, 0.08, 4.5),
      new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.9, roughness: 0.2 })
    );
    ladderBridge.position.set(0, 3.8, 4.4);
    serverCoreGroup.add(ladderBridge);

    // Cool Cyber Cyan Ambient Glow from Server Core
    const serverGlow = new THREE.PointLight(0x06b6d4, 2.4, 9, 2);
    serverGlow.position.set(0, 2.2, 0.5);
    serverCoreGroup.add(serverGlow);

    // Telemetry Status Screen inside server room
    const sStatusCanvas = document.createElement("canvas");
    sStatusCanvas.width = 512;
    sStatusCanvas.height = 256;
    const sCtx = sStatusCanvas.getContext("2d");
    sCtx.fillStyle = "#030712";
    sCtx.fillRect(0, 0, 512, 256);
    sCtx.fillStyle = "#10b981";
    sCtx.font = "bold 28px monospace";
    sCtx.fillText("● CORE TELEMETRY: ONLINE", 24, 48);
    sCtx.fillStyle = "#38bdf8";
    sCtx.font = "20px monospace";
    sCtx.fillText("CLUSTER: DALANG CLOUD • 8 NODES", 24, 95);
    sCtx.fillText("P99 LATENCY: 1.8ms  |  PUE: 1.08", 24, 135);
    sCtx.fillText("ACTIVE THREADS: 182 | RAM: 32GB", 24, 175);
    sCtx.fillStyle = "#a855f7";
    sCtx.fillText("FASTAPI :8765  •  VITE :5173", 24, 215);

    const sStatusTex = new THREE.CanvasTexture(sStatusCanvas);
    const sStatusMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(1.4, 0.7),
      new THREE.MeshStandardMaterial({
        map: sStatusTex,
        emissive: 0xffffff,
        emissiveMap: sStatusTex,
        emissiveIntensity: 0.9,
      })
    );
    sStatusMesh.position.set(2.05, 2.2, 0);
    sStatusMesh.rotation.y = -Math.PI / 2;
    serverCoreGroup.add(sStatusMesh);

    roomGroup.add(serverCoreGroup);

    // ==========================================
    // 🏛️ 5. EXECUTIVE WAR ROOM / CONFERENCE SUITE
    // ==========================================
    const privacyTexture = createPrivacyFilmTexture();
    const officeGlassMat = new THREE.MeshPhysicalMaterial({
      color: 0xecfeff,
      transmission: 0.88,
      opacity: 0.35,
      transparent: true,
      roughness: 0.1,
      ior: 1.5,
      thickness: 0.1,
    });

    // Glass Wall with Dusted Crystal Privacy Band
    const glassWallGeo1 = new THREE.BoxGeometry(0.08, 5.4, 8.0);
    const glassWall1 = new THREE.Mesh(glassWallGeo1, officeGlassMat);
    glassWall1.position.set(11.8, 2.7, -5.5);
    roomGroup.add(glassWall1);

    // Privacy Film Band on Glass
    const privacyBandGeo = new THREE.PlaneGeometry(8.0, 1.4);
    const privacyBandMat = new THREE.MeshStandardMaterial({
      map: privacyTexture,
      transparent: true,
      opacity: 0.75,
      roughness: 0.3,
    });
    const privacyBand = new THREE.Mesh(privacyBandGeo, privacyBandMat);
    privacyBand.rotation.y = Math.PI / 2;
    privacyBand.position.set(11.75, 2.5, -5.5);
    roomGroup.add(privacyBand);

    // Section 2: Glass Header above Doorway (z = -1.5 to 1.5, y = 3.8 to 5.4)
    const glassDoorHeaderGeo = new THREE.BoxGeometry(0.08, 1.6, 3.0);
    const glassDoorHeader = new THREE.Mesh(glassDoorHeaderGeo, officeGlassMat);
    glassDoorHeader.position.set(11.8, 4.6, 0);
    roomGroup.add(glassDoorHeader);

    // Top sliding rail for glass door
    const doorRailGeo = new THREE.BoxGeometry(0.12, 0.12, 3.2);
    const doorRailMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.85, roughness: 0.2 });
    const doorRail = new THREE.Mesh(doorRailGeo, doorRailMat);
    doorRail.position.set(11.8, 3.8, 0);
    roomGroup.add(doorRail);

    // Glass Wall Structural Mullions
    [-9.5, -5.5, -1.5, 1.5].forEach((pz) => {
      const postGeo = new THREE.BoxGeometry(0.14, 5.5, 0.14);
      const post = new THREE.Mesh(postGeo, doorRailMat);
      post.position.set(11.8, 2.75, pz);
      roomGroup.add(post);
    });

    // 5B. CONFERENCE MEETING ROOM INTERIOR
    // Monolithic Engineered Quartz & Walnut Conference Table
    const confTableGroup = new THREE.Group();
    confTableGroup.position.set(14.5, 0, -6.5);

    const confTableTopGeo = new THREE.BoxGeometry(1.7, 0.08, 5.2);
    const confTableMat = new THREE.MeshStandardMaterial({
      color: 0x221711, // Deep Smoked Walnut
      roughness: 0.35,
      metalness: 0.08,
    });
    const confTableTop = new THREE.Mesh(confTableTopGeo, confTableMat);
    confTableTop.position.y = 0.74;
    confTableTop.castShadow = true;
    confTableTop.receiveShadow = true;
    confTableGroup.add(confTableTop);

    // Undercut Chamfer Bevel on Tabletop
    const chamferGeo = new THREE.BoxGeometry(1.64, 0.02, 5.14);
    const chamferMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.9, roughness: 0.2 });
    const chamfer = new THREE.Mesh(chamferGeo, chamferMat);
    chamfer.position.y = 0.69;
    confTableGroup.add(chamfer);

    // Metal Sled Legs for Conference Table (Preserving clearance)
    const sledLegMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.88, roughness: 0.2 });
    [-1.7, 1.7].forEach((lz) => {
      const legFrame = new THREE.Group();
      legFrame.position.set(0, 0.35, lz);
      const bGeo = new THREE.BoxGeometry(1.9, 0.06, 0.08);
      const bMesh = new THREE.Mesh(bGeo, sledLegMat);
      bMesh.position.y = -0.32;
      legFrame.add(bMesh);
      [-0.85, 0.85].forEach((sx) => {
        const uGeo = new THREE.BoxGeometry(0.08, 0.7, 0.08);
        const uMesh = new THREE.Mesh(uGeo, sledLegMat);
        uMesh.position.set(sx, 0.03, 0);
        legFrame.add(uMesh);
      });
      confTableGroup.add(legFrame);
    });

    // Center Pop-up AV/Power Well with Cyan Accent Border
    const wellGeo = new THREE.BoxGeometry(0.38, 0.015, 1.8);
    const wellMat = new THREE.MeshStandardMaterial({
      color: 0x0a0c10,
      metalness: 0.9,
      roughness: 0.2,
      emissive: 0x06b6d4,
      emissiveIntensity: 0.45,
    });
    const wellMesh = new THREE.Mesh(wellGeo, wellMat);
    wellMesh.position.set(0, 0.785, 0);
    confTableGroup.add(wellMesh);

    roomGroup.add(confTableGroup);

    // 5C. Executive Swivel Chairs (Around the Table)
    const confChairGeo = new THREE.BoxGeometry(0.52, 0.08, 0.52);
    const confBackGeo = new THREE.BoxGeometry(0.5, 0.55, 0.06);
    const chairLeatherMat = new THREE.MeshStandardMaterial({ color: 0x181c24, roughness: 0.55 });
    const chairBaseMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.92, roughness: 0.2 });

    const createConfChair = (cx, cz, rotY) => {
      const chair = new THREE.Group();
      chair.position.set(cx, 0, cz);
      chair.rotation.y = rotY;

      const seat = new THREE.Mesh(confChairGeo, chairLeatherMat);
      seat.position.y = 0.46;
      seat.castShadow = true;
      chair.add(seat);

      const back = new THREE.Mesh(confBackGeo, chairLeatherMat);
      back.position.set(0, 0.74, 0.24);
      back.castShadow = true;
      chair.add(back);

      // Aluminum Armrests
      [-0.26, 0.26].forEach((ax) => {
        const armGeo = new THREE.BoxGeometry(0.04, 0.22, 0.32);
        const arm = new THREE.Mesh(armGeo, chairBaseMat);
        arm.position.set(ax, 0.62, 0.08);
        chair.add(arm);
      });

      const stemGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.42, 12);
      const stem = new THREE.Mesh(stemGeo, chairBaseMat);
      stem.position.y = 0.21;
      chair.add(stem);

      const baseGeo = new THREE.CylinderGeometry(0.32, 0.32, 0.04, 16);
      const base = new THREE.Mesh(baseGeo, chairBaseMat);
      base.position.y = 0.02;
      chair.add(base);

      return chair;
    };

    // West Chairs (facing East towards table)
    [-8.2, -6.5, -4.8].forEach((cz) => {
      roomGroup.add(createConfChair(12.9, cz, -Math.PI / 2));
    });
    // East Chairs (facing West towards table)
    [-8.2, -6.5, -4.8].forEach((cz) => {
      roomGroup.add(createConfChair(16.1, cz, Math.PI / 2));
    });
    // South Head Chair (Risko facing North)
    roomGroup.add(createConfChair(14.5, -3.4, Math.PI));
    // North Chair (Ren presenter area)
    roomGroup.add(createConfChair(14.5, -9.6, 0));

    // 5D. 85" Ultra-HD 4K Video Collaboration Wall
    const tvGroup = new THREE.Group();
    tvGroup.position.set(14.5, 3.1, -13.7);

    const tvFrameGeo = new THREE.BoxGeometry(4.2, 2.4, 0.12);
    const tvFrameMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.9, roughness: 0.2 });
    const tvFrame = new THREE.Mesh(tvFrameGeo, tvFrameMat);
    tvGroup.add(tvFrame);

    const tvScreenTex = createMeetingScreenTexture();
    const tvScreenGeo = new THREE.PlaneGeometry(4.08, 2.28);
    const tvScreenMat = new THREE.MeshStandardMaterial({
      map: tvScreenTex,
      emissive: 0xffffff,
      emissiveMap: tvScreenTex,
      emissiveIntensity: 0.9,
      roughness: 0.2,
    });
    const tvScreen = new THREE.Mesh(tvScreenGeo, tvScreenMat);
    tvScreen.position.z = 0.07;
    tvGroup.add(tvScreen);

    // Integrated Soundbar with 4K PTZ Camera Lens
    const soundbarGeo = new THREE.BoxGeometry(2.4, 0.14, 0.14);
    const soundbarMat = new THREE.MeshStandardMaterial({ color: 0x1e2229, metalness: 0.85 });
    const soundbar = new THREE.Mesh(soundbarGeo, soundbarMat);
    soundbar.position.set(0, -1.35, 0.08);
    tvGroup.add(soundbar);

    // Camera Lens Ring
    const lensGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.02, 16);
    const lensMat = new THREE.MeshStandardMaterial({ color: 0x06b6d4, emissive: 0x06b6d4, emissiveIntensity: 0.6 });
    const lens = new THREE.Mesh(lensGeo, lensMat);
    lens.rotation.x = Math.PI / 2;
    lens.position.set(0, -1.35, 0.16);
    tvGroup.add(lens);

    const meetingLight = new THREE.PointLight(0xbae6fd, 1.25, 9, 2);
    meetingLight.position.set(14.5, 4.8, -6.5);
    roomGroup.add(meetingLight);

    roomGroup.add(tvGroup);

    // 6. Large Architectural Glass Whiteboard with System Architecture
    const wbTexture = createWhiteboardTexture();
    const wbFrameGeo = new THREE.BoxGeometry(6.6, 3.4, 0.12);
    const wbFrameMat = new THREE.MeshStandardMaterial({ color: 0x1e2229, metalness: 0.85, roughness: 0.25 });
    const wbFrame = new THREE.Mesh(wbFrameGeo, wbFrameMat);
    wbFrame.position.set(0, 3.3, -13.75);
    roomGroup.add(wbFrame);

    const wbBoardGeo = new THREE.PlaneGeometry(6.4, 3.2);
    const wbBoardMat = new THREE.MeshBasicMaterial({ map: wbTexture });
    const wbBoard = new THREE.Mesh(wbBoardGeo, wbBoardMat);
    wbBoard.position.set(0, 3.3, -13.68);
    roomGroup.add(wbBoard);

    // Marker Tray & Pens
    const trayGeo = new THREE.BoxGeometry(3.5, 0.06, 0.2);
    const trayMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.85 });
    const tray = new THREE.Mesh(trayGeo, trayMat);
    tray.position.set(0, 1.57, -13.65);
    roomGroup.add(tray);

    // 7. Suspended Architectural Linear LED Downlights (Above Desks)
    [-2, 2].forEach((pz) => {
      const fixtureGeo = new THREE.BoxGeometry(14, 0.14, 0.22);
      const fixtureMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.85, roughness: 0.3 });
      const fixture = new THREE.Mesh(fixtureGeo, fixtureMat);
      fixture.position.set(0, 5.2, pz);
      roomGroup.add(fixture);

      // Light strip
      const stripGeo = new THREE.BoxGeometry(13.8, 0.02, 0.18);
      const stripMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        emissive: 0xfffbeb,
        emissiveIntensity: 1.8,
      });
      const strip = new THREE.Mesh(stripGeo, stripMat);
      strip.position.set(0, 5.12, pz);
      roomGroup.add(strip);

      // Suspension wire
      [-6, 6].forEach((wx) => {
        const wireGeo = new THREE.CylinderGeometry(0.012, 0.012, 1.8, 8);
        const wireMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8 });
        const wire = new THREE.Mesh(wireGeo, wireMat);
        wire.position.set(wx, 6.1, pz);
        roomGroup.add(wire);
      });
    });

    // 8. Silicon Valley Breakout Lounge (Deep Charcoal Acoustic Sectional)
    const sofaGroup = new THREE.Group();
    sofaGroup.position.set(8.5, 0, 7.5);

    const loungeFabricMat = new THREE.MeshStandardMaterial({ color: 0x242832, roughness: 0.85 }); // Charcoal acoustic weave
    // Main couch seat
    const couchBaseGeo = new THREE.BoxGeometry(4.2, 0.45, 1.8);
    const couchBase = new THREE.Mesh(couchBaseGeo, loungeFabricMat);
    couchBase.position.set(0, 0.225, 0);
    couchBase.castShadow = true;
    sofaGroup.add(couchBase);

    // Couch Backrest
    const couchBackGeo = new THREE.BoxGeometry(4.2, 0.65, 0.35);
    const couchBack = new THREE.Mesh(couchBackGeo, loungeFabricMat);
    couchBack.position.set(0, 0.775, 0.72);
    couchBack.castShadow = true;
    sofaGroup.add(couchBack);

    // L-Section
    const lSectionGeo = new THREE.BoxGeometry(1.6, 0.45, 2.2);
    const lSection = new THREE.Mesh(lSectionGeo, loungeFabricMat);
    lSection.position.set(1.3, 0.225, -1.8);
    lSection.castShadow = true;
    sofaGroup.add(lSection);

    // Modern Round Travertine / Fluted Coffee Table
    const marbleTableGeo = new THREE.CylinderGeometry(0.9, 0.9, 0.06, 24);
    const marbleMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.18, metalness: 0.05 });
    const marbleTable = new THREE.Mesh(marbleTableGeo, marbleMat);
    marbleTable.position.set(-0.8, 0.48, -0.6);
    marbleTable.castShadow = true;
    sofaGroup.add(marbleTable);

    // Coffee Table Matte Black Metal Legs
    const tableLegGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.48, 12);
    const tableLeg = new THREE.Mesh(tableLegGeo, sledLegMat);
    tableLeg.position.set(-0.8, 0.24, -0.6);
    sofaGroup.add(tableLeg);

    roomGroup.add(sofaGroup);

    // 9. Silicon Valley Style Micro-Kitchen & Coffee Bar (Waterfall Calacatta Quartz)
    const barGeo = new THREE.BoxGeometry(4.6, 1.05, 1.3);
    const barMat = new THREE.MeshStandardMaterial({ color: 0x0c0e12, roughness: 0.35 });
    const bar = new THREE.Mesh(barGeo, barMat);
    bar.position.set(-12, 0.525, -7.5);
    bar.castShadow = true;
    roomGroup.add(bar);

    // Waterfall Calacatta Marble Countertop
    const counterGeo = new THREE.BoxGeometry(4.8, 0.08, 1.45);
    const counterMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.15, metalness: 0.05 });
    const counter = new THREE.Mesh(counterGeo, counterMat);
    counter.position.set(-12, 1.09, -7.5);
    counter.castShadow = true;
    roomGroup.add(counter);

    // Commercial Dual-Group Italian Espresso Machine (La Marzocco Linea PB Style)
    const espressoGroup = new THREE.Group();
    espressoGroup.position.set(-13, 1.13, -7.5);

    const espressoBodyGeo = new THREE.BoxGeometry(0.88, 0.55, 0.62);
    const espressoBodyMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.95, roughness: 0.12 });
    const espressoBody = new THREE.Mesh(espressoBodyGeo, espressoBodyMat);
    espressoBody.position.y = 0.275;
    espressoGroup.add(espressoBody);

    // Dual Chrome Groupheads & Portafilters
    [-0.18, 0.18].forEach((gx) => {
      const groupGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.12, 14);
      const groupMesh = new THREE.Mesh(groupGeo, espressoBodyMat);
      groupMesh.position.set(gx, 0.18, 0.35);
      espressoGroup.add(groupMesh);

      const handleGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.22, 12);
      const handleMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.5 });
      const handle = new THREE.Mesh(handleGeo, handleMat);
      handle.rotation.x = Math.PI / 2;
      handle.position.set(gx, 0.16, 0.48);
      espressoGroup.add(handle);
    });

    // Dual Steam Wands
    [-0.38, 0.38].forEach((wx) => {
      const wandGeo = new THREE.CylinderGeometry(0.015, 0.015, 0.26, 8);
      const wand = new THREE.Mesh(wandGeo, espressoBodyMat);
      wand.rotation.z = wx < 0 ? -0.3 : 0.3;
      wand.position.set(wx, 0.22, 0.32);
      espressoGroup.add(wand);
    });

    roomGroup.add(espressoGroup);

    // Conical Burr Coffee Grinder (Mahlkönig EK43 Style)
    const grinderGeo = new THREE.CylinderGeometry(0.12, 0.14, 0.65, 16);
    const grinderMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.4 });
    const grinder = new THREE.Mesh(grinderGeo, grinderMat);
    grinder.position.set(-11.6, 1.45, -7.5);
    grinder.castShadow = true;
    roomGroup.add(grinder);

    // Glass Beverage Cooler with Illuminated Drinks Display
    const fridgeGeo = new THREE.BoxGeometry(1.1, 1.2, 0.95);
    const fridgeMat = new THREE.MeshStandardMaterial({ color: 0x1e2229, metalness: 0.85, roughness: 0.2 });
    const fridge = new THREE.Mesh(fridgeGeo, fridgeMat);
    fridge.position.set(-14.2, 0.6, -7.5);
    fridge.castShadow = true;
    roomGroup.add(fridge);

    const fridgeDoorGeo = new THREE.PlaneGeometry(0.95, 1.05);
    const fridgeDoorMat = new THREE.MeshPhysicalMaterial({
      color: 0x93c5fd,
      transmission: 0.85,
      transparent: true,
      roughness: 0.1,
    });
    const fridgeDoor = new THREE.Mesh(fridgeDoorGeo, fridgeDoorMat);
    fridgeDoor.rotation.y = Math.PI / 2;
    fridgeDoor.position.set(-13.64, 0.6, -7.5);
    roomGroup.add(fridgeDoor);

    // Standing Touchless Water Cooler
    const coolerGroup = new THREE.Group();
    coolerGroup.position.set(-14.2, 0, -4.5);
    const coolerBody = new THREE.Mesh(new THREE.BoxGeometry(0.55, 1.15, 0.55), new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.2 }));
    coolerBody.position.y = 0.575;
    coolerGroup.add(coolerBody);
    roomGroup.add(coolerGroup);

    // Modern Nordic Bar Stools
    [-12.8, -11.2].forEach((bx) => {
      const stoolGroup = new THREE.Group();
      stoolGroup.position.set(bx, 0, -6.1);
      const stoolSeat = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.06, 18), new THREE.MeshStandardMaterial({ color: 0x3d271b, roughness: 0.5 }));
      stoolSeat.position.y = 0.78;
      stoolGroup.add(stoolSeat);

      const stoolLeg = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.78, 12), sledLegMat);
      stoolLeg.position.y = 0.39;
      stoolGroup.add(stoolLeg);
      roomGroup.add(stoolGroup);
    });

    // 10. Biophilic Plants (Monstera, Fiddle Fig)
    const makePottedPlant = (px, pz, scale = 1, tall = false) => {
      const plantGroup = new THREE.Group();
      plantGroup.position.set(px, 0, pz);
      plantGroup.scale.set(scale, scale, scale);

      const potGeo = new THREE.CylinderGeometry(0.45, 0.32, 0.8, 18);
      const potMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.3 }); // Matte black ceramic
      const pot = new THREE.Mesh(potGeo, potMat);
      pot.position.y = 0.4;
      pot.castShadow = true;
      plantGroup.add(pot);

      const soilGeo = new THREE.CylinderGeometry(0.42, 0.42, 0.1, 16);
      const soilMat = new THREE.MeshStandardMaterial({ color: 0x3f2e1e, roughness: 0.95 });
      const soil = new THREE.Mesh(soilGeo, soilMat);
      soil.position.y = 0.78;
      plantGroup.add(soil);

      const leafMat = new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.35 });
      const leafCount = tall ? 12 : 8;
      for (let l = 0; l < leafCount; l++) {
        const leafGeo = new THREE.SphereGeometry(tall ? 0.32 : 0.38, 8, 8);
        leafGeo.scale(1.2, 0.08, 0.7);
        const leaf = new THREE.Mesh(leafGeo, leafMat);
        const angle = (l / leafCount) * Math.PI * 2;
        const heightOff = tall ? 0.9 + l * 0.16 : 0.9 + (l % 3) * 0.22;
        leaf.position.set(Math.cos(angle) * 0.48, heightOff, Math.sin(angle) * 0.48);
        leaf.rotation.set(0.3, angle, 0.4);
        leaf.castShadow = true;
        plantGroup.add(leaf);
      }
      return plantGroup;
    };

    roomGroup.add(makePottedPlant(-14.5, -12, 1.3, true));  // Corner Fiddle Fig
    roomGroup.add(makePottedPlant(14.2, 11, 1.2, false));   // Lounge Plant
    roomGroup.add(makePottedPlant(-14.5, 11, 1.1, false));  // Entrance Plant
    roomGroup.add(makePottedPlant(11.8, -11.5, 1.25, true)); // Meeting Room Plant

    scene.add(roomGroup);

    // ==========================================
    // 🖥️ ERGONOMIC WORKSTATION SETUP (Silicon Valley Engineering Standard)
    // ==========================================
    const createWorkstation = (x, z, data) => {
      const deskGroup = new THREE.Group();
      deskGroup.position.set(x, 0, z);

      // 1. Dual-Motor Sit-Stand Architectural Desk (Chamfered Ash Wood)
      const deskTopGeo = new THREE.BoxGeometry(2.1, 0.065, 1.25);
      const deskTopMat = new THREE.MeshStandardMaterial({
        color: 0xdfd7cd, // Nordic Bleached Ash
        roughness: 0.42,
        metalness: 0.02,
      });
      const deskTop = new THREE.Mesh(deskTopGeo, deskTopMat);
      deskTop.position.y = 0.76;
      deskTop.castShadow = true;
      deskTop.receiveShadow = true;
      deskGroup.add(deskTop);

      // Undercut Bevel on Tabletop
      const deskBevel = new THREE.Mesh(
        new THREE.BoxGeometry(2.04, 0.02, 1.19),
        new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.85, roughness: 0.2 })
      );
      deskBevel.position.y = 0.72;
      deskGroup.add(deskBevel);

      // Matte Black Dual Motor Lift Columns & Steel Feet
      const frameMat = new THREE.MeshStandardMaterial({ color: 0x0a0c10, metalness: 0.88, roughness: 0.2 });
      [-0.85, 0.85].forEach((lx) => {
        // Telescopic motorized column
        const col = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.72, 0.09), frameMat);
        col.position.set(lx, 0.36, 0);
        col.castShadow = true;
        deskGroup.add(col);

        // Floor skid foot
        const foot = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.04, 1.1), frameMat);
        foot.position.set(lx, 0.02, 0);
        foot.castShadow = true;
        deskGroup.add(foot);
      });

      // Flexible Cable Spine Snake running from desk to floor
      const snakeGeo = new THREE.CylinderGeometry(0.035, 0.035, 0.72, 8);
      const snake = new THREE.Mesh(snakeGeo, frameMat);
      snake.position.set(0.75, 0.36, -0.42);
      deskGroup.add(snake);

      // Large Acoustic Felt Desk Mat (Charcoal)
      const matGeo = new THREE.BoxGeometry(1.6, 0.008, 0.75);
      const feltMat = new THREE.MeshStandardMaterial({ color: 0x181a20, roughness: 0.95 });
      const deskMat = new THREE.Mesh(matGeo, feltMat);
      deskMat.position.set(0, 0.796, 0.02);
      deskMat.receiveShadow = true;
      deskGroup.add(deskMat);

      // Aluminum Laptop Base (MacBook Pro Style)
      const lapBaseGeo = new THREE.BoxGeometry(0.48, 0.016, 0.34);
      const lapBaseMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.92, roughness: 0.2 });
      const lapBase = new THREE.Mesh(lapBaseGeo, lapBaseMat);
      lapBase.position.set(0, 0.805, -0.05);
      lapBase.castShadow = true;
      deskGroup.add(lapBase);

      // Keyboard & Trackpad
      const kbGeo = new THREE.BoxGeometry(0.42, 0.005, 0.16);
      const kbMat = new THREE.MeshStandardMaterial({ color: 0x1e2229, roughness: 0.6 });
      const kb = new THREE.Mesh(kbGeo, kbMat);
      kb.position.set(0, 0.815, -0.02);
      deskGroup.add(kb);

      // Laptop Screen Lid & Display
      const screenPivot = new THREE.Group();
      screenPivot.position.set(0, 0.814, -0.21);

      const lidGeo = new THREE.BoxGeometry(0.48, 0.32, 0.014);
      const lid = new THREE.Mesh(lidGeo, lapBaseMat);
      lid.position.set(0, 0.16, 0);
      lid.castShadow = true;
      screenPivot.add(lid);

      const displayGeo = new THREE.PlaneGeometry(0.45, 0.28);
      const displayMat = new THREE.MeshStandardMaterial({
        color: data.screenColor,
        emissive: data.screenColor,
        emissiveIntensity: 0.9,
        roughness: 0.15,
      });
      const display = new THREE.Mesh(displayGeo, displayMat);
      display.position.set(0, 0.16, 0.008);
      screenPivot.add(display);

      // Screen Tilted slightly backward towards user
      screenPivot.rotation.x = -0.22;
      deskGroup.add(screenPivot);

      // Emissive Laptop Light
      const lapLight = new THREE.PointLight(data.screenColor, 1.1, 2.5);
      lapLight.position.set(0, 1.05, 0.05);
      deskGroup.add(lapLight);

      // 34" Ultrawide Curved Monitor on Articulated Gas-Spring Arm (For all engineering workstations)
      const armGroup = new THREE.Group();
      armGroup.position.set(-0.55, 0.79, -0.38);

      const armBase = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.08, 12), frameMat);
      armBase.position.y = 0.04;
      armGroup.add(armBase);

      const armStem = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.42, 12), frameMat);
      armStem.position.y = 0.25;
      armGroup.add(armStem);

      const armBoom = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.025, 0.025), frameMat);
      armBoom.position.set(0.12, 0.46, 0.08);
      armBoom.rotation.y = 0.3;
      armGroup.add(armBoom);

      // Ultrawide Curved Display Box
      const ultrawideGeo = new THREE.BoxGeometry(0.98, 0.44, 0.025);
      const ultrawideMat = new THREE.MeshStandardMaterial({
        color: 0x0a0c10,
        emissive: data.screenColor,
        emissiveIntensity: 0.45,
        roughness: 0.1,
      });
      const ultrawide = new THREE.Mesh(ultrawideGeo, ultrawideMat);
      ultrawide.position.set(0.15, 0.46, 0.12);
      ultrawide.rotation.y = 0.25; // angled toward user
      ultrawide.castShadow = true;
      armGroup.add(ultrawide);

      // ScreenBar LED Light Bar (BenQ style) mounted on top of ultrawide monitor
      const barFixture = new THREE.Mesh(
        new THREE.CylinderGeometry(0.012, 0.012, 0.65, 8),
        frameMat
      );
      barFixture.rotation.z = Math.PI / 2;
      barFixture.position.set(0.15, 0.7, 0.13);
      barFixture.rotation.y = 0.25;
      armGroup.add(barFixture);

      // Soft downward ScreenBar glow
      const taskGlow = new THREE.PointLight(0xfff7ed, 0.6, 1.8, 2);
      taskGlow.position.set(0.15, 0.65, 0.18);
      armGroup.add(taskGlow);

      deskGroup.add(armGroup);

      // Ceramic Coffee Mug
      const mugGeo = new THREE.CylinderGeometry(0.055, 0.048, 0.11, 16);
      const mugMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.2 });
      const mug = new THREE.Mesh(mugGeo, mugMat);
      mug.position.set(0.55, 0.85, 0.18);
      mug.castShadow = true;
      deskGroup.add(mug);

      // Small Desk Succulent Pot
      const potGeo = new THREE.CylinderGeometry(0.06, 0.045, 0.08, 14);
      const potMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.5 });
      const pot = new THREE.Mesh(potGeo, potMat);
      pot.position.set(-0.75, 0.835, -0.15);
      deskGroup.add(pot);

      const cactusGeo = new THREE.SphereGeometry(0.048, 10, 8);
      const cactusMat = new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.7 });
      const cactus = new THREE.Mesh(cactusGeo, cactusMat);
      cactus.position.set(-0.75, 0.90, -0.15);
      deskGroup.add(cactus);

      // Ergonomic Swivel Mesh Office Chair (Herman Miller Aeron Style, Distance 0.58 preserved)
      const chairGroup = new THREE.Group();
      chairGroup.position.set(0, 0, 0.58);

      const seatGeo = new THREE.BoxGeometry(0.55, 0.08, 0.52);
      const seatMat = new THREE.MeshStandardMaterial({ color: 0x181c24, roughness: 0.8 });
      const seat = new THREE.Mesh(seatGeo, seatMat);
      seat.position.y = 0.46;
      seat.castShadow = true;
      chairGroup.add(seat);

      // Ergonomic Curved Mesh Backrest
      const backGeo = new THREE.BoxGeometry(0.52, 0.62, 0.06);
      const backMat = new THREE.MeshStandardMaterial({ color: 0x222834, roughness: 0.7 });
      const back = new THREE.Mesh(backGeo, backMat);
      back.position.set(0, 0.78, 0.29);
      back.rotation.x = 0.08;
      back.castShadow = true;
      chairGroup.add(back);

      // Adjustable 3D Armrests
      [-0.27, 0.27].forEach((ax) => {
        const armPost = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.24, 0.05), frameMat);
        armPost.position.set(ax, 0.58, 0.08);
        chairGroup.add(armPost);

        const armPad = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.03, 0.22), new THREE.MeshStandardMaterial({ color: 0x0a0c10, roughness: 0.5 }));
        armPad.position.set(ax, 0.71, 0.08);
        chairGroup.add(armPad);
      });

      // Chrome 5-Star Base & Pneumatic Stem
      const baseStemGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.38, 12);
      const baseStemMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.92, roughness: 0.2 });
      const baseStem = new THREE.Mesh(baseStemGeo, baseStemMat);
      baseStem.position.y = 0.22;
      chairGroup.add(baseStem);

      const starBaseGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.04, 5);
      const starBase = new THREE.Mesh(starBaseGeo, baseStemMat);
      starBase.position.y = 0.06;
      chairGroup.add(starBase);

      deskGroup.add(chairGroup);
      scene.add(deskGroup);

      return { displayMat, lapLight };
    };

        // ==========================================
    // 🏷️ FLOATING NAME LABEL (Billboard Canvas Sprite)
    // ==========================================
    const createNameLabel = (name, role, color) => {
      const canvas = document.createElement("canvas");
      canvas.width = 512;
      canvas.height = 112;
      const ctx = canvas.getContext("2d");

      ctx.clearRect(0, 0, 512, 112);
      const colorHex = "#" + color.toString(16).padStart(6, "0");

      // Badge Background Pill
      ctx.fillStyle = "rgba(10, 15, 29, 0.85)";
      ctx.beginPath();
      ctx.roundRect(8, 8, 496, 96, 20);
      ctx.fill();

      // Left Accent Bar
      ctx.fillStyle = colorHex;
      ctx.beginPath();
      ctx.roundRect(8, 8, 10, 96, [20, 0, 0, 20]);
      ctx.fill();

      // Name Text
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 44px system-ui, -apple-system, sans-serif";
      ctx.textBaseline = "middle";
      ctx.fillText(name, 36, 42);

      // Role Subtitle Text
      ctx.fillStyle = colorHex;
      ctx.font = "600 30px system-ui, -apple-system, sans-serif";
      ctx.fillText(role, 36, 80);

      const texture = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthWrite: false,
      });
      const sprite = new THREE.Sprite(spriteMat);
      sprite.scale.set(1.9, 0.42, 1);
      return sprite;
    };

    // ==========================================
    // 👤 REALISTIC STYLIZED HUMAN AVATAR
    // Natural anatomy: head with ears/nose/eyes,
    // shirt collar, ID lanyard, articulate arms & legs.
    // ==========================================
    const createStylizedHuman = (id, data) => {
      const [x, , z] = data.pos;
      const deskObjects = createWorkstation(x, z, data);

      const humanRoot = new THREE.Group();
      humanRoot.position.set(x, 0, z + 0.58);

      // PBR Materials
      const skinMat = new THREE.MeshStandardMaterial({
        color: data.skinColor || 0xf5d0b5,
        roughness: 0.58,
        metalness: 0.0,
      });
      const clothesMat = new THREE.MeshStandardMaterial({
        color: data.color,
        roughness: 0.85,
        metalness: 0.05,
      });
      const pantsMat = new THREE.MeshStandardMaterial({
        color: 0x1e293b,
        roughness: 0.9,
      });
      const hairMat = new THREE.MeshStandardMaterial({
        color: data.hairColor,
        roughness: 0.8,
      });

      // ---- ARTICULATED LOWER BODY (Hips + Knees + Shoes) ----
      const makeLeg = (side) => {
        const hipPivot = new THREE.Group();
        // Placed slightly forward (z = -0.04) and adjusted height (y = 0.46) to align with chair cushion
        hipPivot.position.set(side * 0.125, 0.46, -0.04);

        // Thigh: Extends forward (-Z when hip rotation.x = -PI/2)
        const thighGeo = new THREE.CapsuleGeometry(0.062, 0.22, 8, 14);
        const thigh = new THREE.Mesh(thighGeo, pantsMat);
        thigh.position.y = -0.11;
        thigh.castShadow = true;
        hipPivot.add(thigh);

        // Knee joint
        const kneePivot = new THREE.Group();
        kneePivot.position.y = -0.22;
        hipPivot.add(kneePivot);

        const kneeBall = new THREE.Mesh(new THREE.SphereGeometry(0.054, 10, 8), pantsMat);
        kneePivot.add(kneeBall);

        // Calf: Hangs down to floor
        const calfGeo = new THREE.CapsuleGeometry(0.052, 0.22, 8, 14);
        const calf = new THREE.Mesh(calfGeo, pantsMat);
        calf.position.y = -0.11;
        calf.castShadow = true;
        kneePivot.add(calf);

        // Sneaker
        const shoeGeo = new THREE.SphereGeometry(0.068, 14, 10);
        shoeGeo.scale(1.0, 0.52, 1.45);
        const shoeMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.6 });
        const shoe = new THREE.Mesh(shoeGeo, shoeMat);
        shoe.position.set(0, -0.22, -0.04);
        shoe.castShadow = true;
        kneePivot.add(shoe);

        // White rubber sole resting flush on floor
        const soleGeo = new THREE.BoxGeometry(0.12, 0.025, 0.22);
        const soleMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.4 });
        const sole = new THREE.Mesh(soleGeo, soleMat);
        sole.position.set(0, -0.25, -0.04);
        kneePivot.add(sole);

        humanRoot.add(hipPivot);
        return { hipPivot, kneePivot };
      };

      const leftLeg = makeLeg(-1);
      const rightLeg = makeLeg(1);

      // Default seated at desk
      leftLeg.hipPivot.rotation.x = -Math.PI / 2;
      rightLeg.hipPivot.rotation.x = -Math.PI / 2;
      leftLeg.kneePivot.rotation.x = Math.PI / 2;
      rightLeg.kneePivot.rotation.x = Math.PI / 2;

      // ---- UPPER BODY PIVOT ----
      const torsoPivot = new THREE.Group();
      torsoPivot.position.set(0, 0.52, 0);

      // Torso: Capsule scaled to chest & waist
      const torsoGeo = new THREE.CapsuleGeometry(0.19, 0.3, 10, 20);
      torsoGeo.scale(1.15, 1.0, 0.72);
      const torso = new THREE.Mesh(torsoGeo, clothesMat);
      torso.position.y = 0.23;
      torso.castShadow = true;
      torsoPivot.add(torso);

      // Shirt Collar (Professional Office Look)
      const collarGeo = new THREE.TorusGeometry(0.12, 0.025, 8, 16, Math.PI);
      const collarMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.6 });
      const collar = new THREE.Mesh(collarGeo, collarMat);
      collar.rotation.x = Math.PI / 2;
      collar.position.set(0, 0.45, -0.06);
      torsoPivot.add(collar);

      // ID Card Lanyard Hanging Around Neck
      if (data.hasLanyard) {
        const lanyardGeo = new THREE.TorusGeometry(0.14, 0.012, 8, 16, Math.PI);
        const lanyardMat = new THREE.MeshStandardMaterial({ color: data.accentColor || 0x6366f1 });
        const lanyard = new THREE.Mesh(lanyardGeo, lanyardMat);
        lanyard.rotation.x = Math.PI / 2.2;
        lanyard.position.set(0, 0.44, -0.07);
        torsoPivot.add(lanyard);

        const badgeGeo = new THREE.BoxGeometry(0.08, 0.11, 0.01);
        const badgeMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc });
        const badge = new THREE.Mesh(badgeGeo, badgeMat);
        badge.position.set(0, 0.28, -0.16);
        torsoPivot.add(badge);
      }

      // Neck
      const neckGeo = new THREE.CylinderGeometry(0.075, 0.085, 0.14, 16);
      const neck = new THREE.Mesh(neckGeo, skinMat);
      neck.position.y = 0.5;
      torsoPivot.add(neck);

      // ---- HEAD & DETAILED FACE ----
      const headGroup = new THREE.Group();
      headGroup.position.set(0, 0.64, 0);

      const headGeo = new THREE.SphereGeometry(0.155, 28, 22);
      headGeo.scale(0.95, 1.15, 1.05);
      const head = new THREE.Mesh(headGeo, skinMat);
      head.castShadow = true;
      headGroup.add(head);

      // Ears
      [-0.155, 0.155].forEach((ex) => {
        const earGeo = new THREE.SphereGeometry(0.038, 10, 8);
        earGeo.scale(0.4, 1.0, 0.7);
        const ear = new THREE.Mesh(earGeo, skinMat);
        ear.position.set(ex, 0.01, -0.01);
        headGroup.add(ear);
      });

      // Nose
      const noseGeo = new THREE.ConeGeometry(0.024, 0.06, 12);
      const nose = new THREE.Mesh(noseGeo, skinMat);
      nose.rotation.x = -Math.PI / 2.2;
      nose.position.set(0, -0.01, -0.17);
      headGroup.add(nose);

      // Eyes
      [-0.052, 0.052].forEach((ex) => {
        const eyeGeo = new THREE.SphereGeometry(0.025, 12, 10);
        eyeGeo.scale(1.2, 0.8, 0.6);
        const eye = new THREE.Mesh(eyeGeo, new THREE.MeshBasicMaterial({ color: 0xffffff }));
        eye.position.set(ex, 0.03, -0.16);
        headGroup.add(eye);

        const pupilGeo = new THREE.SphereGeometry(0.013, 8, 8);
        const pupilMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });
        const pupil = new THREE.Mesh(pupilGeo, pupilMat);
        pupil.position.set(ex, 0.03, -0.174);
        headGroup.add(pupil);
      });

      // Glasses
      if (data.hasGlasses) {
        const frameMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.9, roughness: 0.2 });
        [-0.052, 0.052].forEach((gx) => {
          const rimGeo = new THREE.TorusGeometry(0.032, 0.006, 8, 16);
          const rim = new THREE.Mesh(rimGeo, frameMat);
          rim.position.set(gx, 0.03, -0.168);
          headGroup.add(rim);
        });
        const bridgeGeo = new THREE.BoxGeometry(0.04, 0.006, 0.006);
        const bridge = new THREE.Mesh(bridgeGeo, frameMat);
        bridge.position.set(0, 0.03, -0.168);
        headGroup.add(bridge);
      }

      // Hair
      const hairDomeGeo = new THREE.SphereGeometry(0.172, 22, 18, 0, Math.PI * 2, 0, Math.PI / 1.75);
      const hairDome = new THREE.Mesh(hairDomeGeo, hairMat);
      hairDome.position.set(0, 0.045, 0.01);
      hairDome.castShadow = true;
      headGroup.add(hairDome);

      if (data.hairStyle === "ponytail") {
        const ponyGeo = new THREE.CapsuleGeometry(0.045, 0.24, 8, 12);
        const pony = new THREE.Mesh(ponyGeo, hairMat);
        pony.position.set(0, 0.02, 0.22);
        pony.rotation.x = -0.45;
        headGroup.add(pony);
      }

      if (data.hasHeadphones) {
        const bandGeo = new THREE.TorusGeometry(0.18, 0.016, 8, 24, Math.PI);
        const hpMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8, roughness: 0.3 });
        const band = new THREE.Mesh(bandGeo, hpMat);
        band.position.set(0, 0.06, 0);
        headGroup.add(band);

        [-0.17, 0.17].forEach((hx) => {
          const cupMeshGeo = new THREE.CylinderGeometry(0.05, 0.05, 0.04, 16);
          const cupMesh = new THREE.Mesh(cupMeshGeo, hpMat);
          cupMesh.rotation.z = Math.PI / 2;
          cupMesh.position.set(hx, 0.02, 0);
          headGroup.add(cupMesh);
        });
      }

      torsoPivot.add(headGroup);

      // ---- 2-SEGMENT ARTICULATED ARMS ----
      const makeArm = (side) => {
        const shoulder = new THREE.Group();
        shoulder.position.set(side * 0.255, 0.38, 0);

        const upperArmGeo = new THREE.CapsuleGeometry(0.055, 0.18, 8, 14);
        const upperArm = new THREE.Mesh(upperArmGeo, clothesMat);
        upperArm.position.y = -0.1;
        upperArm.castShadow = true;
        shoulder.add(upperArm);

        const elbowPivot = new THREE.Group();
        elbowPivot.position.y = -0.23;
        shoulder.add(elbowPivot);

        const elbowBall = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 10), clothesMat);
        elbowPivot.add(elbowBall);

        const forearmGeo = new THREE.CapsuleGeometry(0.042, 0.17, 8, 14);
        const forearm = new THREE.Mesh(forearmGeo, skinMat);
        forearm.position.y = -0.12;
        forearm.castShadow = true;
        elbowPivot.add(forearm);

        if (data.hasSmartwatch && side === -1) {
          const watchGeo = new THREE.CylinderGeometry(0.046, 0.046, 0.03, 14);
          const watchMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, emissive: 0x38bdf8, emissiveIntensity: 0.8 });
          const watch = new THREE.Mesh(watchGeo, watchMat);
          watch.position.y = -0.18;
          elbowPivot.add(watch);
        }

        // Articulated Wrist Joint for realistic typing on keyboard
        const wristPivot = new THREE.Group();
        wristPivot.position.y = -0.21;
        elbowPivot.add(wristPivot);

        const handGeo = new THREE.SphereGeometry(0.042, 14, 12);
        handGeo.scale(1.2, 0.65, 1.1);
        const hand = new THREE.Mesh(handGeo, skinMat);
        hand.position.set(0, -0.03, 0.02);
        hand.castShadow = true;
        wristPivot.add(hand);

        // Fingertips indicator
        const fingerGeo = new THREE.BoxGeometry(0.065, 0.015, 0.045);
        const finger = new THREE.Mesh(fingerGeo, skinMat);
        finger.position.set(0, -0.045, 0.045);
        wristPivot.add(finger);

        return { shoulder, elbowPivot, wristPivot };
      };

      const leftArm = makeArm(-1);
      const rightArm = makeArm(1);
      const leftShoulder = leftArm.shoulder;
      const rightShoulder = rightArm.shoulder;
      const leftElbow = leftArm.elbowPivot;
      const rightElbow = rightArm.elbowPivot;
      const leftWrist = leftArm.wristPivot;
      const rightWrist = rightArm.wristPivot;
      torsoPivot.add(leftShoulder);
      torsoPivot.add(rightShoulder);
      humanRoot.add(torsoPivot);

      // Coffee Mug in Hand (Visible when in Pantry or Lounge)
      const mugGeo = new THREE.CylinderGeometry(0.038, 0.03, 0.08, 14);
      const mugMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 });
      const coffeeCup = new THREE.Mesh(mugGeo, mugMat);
      coffeeCup.position.set(0, -0.22, 0.06);
      coffeeCup.visible = false;
      rightElbow.add(coffeeCup);

      // Floating Name Sprite directly to scene
      const nameSprite = createNameLabel(data.name, data.role, data.color & 0xffffff);
      nameSprite.position.set(humanRoot.position.x, 2.08, humanRoot.position.z);
      scene.add(nameSprite);

      // Active Floor Halo Ring
      const ringGeo = new THREE.RingGeometry(0.68, 0.78, 44);
      const ringMat = new THREE.MeshBasicMaterial({
        color: data.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0,
      });
      const haloRing = new THREE.Mesh(ringGeo, ringMat);
      haloRing.rotation.x = -Math.PI / 2;
      haloRing.position.y = 0.03;
      humanRoot.add(haloRing);

      scene.add(humanRoot);

      agentMeshesRef.current[id] = {
        humanRoot,
        torsoPivot,
        headGroup,
        leftShoulder,
        rightShoulder,
        leftElbow,
        rightElbow,
        leftWrist,
        rightWrist,
        leftLeg,
        rightLeg,
        haloRing,
        nameSprite,
        deskObjects,
        coffeeCup,
        isWorking: false,
        isWalking: false,
        currentMode: "WORK",
        targetMode: "WORK",
        targetRotationY: 0,
        currentRotationY: 0,
        walkTime: 0,
        waypoints: [],
        deskPos: [x, 0, z + 0.58],
      };
    };

    // ==========================================
    // FLOATING NAME LABEL FOR BOS MUDA (Canvas Sprite)
    // ==========================================
    const createPlayerNameLabel = () => {
      const canvas = document.createElement("canvas");
      canvas.width = 512;
      canvas.height = 120;
      const ctx = canvas.getContext("2d");

      ctx.clearRect(0, 0, 512, 120);

      // Badge Background Pill (Dark Obsidian with Gold Border)
      ctx.fillStyle = "rgba(15, 23, 42, 0.94)";
      ctx.beginPath();
      ctx.roundRect(8, 8, 496, 104, 22);
      ctx.fill();

      // Gold Border
      ctx.strokeStyle = "rgba(245, 158, 11, 0.9)";
      ctx.lineWidth = 4;
      ctx.stroke();

      // Left Gold Accent Bar
      ctx.fillStyle = "#f59e0b";
      ctx.beginPath();
      ctx.roundRect(8, 8, 12, 104, [22, 0, 0, 22]);
      ctx.fill();

      // Crown & Name Text
      ctx.fillStyle = "#f59e0b";
      ctx.font = "bold 40px system-ui, -apple-system, sans-serif";
      ctx.textBaseline = "middle";
      ctx.fillText("BOS MUDA", 36, 44);

      // Subtitle Role
      ctx.fillStyle = "#f8fafc";
      ctx.font = "bold 24px system-ui, -apple-system, sans-serif";
      ctx.fillText("FOUNDER & SANG EMPU", 36, 84);

      const texture = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthWrite: false,
      });
      const sprite = new THREE.Sprite(spriteMat);
      sprite.scale.set(2.1, 0.48, 1);
      return sprite;
    };

    // ==========================================
    // AVATAR BOS MUDA (FOUNDER & SANG EMPU)
    // ==========================================
    const createPlayerAvatar = () => {
      const playerRoot = new THREE.Group();
      playerRoot.position.set(0, 0, 7.2); // Spawns near lounge circulation area

      const skinMat = new THREE.MeshStandardMaterial({
        color: 0xf3c5a8,
        roughness: 0.55,
        metalness: 0.0,
      });
      const jacketMat = new THREE.MeshStandardMaterial({
        color: 0x0f172a,
        roughness: 0.75,
        metalness: 0.08,
      });
      const pantsMat = new THREE.MeshStandardMaterial({
        color: 0x1e293b,
        roughness: 0.85,
      });
      const hairMat = new THREE.MeshStandardMaterial({
        color: 0x171717,
        roughness: 0.8,
      });
      const goldMat = new THREE.MeshStandardMaterial({
        color: 0xd4af37,
        metalness: 0.95,
        roughness: 0.15,
        emissive: 0x92400e,
        emissiveIntensity: 0.25,
      });

      // ---- ARTICULATED LEGS (Standing by default) ----
      const makePlayerLeg = (side) => {
        const hipPivot = new THREE.Group();
        hipPivot.position.set(side * 0.13, 0.46, 0);

        const thighGeo = new THREE.CapsuleGeometry(0.065, 0.24, 8, 14);
        const thigh = new THREE.Mesh(thighGeo, pantsMat);
        thigh.position.y = -0.12;
        thigh.castShadow = true;
        hipPivot.add(thigh);

        const kneePivot = new THREE.Group();
        kneePivot.position.y = -0.24;
        hipPivot.add(kneePivot);

        const kneeBall = new THREE.Mesh(new THREE.SphereGeometry(0.056, 10, 8), pantsMat);
        kneePivot.add(kneeBall);

        const calfGeo = new THREE.CapsuleGeometry(0.054, 0.24, 8, 14);
        const calf = new THREE.Mesh(calfGeo, pantsMat);
        calf.position.y = -0.12;
        calf.castShadow = true;
        kneePivot.add(calf);

        const shoeGeo = new THREE.SphereGeometry(0.07, 14, 10);
        shoeGeo.scale(1.0, 0.52, 1.45);
        const shoeMat = new THREE.MeshStandardMaterial({ color: 0x09090b, roughness: 0.5 });
        const shoe = new THREE.Mesh(shoeGeo, shoeMat);
        shoe.position.set(0, -0.23, -0.04);
        shoe.castShadow = true;
        kneePivot.add(shoe);

        const soleGeo = new THREE.BoxGeometry(0.125, 0.025, 0.23);
        const soleMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 });
        const sole = new THREE.Mesh(soleGeo, soleMat);
        sole.position.set(0, -0.255, -0.04);
        kneePivot.add(sole);

        playerRoot.add(hipPivot);
        return { hipPivot, kneePivot };
      };

      const leftLeg = makePlayerLeg(-1);
      const rightLeg = makePlayerLeg(1);

      leftLeg.hipPivot.rotation.x = 0;
      rightLeg.hipPivot.rotation.x = 0;
      leftLeg.kneePivot.rotation.x = 0;
      rightLeg.kneePivot.rotation.x = 0;

      // ---- UPPER BODY PIVOT ----
      const torsoPivot = new THREE.Group();
      torsoPivot.position.set(0, 0.52, 0);

      const torsoGeo = new THREE.CapsuleGeometry(0.20, 0.32, 10, 20);
      torsoGeo.scale(1.15, 1.0, 0.72);
      const torso = new THREE.Mesh(torsoGeo, jacketMat);
      torso.position.y = 0.24;
      torso.castShadow = true;
      torsoPivot.add(torso);

      const collarGeo = new THREE.TorusGeometry(0.125, 0.025, 8, 16, Math.PI);
      const collarMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.5 });
      const collar = new THREE.Mesh(collarGeo, collarMat);
      collar.rotation.x = Math.PI / 2;
      collar.position.set(0, 0.46, -0.06);
      torsoPivot.add(collar);

      const lanyardGeo = new THREE.TorusGeometry(0.145, 0.014, 8, 16, Math.PI);
      const lanyard = new THREE.Mesh(lanyardGeo, goldMat);
      lanyard.rotation.x = Math.PI / 2.2;
      lanyard.position.set(0, 0.45, -0.07);
      torsoPivot.add(lanyard);

      const founderBadgeGeo = new THREE.BoxGeometry(0.085, 0.12, 0.012);
      const founderBadgeMat = new THREE.MeshStandardMaterial({ color: 0x18181b, metalness: 0.5, roughness: 0.2 });
      const founderBadge = new THREE.Mesh(founderBadgeGeo, founderBadgeMat);
      founderBadge.position.set(0, 0.28, -0.165);
      torsoPivot.add(founderBadge);

      const emblem = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.03, 0.015), goldMat);
      emblem.position.set(0, 0.29, -0.17);
      torsoPivot.add(emblem);

      const neckGeo = new THREE.CylinderGeometry(0.075, 0.085, 0.14, 16);
      const neck = new THREE.Mesh(neckGeo, skinMat);
      neck.position.y = 0.51;
      torsoPivot.add(neck);

      const headGroup = new THREE.Group();
      headGroup.position.set(0, 0.65, 0);

      const headGeo = new THREE.SphereGeometry(0.155, 28, 22);
      headGeo.scale(0.95, 1.15, 1.05);
      const head = new THREE.Mesh(headGeo, skinMat);
      head.castShadow = true;
      headGroup.add(head);

      [-0.155, 0.155].forEach((ex) => {
        const earGeo = new THREE.SphereGeometry(0.038, 10, 8);
        earGeo.scale(0.4, 1.0, 0.7);
        const ear = new THREE.Mesh(earGeo, skinMat);
        ear.position.set(ex, 0.01, -0.01);
        headGroup.add(ear);
      });

      const noseGeo = new THREE.ConeGeometry(0.024, 0.06, 12);
      const nose = new THREE.Mesh(noseGeo, skinMat);
      nose.rotation.x = -Math.PI / 2.2;
      nose.position.set(0, -0.01, -0.17);
      headGroup.add(nose);

      [-0.052, 0.052].forEach((ex) => {
        const eyeGeo = new THREE.SphereGeometry(0.025, 12, 10);
        eyeGeo.scale(1.2, 0.8, 0.6);
        const eye = new THREE.Mesh(eyeGeo, new THREE.MeshBasicMaterial({ color: 0xffffff }));
        eye.position.set(ex, 0.03, -0.16);
        headGroup.add(eye);

        const pupilGeo = new THREE.SphereGeometry(0.013, 8, 8);
        const pupilMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });
        const pupil = new THREE.Mesh(pupilGeo, pupilMat);
        pupil.position.set(ex, 0.03, -0.174);
        headGroup.add(pupil);
      });

      const hairDomeGeo = new THREE.SphereGeometry(0.175, 22, 18, 0, Math.PI * 2, 0, Math.PI / 1.75);
      const hairDome = new THREE.Mesh(hairDomeGeo, hairMat);
      hairDome.position.set(0, 0.05, 0.01);
      hairDome.castShadow = true;
      headGroup.add(hairDome);

      torsoPivot.add(headGroup);

      const makePlayerArm = (side) => {
        const shoulder = new THREE.Group();
        shoulder.position.set(side * 0.26, 0.38, 0);

        const upperArmGeo = new THREE.CapsuleGeometry(0.056, 0.19, 8, 14);
        const upperArm = new THREE.Mesh(upperArmGeo, jacketMat);
        upperArm.position.y = -0.1;
        upperArm.castShadow = true;
        shoulder.add(upperArm);

        const elbowPivot = new THREE.Group();
        elbowPivot.position.y = -0.23;
        shoulder.add(elbowPivot);

        const elbowBall = new THREE.Mesh(new THREE.SphereGeometry(0.052, 12, 10), jacketMat);
        elbowPivot.add(elbowBall);

        const forearmGeo = new THREE.CapsuleGeometry(0.044, 0.17, 8, 14);
        const forearm = new THREE.Mesh(forearmGeo, skinMat);
        forearm.position.y = -0.12;
        forearm.castShadow = true;
        elbowPivot.add(forearm);

        if (side === -1) {
          const watchGeo = new THREE.CylinderGeometry(0.048, 0.048, 0.035, 14);
          const watch = new THREE.Mesh(watchGeo, goldMat);
          watch.position.y = -0.18;
          elbowPivot.add(watch);
        }

        const handGeo = new THREE.SphereGeometry(0.044, 14, 12);
        handGeo.scale(1.2, 0.65, 1.1);
        const hand = new THREE.Mesh(handGeo, skinMat);
        hand.position.set(0, -0.22, 0.02);
        hand.castShadow = true;
        elbowPivot.add(hand);

        return { shoulder, elbowPivot };
      };

      const leftArm = makePlayerArm(-1);
      const rightArm = makePlayerArm(1);
      torsoPivot.add(leftArm.shoulder);
      torsoPivot.add(rightArm.shoulder);

      playerRoot.add(torsoPivot);

      const nameSprite = createPlayerNameLabel();
      nameSprite.position.set(playerRoot.position.x, 2.25, playerRoot.position.z);
      scene.add(nameSprite);

      const ringGeo = new THREE.RingGeometry(0.72, 0.84, 44);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0xf59e0b,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.85,
      });
      const haloRing = new THREE.Mesh(ringGeo, ringMat);
      haloRing.rotation.x = Math.PI / 2;
      haloRing.position.set(playerRoot.position.x, 0.02, playerRoot.position.z);
      scene.add(haloRing);

      scene.add(playerRoot);

      return {
        root: playerRoot,
        leftLeg,
        rightLeg,
        leftArm,
        rightArm,
        torsoPivot,
        headGroup,
        haloRing,
        nameSprite,
        pos: playerRoot.position,
        walkCycle: 0,
        isWalking: false,
        targetDest: null,
      };
    };

    // Instantiate all 8 Wayangs in Studio
    Object.entries(AGENTS).forEach(([id, data]) => {
      createStylizedHuman(id, data);
    });

    // Instantiate Bos Muda Avatar
    playerRef.current = createPlayerAvatar();

    // 60FPS RAF Render Loop (MengTo Optimization)
    // Setup Navigation Handler for App Controls
    window.__agentMeshes = agentMeshesRef.current;
    window.__agentNav = (id, mode) => agentNavRef.current && agentNavRef.current(id, mode);
    agentNavRef.current = (agentId, targetMode) => {
      const agent = agentMeshesRef.current[agentId];
      if (!agent) return;
      agent.targetMode = targetMode;
      agent.currentMode = targetMode;

      const targetConfig = LOCATION_SPOTS[targetMode]?.[agentId];
      if (!targetConfig) return;

      const [tx, ty, tz] = targetConfig.pos;
      const targetPos = new THREE.Vector3(tx, ty, tz);
      const wps = getWaypoints(agent.humanRoot.position, targetPos);
      agent.waypoints = wps;
      agent.targetRotationY = targetConfig.rotY;
      agent.walkTime = 0;
    };

    let lastTime = performance.now();
    let animId;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const now = performance.now();
      const delta = Math.min(Math.max((now - lastTime) / 1000, 0.016), 0.1);
      lastTime = now;
      const elapsed = now / 1000;
      controls.update();

      mixers.forEach((m) => m.update(delta));

      Object.entries(agentMeshesRef.current).forEach(([id, agent]) => {
        const {
          humanRoot,
          torsoPivot,
          headGroup,
          leftShoulder,
          rightShoulder,
          leftElbow,
          rightElbow,
          leftLeg,
          rightLeg,
          haloRing,
          nameSprite,
          deskObjects,
          coffeeCup,
          isWorking,
        } = agent;

        // 1. Clean Frame-Safe Waypoint Walking Locomotion
        if (agent.waypoints && agent.waypoints.length > 0) {
          agent.isWalking = true;
          const targetWp = agent.waypoints[0];
          const curPos = humanRoot.position;
          const dx = targetWp.x - curPos.x;
          const dz = targetWp.z - curPos.z;
          const dist = Math.hypot(dx, dz);

          if (dist < 0.25) {
            curPos.x = targetWp.x;
            curPos.z = targetWp.z;
            agent.waypoints.shift();
            if (agent.waypoints.length === 0) {
              agent.isWalking = false;
            }
          } else {
            const step = Math.min(dist, 7.5 * delta);
            curPos.x += (dx / dist) * step;
            curPos.z += (dz / dist) * step;

            const walkAngle = Math.atan2(dx, dz) + Math.PI;
            humanRoot.rotation.y = THREE.MathUtils.lerp(humanRoot.rotation.y, walkAngle, 0.25);
          }

          agent.walkTime += delta * 12;
          const swing = Math.sin(agent.walkTime);

          leftLeg.hipPivot.rotation.x = swing * 0.52;
          rightLeg.hipPivot.rotation.x = -swing * 0.52;
          leftLeg.kneePivot.rotation.x = Math.max(0, -swing) * 0.6;
          rightLeg.kneePivot.rotation.x = Math.max(0, swing) * 0.6;

          leftShoulder.rotation.x = -swing * 0.42;
          rightShoulder.rotation.x = swing * 0.42;
          leftElbow.rotation.x = -0.3;
          rightElbow.rotation.x = -0.3;

          torsoPivot.position.y = 0.52 + Math.abs(Math.sin(agent.walkTime * 2)) * 0.04;
          torsoPivot.rotation.x = 0.05;
        } else {
          // 2. Stationary State Postures
          agent.isWalking = false;
          humanRoot.rotation.y = THREE.MathUtils.lerp(humanRoot.rotation.y, agent.targetRotationY, 0.08);

          if (agent.currentMode === "WORK") {
            coffeeCup.visible = false;
            leftLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(leftLeg.hipPivot.rotation.x, -Math.PI / 2, 0.1);
            rightLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(rightLeg.hipPivot.rotation.x, -Math.PI / 2, 0.1);
            leftLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(leftLeg.kneePivot.rotation.x, Math.PI / 2, 0.1);
            rightLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(rightLeg.kneePivot.rotation.x, Math.PI / 2, 0.1);

            const { leftWrist, rightWrist } = agent;
            const pInfo = AGENTS[id];
            const speed = pInfo?.speedFactor || 1.0;
            const pStyle = pInfo?.typingStyle || "methodical";

            if (isWorking) {
              // --- UNIQUE PERSONALITY TYPING BEHAVIORS ---
              let lTyping = 0;
              let rTyping = 0;
              let lWristFlick = 0;
              let rWristFlick = 0;
              let torsoPitch = 0.18;
              let headPitch = 0.32;
              let headYaw = 0;

              if (pStyle === "commanding") { // Risko: Wibawa, ketukan mantap berbobot
                const burst = Math.sin(elapsed * 16 * speed);
                lTyping = burst * 0.12;
                rTyping = Math.cos(elapsed * 16 * speed + 0.8) * 0.12;
                lWristFlick = Math.sin(elapsed * 18) * 0.14;
                rWristFlick = Math.cos(elapsed * 18) * 0.14;
                torsoPitch = 0.15;
                headPitch = 0.28;
                headYaw = Math.sin(elapsed * 1.2) * 0.04;
              } else if (pStyle === "furious") { // Zaki: Hacker cepat kilat + headphone headbobbing
                const burst = Math.sin(elapsed * 32 * speed);
                lTyping = burst * 0.16;
                rTyping = Math.cos(elapsed * 32 * speed + 1.4) * 0.16;
                lWristFlick = Math.sin(elapsed * 34) * 0.22;
                rWristFlick = Math.cos(elapsed * 34) * 0.22;
                torsoPitch = 0.22;
                headPitch = 0.34 + Math.sin(elapsed * 8) * 0.08; // Headbobbing to music!
                headYaw = Math.sin(elapsed * 4) * 0.03;
              } else if (pStyle === "methodical") { // Pingot: Metronomik, tenang, teratur
                const clk = elapsed * 14 * speed;
                lTyping = Math.sin(clk) * 0.09;
                rTyping = Math.cos(clk + Math.PI / 2) * 0.09;
                lWristFlick = Math.sin(clk) * 0.12;
                rWristFlick = Math.cos(clk + Math.PI / 2) * 0.12;
                torsoPitch = 0.14;
                headPitch = 0.30;
                headYaw = Math.sin(elapsed * 0.9) * 0.02;
              } else if (pStyle === "perfectionist") { // Lulu: Desainer, tangan kanan aktif mouse/stylus
                lTyping = Math.sin(elapsed * 18 * speed) * 0.08; // Tangan kiri di keyboard shortcuts
                rTyping = Math.sin(elapsed * 9 * speed) * 0.04;  // Tangan kanan gerak luwes
                lWristFlick = Math.sin(elapsed * 18) * 0.14;
                rWristFlick = Math.cos(elapsed * 6) * 0.18; // Luwes di mousepad
                torsoPitch = 0.17;
                headPitch = 0.30;
                headYaw = Math.sin(elapsed * 2.2) * 0.06; // Memeriksa kanvas visual
              } else if (pStyle === "poetic") { // Mika: Santai, ritmis lembut, sering jeda diksi
                const thoughtPause = Math.sin(elapsed * 1.5) > 0.4;
                if (!thoughtPause) {
                  const clk = elapsed * 20 * speed;
                  lTyping = Math.sin(clk) * 0.10;
                  rTyping = Math.cos(clk + 1.1) * 0.10;
                  lWristFlick = Math.sin(clk) * 0.15;
                  rWristFlick = Math.cos(clk) * 0.15;
                  headPitch = 0.32;
                } else {
                  // Jeda sejenak mikir diksi kata
                  headPitch = 0.18; // Dongak sedikit
                  headYaw = 0.12;
                }
                torsoPitch = 0.14;
              } else if (pStyle === "frantic") { // Nova: DevOps burst kilat, cek smartwatch
                const clk = elapsed * 28 * speed;
                lTyping = Math.sin(clk) * 0.14;
                rTyping = Math.cos(clk + 0.9) * 0.14;
                lWristFlick = Math.sin(clk) * 0.20;
                rWristFlick = Math.cos(clk) * 0.20;
                torsoPitch = 0.20;
                headPitch = 0.35;
                headYaw = Math.sin(elapsed * 3) * 0.05;
              } else if (pStyle === "hyperfocused") { // Kai: Keamanan intens, nunduk tajam
                const clk = elapsed * 24 * speed;
                lTyping = Math.sin(clk) * 0.11;
                rTyping = Math.cos(clk + 1.2) * 0.11;
                lWristFlick = Math.sin(clk) * 0.16;
                rWristFlick = Math.cos(clk) * 0.16;
                torsoPitch = 0.24; // Nunduk intens ke monitor
                headPitch = 0.38;
                headYaw = Math.sin(elapsed * 1.4) * 0.02;
              } else { // Ren & default: Tegas & audit
                const clk = elapsed * 22 * speed;
                lTyping = Math.sin(clk) * 0.11;
                rTyping = Math.cos(clk + 1.0) * 0.11;
                lWristFlick = Math.sin(clk) * 0.15;
                rWristFlick = Math.cos(clk) * 0.15;
                torsoPitch = 0.16;
                headPitch = 0.31;
                headYaw = Math.sin(elapsed * 1.5) * 0.03;
              }

              // Apply Articulation
              torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, torsoPitch, 0.08);
              headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, headPitch, 0.08);
              headGroup.rotation.y = THREE.MathUtils.lerp(headGroup.rotation.y, headYaw, 0.08);

              // Bahu menjangkau ke atas meja laptop
              leftShoulder.rotation.x = THREE.MathUtils.lerp(leftShoulder.rotation.x, -0.54 + lTyping * 0.4, 0.12);
              leftShoulder.rotation.z = THREE.MathUtils.lerp(leftShoulder.rotation.z, -0.16, 0.08);
              rightShoulder.rotation.x = THREE.MathUtils.lerp(rightShoulder.rotation.x, -0.54 + rTyping * 0.4, 0.12);
              rightShoulder.rotation.z = THREE.MathUtils.lerp(rightShoulder.rotation.z, 0.16, 0.08);

              // Siku menekuk tepat di ketinggian daun meja
              leftElbow.rotation.x = THREE.MathUtils.lerp(leftElbow.rotation.x, -0.92 + lTyping, 0.14);
              rightElbow.rotation.x = THREE.MathUtils.lerp(rightElbow.rotation.x, -0.92 + rTyping, 0.14);

              // Pergelangan tangan mengetik di tuts keyboard (Active Hands & Fingers!)
              if (leftWrist) {
                leftWrist.rotation.x = THREE.MathUtils.lerp(leftWrist.rotation.x, 0.28 + lWristFlick, 0.18);
                leftWrist.rotation.z = THREE.MathUtils.lerp(leftWrist.rotation.z, -0.12 + lTyping * 0.5, 0.14);
              }
              if (rightWrist) {
                rightWrist.rotation.x = THREE.MathUtils.lerp(rightWrist.rotation.x, 0.28 + rWristFlick, 0.18);
                rightWrist.rotation.z = THREE.MathUtils.lerp(rightWrist.rotation.z, 0.12 + rTyping * 0.5, 0.14);
              }

              deskObjects.displayMat.emissiveIntensity = 0.95 + Math.sin(elapsed * 9 * speed) * 0.18;
              deskObjects.lapLight.intensity = 1.1 + Math.sin(elapsed * 7 * speed) * 0.2;

              haloRing.material.opacity = THREE.MathUtils.lerp(haloRing.material.opacity, 0.85, 0.06);
              haloRing.rotation.z = elapsed * 1.2;
            } else {
              // --- UNIQUE PERSONALITY IDLE BEHAVIORS ---
              torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, -0.04, 0.05);
              torsoPivot.position.y = 0.52 + Math.sin(elapsed * 1.6 + id.charCodeAt(0)) * 0.012;

              if (pStyle === "furious") { // Zaki santai denger musik di headphone
                headGroup.rotation.x = 0.05 + Math.sin(elapsed * 4.5) * 0.04;
                headGroup.rotation.y = Math.sin(elapsed * 2.2) * 0.06;
              } else if (pStyle === "commanding") { // Risko memandang studio dengan tenang
                headGroup.rotation.x = 0.02;
                headGroup.rotation.y = Math.sin(elapsed * 0.8) * 0.15;
              } else {
                headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, 0.05, 0.05);
                headGroup.rotation.y = Math.sin(elapsed * 1.2 + id.charCodeAt(0)) * 0.08;
              }

              leftShoulder.rotation.set(-0.2, 0, -0.12);
              rightShoulder.rotation.set(-0.2, 0, 0.12);
              leftElbow.rotation.x = -0.5;
              rightElbow.rotation.x = -0.5;
              if (leftWrist) leftWrist.rotation.set(0, 0, 0);
              if (rightWrist) rightWrist.rotation.set(0, 0, 0);

              deskObjects.displayMat.emissiveIntensity = 0.45;
              deskObjects.lapLight.intensity = 0.45;
              haloRing.material.opacity = THREE.MathUtils.lerp(haloRing.material.opacity, 0, 0.08);
            }
          } else if (agent.currentMode === "MEETING") {
            coffeeCup.visible = false;
            const isStandingPresenter = id === "ren";
            if (isStandingPresenter) {
              leftLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(leftLeg.hipPivot.rotation.x, 0, 0.1);
              rightLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(rightLeg.hipPivot.rotation.x, 0, 0.1);
              leftLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(leftLeg.kneePivot.rotation.x, 0, 0.1);
              rightLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(rightLeg.kneePivot.rotation.x, 0, 0.1);
              torsoPivot.position.y = 0.52 + Math.sin(elapsed * 2) * 0.01;

              leftShoulder.rotation.set(-0.4 + Math.sin(elapsed * 2.5) * 0.25, 0, -0.3);
              rightShoulder.rotation.set(-0.7 + Math.cos(elapsed * 2.0) * 0.3, 0, 0.4);
              rightElbow.rotation.x = -0.8;
              headGroup.rotation.y = Math.sin(elapsed * 1.5) * 0.25;
            } else {
              leftLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(leftLeg.hipPivot.rotation.x, -Math.PI / 2, 0.1);
              rightLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(rightLeg.hipPivot.rotation.x, -Math.PI / 2, 0.1);
              leftLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(leftLeg.kneePivot.rotation.x, Math.PI / 2, 0.1);
              rightLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(rightLeg.kneePivot.rotation.x, Math.PI / 2, 0.1);

              torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, 0.08, 0.05);
              torsoPivot.position.y = 0.52 + Math.sin(elapsed * 1.4 + id.charCodeAt(0)) * 0.01;

              headGroup.rotation.x = Math.sin(elapsed * 1.8 + id.charCodeAt(0)) * 0.06;
              headGroup.rotation.y = Math.sin(elapsed * 0.8 + id.charCodeAt(0)) * 0.12;

              leftShoulder.rotation.set(-0.35, 0, -0.15);
              rightShoulder.rotation.set(-0.35, 0, 0.15);
              leftElbow.rotation.x = -0.7;
              rightElbow.rotation.x = -0.7;
            }
            deskObjects.displayMat.emissiveIntensity = 0.2;
            deskObjects.lapLight.intensity = 0.2;
            haloRing.material.opacity = THREE.MathUtils.lerp(haloRing.material.opacity, 0.3, 0.05);
          } else if (agent.currentMode === "LOUNGE") {
            coffeeCup.visible = true;
            const isStandingLounge = id === "kai" || id === "mika" || id === "ren";
            if (isStandingLounge) {
              leftLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(leftLeg.hipPivot.rotation.x, 0, 0.1);
              rightLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(rightLeg.hipPivot.rotation.x, 0, 0.1);
              leftLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(leftLeg.kneePivot.rotation.x, 0, 0.1);
              rightLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(rightLeg.kneePivot.rotation.x, 0, 0.1);
              torsoPivot.position.y = 0.52;
              torsoPivot.rotation.x = -0.02;
              headGroup.rotation.y = Math.sin(elapsed * 1.2 + id.charCodeAt(0)) * 0.2;

              rightShoulder.rotation.set(-0.6, 0, 0.2);
              rightElbow.rotation.x = -1.1;
              leftShoulder.rotation.set(-0.1, 0, -0.1);
            } else {
              leftLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(leftLeg.hipPivot.rotation.x, -Math.PI / 2, 0.1);
              rightLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(rightLeg.hipPivot.rotation.x, -Math.PI / 2, 0.1);
              leftLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(leftLeg.kneePivot.rotation.x, Math.PI / 2, 0.1);
              rightLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(rightLeg.kneePivot.rotation.x, Math.PI / 2, 0.1);

              torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, -0.14, 0.05);
              torsoPivot.position.y = 0.44 + Math.sin(elapsed * 1.2 + id.charCodeAt(0)) * 0.01;

              rightShoulder.rotation.set(-0.5, 0, 0.3);
              rightElbow.rotation.x = -1.0;
              leftShoulder.rotation.set(-0.1, 0, -0.2);
              leftElbow.rotation.x = -0.4;
            }
            haloRing.material.opacity = 0;
            deskObjects.displayMat.emissiveIntensity = 0.2;
            deskObjects.lapLight.intensity = 0.2;
          } else if (agent.currentMode === "PANTRY") {
            coffeeCup.visible = true;
            const isStool = id === "risko" || id === "pingot";
            if (isStool) {
              leftLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(leftLeg.hipPivot.rotation.x, -Math.PI / 2.6, 0.1);
              rightLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(rightLeg.hipPivot.rotation.x, -Math.PI / 2.6, 0.1);
              leftLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(leftLeg.kneePivot.rotation.x, Math.PI / 2.6, 0.1);
              rightLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(rightLeg.kneePivot.rotation.x, Math.PI / 2.6, 0.1);
              torsoPivot.position.y = 0.65;
            } else {
              leftLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(leftLeg.hipPivot.rotation.x, 0, 0.1);
              rightLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(rightLeg.hipPivot.rotation.x, 0, 0.1);
              leftLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(leftLeg.kneePivot.rotation.x, 0, 0.1);
              rightLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(rightLeg.kneePivot.rotation.x, 0, 0.1);
              torsoPivot.position.y = 0.52;
            }
            rightShoulder.rotation.set(-0.55 + Math.sin(elapsed * 1.5 + id.charCodeAt(0)) * 0.15, 0, 0.25);
            rightElbow.rotation.x = -1.1;
            leftShoulder.rotation.set(-0.15, 0, -0.15);
            leftElbow.rotation.x = -0.3;

            haloRing.material.opacity = 0;
            deskObjects.displayMat.emissiveIntensity = 0.2;
            deskObjects.lapLight.intensity = 0.2;
          }
        }

        const labelHeightOffset = agent.currentMode === "MEETING" 
          ? (id === "risko" || id === "ren" ? 2.32 : (id === "pingot" || id === "mika" ? 2.18 : 2.04))
          : 2.08;
        nameSprite.position.set(humanRoot.position.x, humanRoot.position.y + labelHeightOffset, humanRoot.position.z);
      });

      // ==========================================
      // BOS MUDA (PLAYER) LOCOMOTION & KINEMATICS & PROXIMITY
      // ==========================================
      if (playerRef.current) {
        const player = playerRef.current;
        const keys = keysPressedRef.current;
        let moveX = 0;
        let moveZ = 0;

        if (keys.w) moveZ -= 1;
        if (keys.s) moveZ += 1;
        if (keys.a) moveX -= 1;
        if (keys.d) moveX += 1;

        if (moveX !== 0 || moveZ !== 0) {
          player.targetDest = null;
          const len = Math.hypot(moveX, moveZ);
          const dirX = moveX / len;
          const dirZ = moveZ / len;
          const speed = keys.shift ? 7.8 : 4.6;

          player.pos.x += dirX * speed * delta;
          player.pos.z += dirZ * speed * delta;

          player.pos.x = THREE.MathUtils.clamp(player.pos.x, -14.2, 14.2);
          player.pos.z = THREE.MathUtils.clamp(player.pos.z, -12.6, 12.6);

          const targetAngle = Math.atan2(dirX, dirZ) + Math.PI;
          player.root.rotation.y = THREE.MathUtils.lerp(player.root.rotation.y, targetAngle, 0.22);
          player.isWalking = true;
        } else if (player.targetDest) {
          const tdx = player.targetDest.x - player.pos.x;
          const tdz = player.targetDest.z - player.pos.z;
          const tdist = Math.hypot(tdx, tdz);

          if (tdist < 0.25) {
            player.targetDest = null;
            player.isWalking = false;
          } else {
            const step = Math.min(tdist, 5.0 * delta);
            player.pos.x += (tdx / tdist) * step;
            player.pos.z += (tdz / tdist) * step;

            player.pos.x = THREE.MathUtils.clamp(player.pos.x, -14.2, 14.2);
            player.pos.z = THREE.MathUtils.clamp(player.pos.z, -12.6, 12.6);

            const targetAngle = Math.atan2(tdx, tdz) + Math.PI;
            player.root.rotation.y = THREE.MathUtils.lerp(player.root.rotation.y, targetAngle, 0.22);
            player.isWalking = true;
          }
        } else {
          player.isWalking = false;
        }

        if (player.isWalking) {
          player.walkCycle += delta * (keys.shift ? 14 : 9.5);
          player.leftLeg.hipPivot.rotation.x = Math.sin(player.walkCycle) * 0.72;
          player.rightLeg.hipPivot.rotation.x = -Math.sin(player.walkCycle) * 0.72;
          player.leftLeg.kneePivot.rotation.x = Math.max(0, -Math.sin(player.walkCycle)) * 0.65;
          player.rightLeg.kneePivot.rotation.x = Math.max(0, Math.sin(player.walkCycle)) * 0.65;
          player.leftArm.shoulder.rotation.x = -Math.sin(player.walkCycle) * 0.5;
          player.rightArm.shoulder.rotation.x = Math.sin(player.walkCycle) * 0.5;
          player.torsoPivot.position.y = 0.52 + Math.abs(Math.sin(player.walkCycle * 2)) * 0.025;
        } else {
          player.leftLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(player.leftLeg.hipPivot.rotation.x, 0, 0.15);
          player.rightLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(player.rightLeg.hipPivot.rotation.x, 0, 0.15);
          player.leftLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(player.leftLeg.kneePivot.rotation.x, 0, 0.15);
          player.rightLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(player.rightLeg.kneePivot.rotation.x, 0, 0.15);
          player.leftArm.shoulder.rotation.x = THREE.MathUtils.lerp(player.leftArm.shoulder.rotation.x, 0, 0.15);
          player.rightArm.shoulder.rotation.x = THREE.MathUtils.lerp(player.rightArm.shoulder.rotation.x, 0, 0.15);
          player.torsoPivot.position.y = 0.52 + Math.sin(elapsed * 2) * 0.008;
        }

        player.nameSprite.position.set(player.pos.x, 2.25, player.pos.z);
        player.haloRing.position.set(player.pos.x, 0.02, player.pos.z);
        player.haloRing.rotation.z += delta * 1.2;

        if (cameraModeRef.current === "player") {
          controls.target.lerp(new THREE.Vector3(player.pos.x, 1.2, player.pos.z), 0.08);
          const desiredCamPos = new THREE.Vector3(player.pos.x + 9.5, player.pos.y + 13.5, player.pos.z + 14.5);
          camera.position.lerp(desiredCamPos, 0.04);
        }

        let closest = null;
        let minDist = 3.2;

        Object.entries(agentMeshesRef.current).forEach(([aid, agent]) => {
          const adx = player.pos.x - agent.humanRoot.position.x;
          const adz = player.pos.z - agent.humanRoot.position.z;
          const dist = Math.hypot(adx, adz);

          if (dist < minDist) {
            minDist = dist;
            closest = {
              id: aid,
              name: AGENTS[aid]?.name || aid,
              role: AGENTS[aid]?.role || "",
              title: AGENTS[aid]?.title || "",
              color: AGENTS[aid]?.color || 0x6366f1,
              dialogue: AGENT_MINGLE_DIALOGUES[aid],
              dist: dist.toFixed(1),
            };

            const lookAngle = Math.atan2(adx, adz);
            agent.headGroup.rotation.y = THREE.MathUtils.lerp(agent.headGroup.rotation.y, lookAngle - agent.humanRoot.rotation.y, 0.15);
          }
        });

        nearAgentRef.current = closest;
        setNearAgent(closest);
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    const handleKeyDown = (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      const k = e.key.toLowerCase();
      if (k === "w" || e.key === "ArrowUp") keysPressedRef.current.w = true;
      if (k === "s" || e.key === "ArrowDown") keysPressedRef.current.s = true;
      if (k === "a" || e.key === "ArrowLeft") keysPressedRef.current.a = true;
      if (k === "d" || e.key === "ArrowRight") keysPressedRef.current.d = true;
      if (e.key === "Shift") keysPressedRef.current.shift = true;

      if (k === "e") {
        if (nearAgentRef.current) {
          setMingleModalAgent(nearAgentRef.current);
        }
      }

      if (k === "v") {
        setCameraMode((prev) => {
          const next = prev === "player" ? "orbit" : "player";
          cameraModeRef.current = next;
          return next;
        });
      }
    };

    const handleKeyUp = (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      const k = e.key.toLowerCase();
      if (k === "w" || e.key === "ArrowUp") keysPressedRef.current.w = false;
      if (k === "s" || e.key === "ArrowDown") keysPressedRef.current.s = false;
      if (k === "a" || e.key === "ArrowLeft") keysPressedRef.current.a = false;
      if (k === "d" || e.key === "ArrowRight") keysPressedRef.current.d = false;
      if (e.key === "Shift") keysPressedRef.current.shift = false;
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let pointerDownPos = { x: 0, y: 0 };

    const handlePointerDown = (e) => {
      pointerDownPos = { x: e.clientX, y: e.clientY };
    };

    const handlePointerUp = (e) => {
      const dist = Math.hypot(e.clientX - pointerDownPos.x, e.clientY - pointerDownPos.y);
      if (dist > 6) return;

      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
      const targetPoint = new THREE.Vector3();
      if (raycaster.ray.intersectPlane(plane, targetPoint)) {
        if (targetPoint.x >= -14.5 && targetPoint.x <= 14.5 && targetPoint.z >= -13 && targetPoint.z <= 13) {
          if (playerRef.current) {
            playerRef.current.targetDest = { x: targetPoint.x, z: targetPoint.z };
          }
        }
      }
    };

    renderer.domElement.addEventListener("pointerdown", handlePointerDown);
    renderer.domElement.addEventListener("pointerup", handlePointerUp);

    // Autonomous Smart Office Simulator
    const autoInterval = setInterval(() => {
      if (window.__officeMode !== "AUTONOMOUS") return;
      const idleAgents = Object.entries(agentMeshesRef.current).filter(
        ([, a]) => !a.isWorking && (!a.waypoints || a.waypoints.length === 0)
      );
      if (idleAgents.length > 0 && Math.random() < 0.45) {
        const [chosenId, chosenAgent] = idleAgents[Math.floor(Math.random() * idleAgents.length)];
        if (chosenAgent.currentMode === "WORK") {
          const destination = Math.random() < 0.5 ? "PANTRY" : "LOUNGE";
          if (agentNavRef.current) {
            agentNavRef.current(chosenId, destination);
            setAgentModes((prev) => ({ ...prev, [chosenId]: destination }));
          }
        } else {
          if (agentNavRef.current) {
            agentNavRef.current(chosenId, "WORK");
            setAgentModes((prev) => ({ ...prev, [chosenId]: "WORK" }));
          }
        }
      }
    }, 14000);

    // ==========================================
    // 🌐 WEBSOCKET LIVE SYNC DENGAN BACKEND DALANG
    // ==========================================
    let ws;
    const connectWS = () => {
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.hostname || "localhost";
      const wsUrl = `${proto}//${host}:8765/ws/events`;

      ws = new WebSocket(wsUrl);
      ws.onopen = () => {
        setConnected(true);
        console.log("WebSocket connected to Dalang-AI Orchestrator");
      };

      ws.onmessage = (e) => {
        try {
          const ev = JSON.parse(e.data);
          setEvents((prev) => [ev, ...prev.slice(0, 49)]);

          if (ev.event_type === "task_dispatched") {
            const agentMesh = agentMeshesRef.current[ev.agent];
            if (agentMesh) {
              agentMesh.isWorking = true;
              if (agentMesh.currentMode !== "WORK" && agentNavRef.current) {
                agentNavRef.current(ev.agent, "WORK");
                setAgentModes((m) => ({ ...m, [ev.agent]: "WORK" }));
              }
            }
            setWorkingMap((prev) => ({ ...prev, [ev.agent]: true }));
            setActiveTask({
              agent: ev.agent,
              task: ev.message,
              id: ev.plan_id || ev.task_id || "TASK-ACTIVE",
            });
          } else if (ev.event_type === "task_completed") {
            const agentMesh = agentMeshesRef.current[ev.agent];
            if (agentMesh) {
              agentMesh.isWorking = false;
            }
            setWorkingMap((prev) => ({ ...prev, [ev.agent]: false }));
          } else if (ev.event_type === "sprint_completed") {
            Object.values(agentMeshesRef.current).forEach((m) => {
              m.isWorking = false;
            });
            setWorkingMap({});
            setActiveTask(null);
          }
        } catch (err) {
          console.error("WS Parse error", err);
        }
      };

      ws.onerror = () => setConnected(false);
      ws.onclose = () => {
        setConnected(false);
        setTimeout(connectWS, 4000);
      };
    };

    connectWS();

    const fetchStatus = async () => {
      try {
        const host = window.location.hostname || "localhost";
        const res = await fetch(`http://${host}:8765/agents/status`);
        if (!res.ok) return;
        const data = await res.json();
        const statusMap = {};
        data.forEach((a) => {
          statusMap[a.agent] = a;
        });
        setAgentStatus(statusMap);
      } catch {
        // Backend offline
      }
    };

    fetchStatus();
    const iv = setInterval(fetchStatus, 3500);

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
      renderer.domElement.removeEventListener("pointerdown", handlePointerDown);
      renderer.domElement.removeEventListener("pointerup", handlePointerUp);
      clearInterval(autoInterval);
      clearInterval(iv);
      if (ws) ws.close();
      cancelAnimationFrame(animId);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Dispatch Real Task to Backend (Task-Driven Architecture)
  const handleDispatchTask = async (customTitle = null, customAgent = null) => {
    const title = (customTitle || taskInput).trim();
    if (!title) return;
    setIsDispatching(true);

    const agentChoice = customAgent || targetAgent;
    const host = window.location.hostname || "localhost";

    try {
      const res = await fetch(`http://${host}:8765/tasks/dispatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          agent: agentChoice === "auto" ? null : agentChoice,
          duration_seconds: 14,
        }),
      });

      if (res.ok) {
        await res.json();
        setTaskInput("");
      } else {
        console.error("Gagal mengirim tugas ke backend", res.status);
      }
    } catch (err) {
      console.error("Koneksi backend error saat kirim tugas", err);
    } finally {
      setIsDispatching(false);
    }
  };

  // Quick dispatch helper for cards
  const handleAssignToAgent = (agentId) => {
    const defaultActions = {
      zaki: "Mengembangkan endpoint auth JWT & API rate limiter",
      pingot: "Audit skema relasi database & migrasi index",
      lulu: "Mendesain antarmuka 3D visual & styling komponen dark mode",
      nova: "Menyiapkan pipeline CI/CD GitHub Actions & build docker",
      kai: "Audit keamanan OWASP Top 10 & scan vulnerabilitas",
      ren: "Menjalankan 182 test suite otomatis & validasi assertions",
      mika: "Menulis spesifikasi arsitektur & panduan teknis",
      risko: "Mengevaluasi lakon sprint & mengorkestrasi roadmap",
    };
    handleDispatchTask(defaultActions[agentId] || `Tugas pengembangan untuk ${AGENTS[agentId]?.name}`, agentId);
  };

  const handleAllMode = (mode) => {
    setOfficeMode(mode);
    Object.keys(AGENTS).forEach((id, idx) => {
      let targetLoc = mode;
      if (mode === "LOUNGE") {
        targetLoc = idx % 2 === 0 ? "LOUNGE" : "PANTRY";
      } else if (mode === "AUTONOMOUS") {
        targetLoc = "WORK";
      }
      if (agentNavRef.current) {
        agentNavRef.current(id, targetLoc);
      }
      setAgentModes((prev) => ({ ...prev, [id]: targetLoc }));
    });
  };

  const handleAgentNav = (agentId, targetLoc, e) => {
    if (e) e.stopPropagation();
    if (agentNavRef.current) {
      agentNavRef.current(agentId, targetLoc);
    }
    setAgentModes((prev) => ({ ...prev, [agentId]: targetLoc }));
  };

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      width: "100vw",
      height: "100vh",
      backgroundColor: "#08090a",
      color: "#f7f8f8",
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      fontFeatureSettings: "'cv01', 'ss03'",
      overflow: "hidden"
    }}>
      {/* 1. TOP SYSTEM DOCK (Linear-Engineered Header Bar) */}
      <header style={{
        height: 46,
        backgroundColor: "#08090a",
        borderBottom: "1px solid rgba(255, 255, 255, 0.07)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 18px",
        flexShrink: 0,
        zIndex: 20
      }}>
        {/* Brand & Connection State */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
            <span style={{ fontSize: "13px", fontWeight: "600", letterSpacing: "-0.02em", color: "#f7f8f8" }}>
              DALANG-AI
            </span>
            <span style={{ fontSize: "10px", fontFamily: "'JetBrains Mono', monospace", color: "#8a8f98", padding: "1px 5px", backgroundColor: "rgba(255,255,255,0.04)", borderRadius: 4, border: "1px solid rgba(255,255,255,0.06)" }}>
              STUDIO v1.0
            </span>
          </div>

          <div style={{ height: 14, width: 1, backgroundColor: "rgba(255, 255, 255, 0.08)" }} />

          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "11px", color: "#8a8f98" }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: connected ? "#10b981" : "#ef4444" }} />
            <span>{connected ? "Orchestrator Terhubung" : "Menghubungkan..."}</span>
          </div>
        </div>

        {/* Center: Mode Switcher (Discrete Segmented Control) */}
        <nav style={{
          display: "flex",
          alignItems: "center",
          gap: 2,
          backgroundColor: "#0f1011",
          padding: 3,
          borderRadius: 8,
          border: "1px solid rgba(255, 255, 255, 0.07)"
        }}>
          {[
            { id: "WORK", label: "Meja Kerja", icon: Laptop },
            { id: "MEETING", label: "Ruang Rapat", icon: Users },
            { id: "LOUNGE", label: "Lounge & Pantry", icon: Coffee },
            { id: "AUTONOMOUS", label: "Simulasi Otonom", icon: Sparkles },
          ].map((mode) => {
            const Icon = mode.icon;
            const isActive = officeMode === mode.id;
            return (
              <button
                key={mode.id}
                onClick={() => handleAllMode(mode.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "4px 10px",
                  borderRadius: 6,
                  border: isActive ? "1px solid rgba(255, 255, 255, 0.1)" : "1px solid transparent",
                  backgroundColor: isActive ? "rgba(255, 255, 255, 0.08)" : "transparent",
                  color: isActive ? "#f7f8f8" : "#8a8f98",
                  fontSize: "12px",
                  fontWeight: isActive ? "500" : "400",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                  outline: "none"
                }}
              >
                <Icon size={13} style={{ opacity: isActive ? 1 : 0.7 }} />
                <span>{mode.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Camera Perspective Mode Toggle (Bos Muda Follow vs Free Orbit) */}
        <button
          onClick={() => {
            const next = cameraMode === "player" ? "orbit" : "player";
            setCameraMode(next);
            cameraModeRef.current = next;
          }}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            padding: "4px 10px",
            borderRadius: 6,
            border: cameraMode === "player" ? "1px solid rgba(245, 158, 11, 0.45)" : "1px solid rgba(255, 255, 255, 0.08)",
            backgroundColor: cameraMode === "player" ? "rgba(245, 158, 11, 0.12)" : "#0f1011",
            color: cameraMode === "player" ? "#fbbf24" : "#8a8f98",
            fontSize: "12px",
            fontWeight: "500",
            cursor: "pointer",
            outline: "none",
            transition: "all 0.15s ease"
          }}
          title="Shortcut tombol [V] untuk beralih mode kamera"
        >
          {cameraMode === "player" ? <Crown size={13} color="#fbbf24" /> : <Eye size={13} />}
          <span>{cameraMode === "player" ? "Mode Bos Muda (Follow)" : "Orbit Bebas"}</span>
        </button>

        {/* Right: Telemetry Counts (JetBrains Mono) */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, fontFamily: "'JetBrains Mono', monospace", fontSize: "11px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, color: activeWayangCount > 0 ? "#7170ff" : "#8a8f98" }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: activeWayangCount > 0 ? "#7170ff" : "#62666d" }} />
            <span>{activeWayangCount} AKTIF</span>
          </div>
          <span style={{ color: "rgba(255, 255, 255, 0.1)" }}>/</span>
          <span style={{ color: "#8a8f98" }}>{8 - activeWayangCount} IDLE</span>
        </div>
      </header>

      {/* 2. BODY SPLIT: 3D Viewport (Left) + Inspector Sidebar (Right) */}
      <div style={{ display: "flex", flex: 1, minHeight: 0, position: "relative" }}>
        
        {/* LEFT: 3D Studio Canvas */}
        <div style={{ flex: 1, position: "relative", backgroundColor: "#08090a", overflow: "hidden" }}>
          <div ref={mountRef} style={{ width: "100%", height: "100%" }} />

          {/* 🎮 Virtual On-Screen Controls for Bos Muda (Bottom-Left) */}
          <div style={{
            position: "absolute",
            bottom: 20,
            left: 20,
            zIndex: 15,
            backgroundColor: "rgba(15, 16, 17, 0.88)",
            backdropFilter: "blur(8px)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: 8,
            padding: "10px 12px",
            display: "flex",
            flexDirection: "column",
            gap: 8,
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
            pointerEvents: "auto"
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "11px", fontWeight: "600", color: "#fbbf24" }}>
                <Crown size={12} />
                <span>KENDALI BOS MUDA</span>
              </div>
              <span style={{ fontSize: "9px", fontFamily: "'JetBrains Mono', monospace", color: "#8a8f98" }}>
                WASD / PANAH
              </span>
            </div>

            {/* Virtual Directional D-Pad */}
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
              <button
                onMouseDown={() => { keysPressedRef.current.w = true; }}
                onMouseUp={() => { keysPressedRef.current.w = false; }}
                onTouchStart={() => { keysPressedRef.current.w = true; }}
                onTouchEnd={() => { keysPressedRef.current.w = false; }}
                style={{
                  width: 32,
                  height: 28,
                  backgroundColor: "rgba(255, 255, 255, 0.06)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  borderRadius: 4,
                  color: "#f7f8f8",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer"
                }}
                title="Maju (W / Panah Atas)"
              >
                <ArrowUp size={13} />
              </button>

              <div style={{ display: "flex", gap: 4 }}>
                <button
                  onMouseDown={() => { keysPressedRef.current.a = true; }}
                  onMouseUp={() => { keysPressedRef.current.a = false; }}
                  onTouchStart={() => { keysPressedRef.current.a = true; }}
                  onTouchEnd={() => { keysPressedRef.current.a = false; }}
                  style={{
                    width: 32,
                    height: 28,
                    backgroundColor: "rgba(255, 255, 255, 0.06)",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    borderRadius: 4,
                    color: "#f7f8f8",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer"
                  }}
                  title="Kiri (A / Panah Kiri)"
                >
                  <ArrowLeft size={13} />
                </button>

                <button
                  onMouseDown={() => { keysPressedRef.current.s = true; }}
                  onMouseUp={() => { keysPressedRef.current.s = false; }}
                  onTouchStart={() => { keysPressedRef.current.s = true; }}
                  onTouchEnd={() => { keysPressedRef.current.s = false; }}
                  style={{
                    width: 32,
                    height: 28,
                    backgroundColor: "rgba(255, 255, 255, 0.06)",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    borderRadius: 4,
                    color: "#f7f8f8",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer"
                  }}
                  title="Mundur (S / Panah Bawah)"
                >
                  <ArrowDown size={13} />
                </button>

                <button
                  onMouseDown={() => { keysPressedRef.current.d = true; }}
                  onMouseUp={() => { keysPressedRef.current.d = false; }}
                  onTouchStart={() => { keysPressedRef.current.d = true; }}
                  onTouchEnd={() => { keysPressedRef.current.d = false; }}
                  style={{
                    width: 32,
                    height: 28,
                    backgroundColor: "rgba(255, 255, 255, 0.06)",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    borderRadius: 4,
                    color: "#f7f8f8",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer"
                  }}
                  title="Kanan (D / Panah Kanan)"
                >
                  <ArrowRight size={13} />
                </button>
              </div>
            </div>

            <div style={{ fontSize: "10px", color: "#8a8f98", lineHeight: 1.4, textAlign: "center" }}>
              Klik lantai untuk jalan cepat<br />
              Tahan <span style={{ color: "#d0d6e0", fontFamily: "monospace" }}>[Shift]</span> untuk lari
            </div>
          </div>

          {/* 💬 Proximity Interaction Floating Banner (When near an Employee) */}
          {nearAgent && (
            <div
              onClick={() => setMingleModalAgent(nearAgent)}
              style={{
                position: "absolute",
                bottom: 84,
                left: "50%",
                transform: "translateX(-50%)",
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                border: "1px solid rgba(245, 158, 11, 0.5)",
                boxShadow: "0 10px 30px rgba(0, 0, 0, 0.7), 0 0 16px rgba(245, 158, 11, 0.25)",
                borderRadius: 24,
                padding: "8px 18px",
                display: "flex",
                alignItems: "center",
                gap: 10,
                zIndex: 25,
                cursor: "pointer",
                transition: "all 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
                animation: "pulse 2s infinite"
              }}
            >
              <div style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: "#fbbf24",
                boxShadow: "0 0 8px #fbbf24"
              }} />
              <div style={{ fontSize: "12px", color: "#f8fafc", fontWeight: "500" }}>
                Dekat dengan <span style={{ color: "#fbbf24", fontWeight: "600" }}>{nearAgent.name}</span> ({nearAgent.role})
              </div>
              <div style={{
                fontSize: "11px",
                padding: "2px 8px",
                backgroundColor: "rgba(245, 158, 11, 0.2)",
                border: "1px solid rgba(245, 158, 11, 0.4)",
                borderRadius: 12,
                color: "#fef08a",
                fontWeight: "600",
                letterSpacing: "0.02em"
              }}>
                [E] Tekan untuk Berbaur
              </div>
            </div>
          )}

          {/* Integrated Linear-Style Command Dock (Bottom Center) */}
          <div style={{
            position: "absolute",
            bottom: 18,
            left: "50%",
            transform: "translateX(-50%)",
            width: "min(720px, 94%)",
            backgroundColor: "#0f1011",
            border: "1px solid rgba(255, 255, 255, 0.09)",
            borderRadius: 8,
            boxShadow: "0 12px 32px -4px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(255, 255, 255, 0.04)",
            display: "flex",
            flexDirection: "column",
            zIndex: 10,
            overflow: "hidden"
          }}>
            {/* Active Task Banner if running */}
            {activeTask && (
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "6px 14px",
                backgroundColor: "rgba(94, 106, 210, 0.08)",
                borderBottom: "1px solid rgba(94, 106, 210, 0.15)",
                fontSize: "11px"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: "#7170ff" }} />
                  <span style={{ fontWeight: "500", color: "#f7f8f8" }}>
                    {AGENTS[activeTask.agent]?.name} ({AGENTS[activeTask.agent]?.role})
                  </span>
                  <span style={{ color: "#8a8f98" }}>•</span>
                  <span style={{ color: "#d0d6e0", maxWidth: 360, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {activeTask.task}
                  </span>
                </div>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", color: "#7170ff", fontSize: "10px", fontWeight: "500" }}>
                  MENGETIK
                </span>
              </div>
            )}

            {/* Input Bar */}
            <div style={{ display: "flex", alignItems: "center", padding: "8px 12px", gap: 8 }}>
              <input
                type="text"
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleDispatchTask()}
                placeholder="Perintahkan tugas (misal: 'Zaki buat endpoint auth JWT' atau 'Audit celah keamanan')..."
                style={{
                  flex: 1,
                  backgroundColor: "transparent",
                  border: "none",
                  outline: "none",
                  color: "#f7f8f8",
                  fontSize: "13px",
                  fontFamily: "'Inter', sans-serif",
                }}
              />

              <select
                value={targetAgent}
                onChange={(e) => setTargetAgent(e.target.value)}
                style={{
                  backgroundColor: "rgba(255, 255, 255, 0.04)",
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                  borderRadius: 6,
                  padding: "4px 8px",
                  color: "#d0d6e0",
                  fontSize: "11px",
                  cursor: "pointer",
                  outline: "none"
                }}
              >
                <option value="auto">Auto-Route (Risko)</option>
                <option value="zaki">Zaki (Backend)</option>
                <option value="pingot">Pingot (Data)</option>
                <option value="lulu">Lulu (Visual UI)</option>
                <option value="kai">Kai (Security)</option>
                <option value="ren">Ren (QA Test)</option>
                <option value="nova">Nova (DevOps)</option>
                <option value="mika">Mika (Pujangga)</option>
                <option value="risko">Risko (Dalang)</option>
              </select>

              <button
                onClick={() => handleDispatchTask()}
                disabled={isDispatching || !taskInput.trim()}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 5,
                  padding: "5px 12px",
                  borderRadius: 6,
                  border: "none",
                  backgroundColor: isDispatching || !taskInput.trim() ? "rgba(255, 255, 255, 0.05)" : "#5e6ad2",
                  color: isDispatching || !taskInput.trim() ? "#62666d" : "#ffffff",
                  fontSize: "12px",
                  fontWeight: "500",
                  cursor: isDispatching || !taskInput.trim() ? "not-allowed" : "pointer",
                  transition: "background 0.15s ease"
                }}
              >
                <Send size={12} />
                <span>{isDispatching ? "Mengirim..." : "Tugaskan"}</span>
              </button>
            </div>

            {/* Quick Dispatch Chips */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "4px 12px 8px",
              borderTop: "1px solid rgba(255, 255, 255, 0.04)",
              overflowX: "auto"
            }}>
              <span style={{ fontSize: "10px", color: "#62666d", textTransform: "uppercase", letterSpacing: "0.04em", whiteSpace: "nowrap" }}>
                Rekomendasi:
              </span>
              {[
                { label: "API Auth JWT", task: "Buat endpoint autentikasi JWT dan middleware token", agent: "zaki" },
                { label: "Audit OWASP", task: "Audit keamanan celah OWASP & token validation", agent: "kai" },
                { label: "UI Dark Mode", task: "Mendesain antarmuka dashboard dark mode responsif", agent: "lulu" },
                { label: "Skema Database", task: "Audit relasi skema database & migrasi tabel", agent: "pingot" },
                { label: "Run Test Suite", task: "Jalankan 182 test suite otomatis & validasi assertions", agent: "ren" },
              ].map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => handleDispatchTask(chip.task, chip.agent)}
                  style={{
                    backgroundColor: "rgba(255, 255, 255, 0.02)",
                    border: "1px solid rgba(255, 255, 255, 0.06)",
                    borderRadius: 4,
                    padding: "2px 7px",
                    color: "#8a8f98",
                    fontSize: "11px",
                    cursor: "pointer",
                    whiteSpace: "nowrap",
                    transition: "all 0.12s ease"
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
                    e.currentTarget.style.color = "#d0d6e0";
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.02)";
                    e.currentTarget.style.color = "#8a8f98";
                  }}
                >
                  {chip.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT: Inspector Sidebar (Clean Engineering Roster & Terminal Log) */}
        <aside style={{
          width: 360,
          backgroundColor: "#08090a",
          borderLeft: "1px solid rgba(255, 255, 255, 0.07)",
          display: "flex",
          flexDirection: "column",
          flexShrink: 0
        }}>
          {/* Panel Header */}
          <div style={{
            padding: "14px 18px",
            borderBottom: "1px solid rgba(255, 255, 255, 0.07)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}>
            <div>
              <div style={{ fontSize: "13px", fontWeight: "600", color: "#f7f8f8", letterSpacing: "-0.01em" }}>
                Tim Wayang
              </div>
              <div style={{ fontSize: "11px", color: "#8a8f98", marginTop: 2 }}>
                Status kerja otonom berbasis antrean tugas
              </div>
            </div>
            <span style={{ fontSize: "10px", fontFamily: "'JetBrains Mono', monospace", color: "#8a8f98", padding: "2px 6px", backgroundColor: "rgba(255,255,255,0.03)", borderRadius: 4, border: "1px solid rgba(255,255,255,0.06)" }}>
              8 AGEN
            </span>
          </div>

          {/* Wayang Cards (Zero Accent-Rail Slop, Linear Clean Item Style) */}
          <div style={{ flex: 1, overflowY: "auto", padding: "10px 14px", display: "flex", flexDirection: "column", gap: 6 }}>
            {Object.entries(AGENTS).map(([id, info]) => {
              const isWorking = Boolean(workingMap[id]);
              return (
                <div
                  key={id}
                  onClick={() => setSelectedAgentDetail({ id, ...info })}
                  style={{
                    padding: "10px 12px",
                    borderRadius: 6,
                    backgroundColor: isWorking ? "rgba(94, 106, 210, 0.06)" : "rgba(255, 255, 255, 0.02)",
                    border: isWorking ? "1px solid rgba(94, 106, 210, 0.28)" : "1px solid rgba(255, 255, 255, 0.05)",
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                  onMouseOver={(e) => {
                    if (!isWorking) e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.04)";
                  }}
                  onMouseOut={(e) => {
                    if (!isWorking) e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.02)";
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        backgroundColor: isWorking ? "#10b981" : "#45474c"
                      }} />
                      <span style={{ fontSize: "13px", fontWeight: "500", color: "#f7f8f8" }}>
                        {info.name}
                      </span>
                      <span style={{ fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", color: "#8a8f98" }}>
                        {info.role}
                      </span>
                    </div>

                    <span style={{
                      fontSize: "10px",
                      fontFamily: "'JetBrains Mono', monospace",
                      fontWeight: "500",
                      padding: "1px 6px",
                      borderRadius: 4,
                      backgroundColor: isWorking ? "rgba(16, 185, 129, 0.12)" : "rgba(255, 255, 255, 0.03)",
                      color: isWorking ? "#10b981" : "#62666d",
                      border: isWorking ? "1px solid rgba(16, 185, 129, 0.25)" : "1px solid rgba(255, 255, 255, 0.04)"
                    }}>
                      {isWorking ? "NGETIK" : "IDLE"}
                    </span>
                  </div>

                  <div style={{ fontSize: "11px", color: "#8a8f98", marginTop: 4, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {info.personality}
                  </div>

                  {/* Card Controls */}
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 8, paddingTop: 6, borderTop: "1px solid rgba(255, 255, 255, 0.04)" }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAssignToAgent(id);
                      }}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 4,
                        backgroundColor: isWorking ? "rgba(94, 106, 210, 0.12)" : "rgba(255, 255, 255, 0.03)",
                        border: isWorking ? "1px solid rgba(94, 106, 210, 0.25)" : "1px solid rgba(255, 255, 255, 0.06)",
                        borderRadius: 4,
                        padding: "2px 7px",
                        color: isWorking ? "#828fff" : "#d0d6e0",
                        fontSize: "11px",
                        cursor: "pointer"
                      }}
                    >
                      <PlusCircle size={11} />
                      <span>{isWorking ? "Tugas Lain" : "Tugaskan"}</span>
                    </button>

                    <div style={{ display: "flex", gap: 3 }}>
                      {[
                        { loc: "WORK", label: "Meja" },
                        { loc: "MEETING", label: "Rapat" },
                        { loc: "LOUNGE", label: "Sofa" },
                        { loc: "PANTRY", label: "Pantry" },
                      ].map((btn) => (
                        <button
                          key={btn.loc}
                          onClick={(e) => handleAgentNav(id, btn.loc, e)}
                          style={{
                            fontSize: "10px",
                            padding: "2px 5px",
                            borderRadius: 4,
                            backgroundColor: agentModes[id] === btn.loc ? "rgba(255, 255, 255, 0.08)" : "transparent",
                            color: agentModes[id] === btn.loc ? "#f7f8f8" : "#62666d",
                            border: agentModes[id] === btn.loc ? "1px solid rgba(255, 255, 255, 0.1)" : "1px solid transparent",
                            cursor: "pointer"
                          }}
                        >
                          {btn.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Studio Audit Stream (Compact Terminal Log) */}
          <div style={{
            height: 180,
            backgroundColor: "#050607",
            borderTop: "1px solid rgba(255, 255, 255, 0.07)",
            padding: "10px 14px",
            display: "flex",
            flexDirection: "column"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <span style={{ fontSize: "10px", fontFamily: "'JetBrains Mono', monospace", color: "#62666d", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Audit Log Studio
              </span>
              <span style={{ width: 5, height: 5, borderRadius: "50%", backgroundColor: connected ? "#10b981" : "#ef4444" }} />
            </div>

            <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 4, fontFamily: "'JetBrains Mono', monospace", fontSize: "11px" }}>
              {events.length === 0 ? (
                <div style={{ color: "#45474c", margin: "auto 0", textAlign: "center" }}>
                  Menunggu lakon tugas...
                </div>
              ) : (
                events.slice(0, 20).map((ev, i) => (
                  <div key={i} style={{ color: "#8a8f98", lineHeight: 1.4 }}>
                    <span style={{ color: "#62666d", marginRight: 6 }}>
                      {new Date(ev.timestamp || Date.now()).toLocaleTimeString()}
                    </span>
                    <span style={{ color: "#7170ff", marginRight: 6, fontWeight: "500" }}>
                      [{ev.agent?.toUpperCase() || "DALANG"}]
                    </span>
                    <span style={{ color: "#d0d6e0" }}>{ev.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>
      </div>

      {/* 👑 MODAL BERBAUR DENGAN KARYAWAN (Interaksi Tatap Muka Bos Muda) */}
      {mingleModalAgent && (
        <div
          onClick={() => setMingleModalAgent(null)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            backgroundColor: "rgba(0, 0, 0, 0.76)",
            backdropFilter: "blur(6px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 110,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              backgroundColor: "#0d0f12",
              border: "1px solid rgba(245, 158, 11, 0.35)",
              borderRadius: 12,
              padding: "24px 28px",
              width: "min(480px, 94%)",
              boxShadow: "0 24px 64px -8px rgba(0, 0, 0, 0.85), 0 0 24px rgba(245, 158, 11, 0.12)",
              display: "flex",
              flexDirection: "column",
              gap: 16
            }}
          >
            {/* Header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  backgroundColor: "rgba(245, 158, 11, 0.12)",
                  border: "1px solid rgba(245, 158, 11, 0.3)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#fbbf24"
                }}>
                  <Crown size={18} />
                </div>
                <div>
                  <div style={{ fontSize: "16px", fontWeight: "600", color: "#f7f8f8" }}>
                    Berbincang dengan {mingleModalAgent.name}
                  </div>
                  <div style={{ fontSize: "12px", fontFamily: "'JetBrains Mono', monospace", color: "#fbbf24" }}>
                    {mingleModalAgent.role} • {mingleModalAgent.title}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setMingleModalAgent(null)}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "#8a8f98",
                  fontSize: "16px",
                  cursor: "pointer",
                  padding: "4px 8px"
                }}
              >
                ✕
              </button>
            </div>

            {/* Conversation Speech Box */}
            <div style={{
              backgroundColor: "rgba(255, 255, 255, 0.03)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              borderRadius: 8,
              padding: "14px 16px",
              display: "flex",
              flexDirection: "column",
              gap: 8
            }}>
              <div style={{ fontSize: "13px", fontWeight: "500", color: "#e2e8f0" }}>
                "{mingleModalAgent.dialogue?.greeting}"
              </div>
              <div style={{ fontSize: "13px", color: "#94a3b8", lineHeight: 1.6, fontStyle: "italic" }}>
                "{mingleModalAgent.dialogue?.quote}"
              </div>
              <div style={{
                marginTop: 4,
                paddingTop: 8,
                borderTop: "1px solid rgba(255, 255, 255, 0.05)",
                fontSize: "11px",
                color: "#64748b"
              }}>
                💡 {mingleModalAgent.dialogue?.tip}
              </div>
            </div>

            {/* Interactive Actions with Employee */}
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div style={{ fontSize: "11px", fontWeight: "600", color: "#8a8f98", letterSpacing: "0.04em" }}>
                AKSI BERSAMA BOS MUDA:
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                <button
                  onClick={() => {
                    handleAgentNav(mingleModalAgent.id, "PANTRY");
                    setMingleModalAgent(null);
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "8px 12px",
                    borderRadius: 6,
                    backgroundColor: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid rgba(255, 255, 255, 0.08)",
                    color: "#f8fafc",
                    fontSize: "12px",
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                >
                  <Coffee size={14} color="#f59e0b" />
                  <span>Ajak Ngopi di Pantry</span>
                </button>

                <button
                  onClick={() => {
                    handleAgentNav(mingleModalAgent.id, "MEETING");
                    setMingleModalAgent(null);
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "8px 12px",
                    borderRadius: 6,
                    backgroundColor: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid rgba(255, 255, 255, 0.08)",
                    color: "#f8fafc",
                    fontSize: "12px",
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                >
                  <Users size={14} color="#38bdf8" />
                  <span>Ajak Rapat di War Room</span>
                </button>

                <button
                  onClick={() => {
                    handleAgentNav(mingleModalAgent.id, "LOUNGE");
                    setMingleModalAgent(null);
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "8px 12px",
                    borderRadius: 6,
                    backgroundColor: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid rgba(255, 255, 255, 0.08)",
                    color: "#f8fafc",
                    fontSize: "12px",
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                >
                  <Sparkles size={14} color="#a855f7" />
                  <span>Ajak Santai di Lounge</span>
                </button>

                <button
                  onClick={() => {
                    handleAgentNav(mingleModalAgent.id, "WORK");
                    setMingleModalAgent(null);
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "8px 12px",
                    borderRadius: 6,
                    backgroundColor: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid rgba(255, 255, 255, 0.08)",
                    color: "#f8fafc",
                    fontSize: "12px",
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                >
                  <Laptop size={14} color="#10b981" />
                  <span>Kembali ke Meja Kerja</span>
                </button>
              </div>
            </div>

            {/* Direct Task Assignment & Close */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 4 }}>
              <button
                onClick={() => {
                  handleAssignToAgent(mingleModalAgent.id);
                  setMingleModalAgent(null);
                }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "6px 14px",
                  borderRadius: 6,
                  backgroundColor: "rgba(94, 106, 210, 0.15)",
                  border: "1px solid rgba(94, 106, 210, 0.35)",
                  color: "#a5b4fc",
                  fontSize: "12px",
                  fontWeight: "500",
                  cursor: "pointer"
                }}
              >
                <Send size={12} />
                <span>Beri Tugas Langsung</span>
              </button>

              <button
                onClick={() => setMingleModalAgent(null)}
                style={{
                  padding: "6px 14px",
                  borderRadius: 6,
                  backgroundColor: "rgba(255, 255, 255, 0.06)",
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  color: "#d0d6e0",
                  fontSize: "12px",
                  cursor: "pointer"
                }}
              >
                Tutup Obrolan
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. MODAL DETAIL WAYANG (Linear Dialog Standard) */}
      {selectedAgentDetail && (
        <div
          onClick={() => setSelectedAgentDetail(null)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            backgroundColor: "rgba(0, 0, 0, 0.72)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              backgroundColor: "#0f1011",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: 8,
              padding: "20px 24px",
              width: "min(420px, 92%)",
              boxShadow: "0 20px 48px -8px rgba(0, 0, 0, 0.8)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 12 }}>
              <h3 style={{ margin: 0, fontSize: "16px", color: "#f7f8f8", fontWeight: "600" }}>
                {selectedAgentDetail.name}
              </h3>
              <span style={{ fontSize: "12px", fontFamily: "'JetBrains Mono', monospace", color: "#8a8f98" }}>
                {selectedAgentDetail.role}
              </span>
            </div>

            <div style={{ fontSize: "12px", color: "#8a8f98", lineHeight: 1.6, marginBottom: 16 }}>
              <div><strong style={{ color: "#d0d6e0" }}>Gelar:</strong> {selectedAgentDetail.title}</div>
              <div style={{ marginTop: 4 }}><strong style={{ color: "#d0d6e0" }}>Kepribadian:</strong> {selectedAgentDetail.personality}</div>
              <div style={{ marginTop: 4 }}><strong style={{ color: "#d0d6e0" }}>Spesialisasi:</strong> {selectedAgentDetail.action}</div>
              <div style={{ marginTop: 10, padding: "8px 10px", borderRadius: 6, backgroundColor: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.05)" }}>
                <strong style={{ color: "#d0d6e0" }}>Status:</strong>{" "}
                <span style={{ color: workingMap[selectedAgentDetail.id] ? "#10b981" : "#8a8f98", fontWeight: "500" }}>
                  {workingMap[selectedAgentDetail.id] ? "Aktif Mengetik (Menyelesaikan Tugas)" : "Istirahat (Siap Menerima Tugas)"}
                </span>
              </div>
            </div>

            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button
                onClick={() => setSelectedAgentDetail(null)}
                style={{
                  padding: "6px 12px",
                  borderRadius: 6,
                  backgroundColor: "rgba(255, 255, 255, 0.04)",
                  color: "#8a8f98",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                  cursor: "pointer",
                  fontSize: "12px",
                }}
              >
                Tutup
              </button>
              <button
                onClick={() => {
                  handleAssignToAgent(selectedAgentDetail.id);
                  setSelectedAgentDetail(null);
                }}
                style={{
                  padding: "6px 14px",
                  borderRadius: 6,
                  backgroundColor: "#5e6ad2",
                  color: "#ffffff",
                  border: "none",
                  cursor: "pointer",
                  fontSize: "12px",
                  fontWeight: "500",
                }}
              >
                Tugaskan Sekarang
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}