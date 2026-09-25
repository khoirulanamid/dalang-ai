import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { Sparkles, Coffee, Users, Laptop } from "lucide-react";

// 8 Para Wayang Roster & Detailed Office Profiles
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
  },
};

// Procedural Parquet Wood Floor Texture (MengTo Standard PBR)
function createParquetTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 1024;
  const ctx = canvas.getContext("2d");

  // Warm Oak Base
  ctx.fillStyle = "#8a6642";
  ctx.fillRect(0, 0, 1024, 1024);

  const plankW = 128;
  const plankH = 32;

  for (let y = 0; y < 1024; y += plankH) {
    const rowOffset = (Math.floor(y / plankH) % 2) * (plankW / 2);
    for (let x = -plankW; x < 1024 + plankW; x += plankW) {
      const px = x + rowOffset;
      const shade = ((Math.sin(px * 12.3 + y * 7.1) + 1) / 2) * 22;
      const r = Math.floor(138 + shade);
      const g = Math.floor(102 + shade * 0.8);
      const b = Math.floor(66 + shade * 0.6);
      ctx.fillStyle = `rgb(${r},${g},${b})`;
      ctx.fillRect(px + 1, y + 1, plankW - 2, plankH - 2);

      // Plank Grain
      ctx.strokeStyle = `rgba(0, 0, 0, 0.08)`;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(px, y + plankH * 0.35);
      ctx.lineTo(px + plankW, y + plankH * 0.35);
      ctx.moveTo(px, y + plankH * 0.7);
      ctx.lineTo(px + plankW, y + plankH * 0.7);
      ctx.stroke();

      // Border Bevel
      ctx.strokeStyle = "rgba(40, 25, 12, 0.35)";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(px, y, plankW, plankH);
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(2, 2);
  return texture;
}

// Procedural Scandinavian Area Rug Texture
function createRugTexture(baseColorHex, patternColorHex) {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = baseColorHex;
  ctx.fillRect(0, 0, 512, 512);

  ctx.strokeStyle = patternColorHex;
  ctx.lineWidth = 4;
  for (let i = -512; i < 1024; i += 64) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i + 512, 512);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(i + 512, 0);
    ctx.lineTo(i, 512);
    ctx.stroke();
  }

  ctx.strokeStyle = patternColorHex;
  ctx.lineWidth = 16;
  ctx.strokeRect(8, 8, 496, 496);

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
    risko: { pos: [14.5, 0, -4.0], rotY: 0 },
    pingot: { pos: [13.2, 0, -5.2], rotY: Math.PI / 2 },
    zaki: { pos: [13.2, 0, -6.5], rotY: Math.PI / 2 },
    lulu: { pos: [13.2, 0, -7.8], rotY: Math.PI / 2 },
    mika: { pos: [15.8, 0, -5.2], rotY: -Math.PI / 2 },
    nova: { pos: [15.8, 0, -6.5], rotY: -Math.PI / 2 },
    kai: { pos: [15.8, 0, -7.8], rotY: -Math.PI / 2 },
    ren: { pos: [14.5, 0, -9.8], rotY: Math.PI },
  },
  LOUNGE: {
    risko: { pos: [7.2, 0, 7.3], rotY: 0 },
    lulu: { pos: [8.4, 0, 7.3], rotY: 0 },
    pingot: { pos: [9.6, 0, 7.3], rotY: 0 },
    zaki: { pos: [9.6, 0, 5.8], rotY: -Math.PI / 2 },
    mika: { pos: [6.6, 0, 6.2], rotY: Math.PI / 4 },
    nova: { pos: [10.6, 0, 7.8], rotY: -Math.PI / 3 },
    kai: { pos: [7.5, 0, 5.5], rotY: Math.PI },
    ren: { pos: [8.6, 0, 5.5], rotY: Math.PI },
  },
  PANTRY: {
    risko: { pos: [-11.2, 0, -6.1], rotY: 0 },
    pingot: { pos: [-12.8, 0, -6.1], rotY: 0 },
    lulu: { pos: [-13.4, 0, -6.8], rotY: Math.PI / 2 },
    zaki: { pos: [-10.2, 0, -7.2], rotY: Math.PI },
    mika: { pos: [-14.2, 0, -6.5], rotY: 0 },
    nova: { pos: [-9.6, 0, -5.8], rotY: -Math.PI / 3 },
    kai: { pos: [-12.0, 0, -4.8], rotY: 0 },
    ren: { pos: [-13.2, 0, -4.8], rotY: 0 },
  },
};

function getWaypoints(startPos, endPos) {
  const wps = [];
  const sx = startPos.x;
  const sz = startPos.z;
  const ex = endPos.x;
  const ez = endPos.z;

  const isStartInMeeting = sx > 12.0;
  const isEndInMeeting = ex > 12.0;

  if (isStartInMeeting && !isEndInMeeting) {
    wps.push(new THREE.Vector3(14.5, 0, 0));
    wps.push(new THREE.Vector3(11.5, 0, 0));
    wps.push(new THREE.Vector3(ex, 0, 0));
    wps.push(new THREE.Vector3(ex, 0, ez));
    return wps;
  }

  if (!isStartInMeeting && isEndInMeeting) {
    wps.push(new THREE.Vector3(sx, 0, 0));
    wps.push(new THREE.Vector3(11.5, 0, 0));
    wps.push(new THREE.Vector3(14.5, 0, 0));
    wps.push(new THREE.Vector3(ex, 0, ez));
    return wps;
  }

  if (Math.hypot(ex - sx, ez - sz) > 1.2) {
    wps.push(new THREE.Vector3(sx, 0, 0));
    wps.push(new THREE.Vector3(ex, 0, 0));
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

    const camera = new THREE.PerspectiveCamera(36, width / height, 0.1, 1000);
    camera.position.set(22, 24, 28);
    camera.lookAt(0, 1.2, 0);

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

    // 1. Warm Oak Parquet Floor
    const parquetTexture = createParquetTexture();
    const floorGeo = new THREE.PlaneGeometry(32, 28);
    const floorMat = new THREE.MeshStandardMaterial({
      map: parquetTexture,
      roughness: 0.62,
      metalness: 0.05,
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    roomGroup.add(floor);

    // 2. Central Scandinavian Area Rug
    const rugTexture = createRugTexture("#1e293b", "#334155");
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

    // 3. Back Wall (Dark Slate Architect Wall)
    const backWallGeo = new THREE.BoxGeometry(32, 5.8, 0.4);
    const wallMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.88 });
    const backWall = new THREE.Mesh(backWallGeo, wallMat);
    backWall.position.set(0, 2.9, -14);
    backWall.receiveShadow = true;
    roomGroup.add(backWall);

    // Left Wall with Big Industrial Daylight Windows
    const leftWallGeo = new THREE.BoxGeometry(0.4, 5.8, 28);
    const leftWall = new THREE.Mesh(leftWallGeo, wallMat);
    leftWall.position.set(-16, 2.9, 0);
    leftWall.receiveShadow = true;
    roomGroup.add(leftWall);

    // Baseboards
    const baseboardGeo = new THREE.BoxGeometry(32, 0.25, 0.45);
    const baseboardMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5 });
    const baseboard = new THREE.Mesh(baseboardGeo, baseboardMat);
    baseboard.position.set(0, 0.125, -13.8);
    roomGroup.add(baseboard);

    // 4. Large Sunlight Windows on Left Wall
    const windowFrameGeo = new THREE.BoxGeometry(0.3, 3.4, 12);
    const windowFrameMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.85, roughness: 0.25 });
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

    // 5. Frameless Glass Partition Wall (Meeting Room Boundary) with Doorway
    // Section 1: South Glass Wall (z = -9.5 to z = -1.5)
    const glassWallGeo1 = new THREE.BoxGeometry(0.08, 5.4, 8.0);
    const officeGlassMat = new THREE.MeshPhysicalMaterial({
      color: 0xecfeff,
      transmission: 0.88,
      opacity: 0.35,
      transparent: true,
      roughness: 0.1,
      ior: 1.5,
      thickness: 0.1,
    });
    const glassWall1 = new THREE.Mesh(glassWallGeo1, officeGlassMat);
    glassWall1.position.set(11.8, 2.7, -5.5);
    roomGroup.add(glassWall1);

    // Section 2: Glass Header above Doorway (z = -1.5 to 1.5, y = 3.8 to 5.4)
    const glassDoorHeaderGeo = new THREE.BoxGeometry(0.08, 1.6, 3.0);
    const glassDoorHeader = new THREE.Mesh(glassDoorHeaderGeo, officeGlassMat);
    glassDoorHeader.position.set(11.8, 4.6, 0);
    roomGroup.add(glassDoorHeader);

    // Top sliding rail for glass door
    const doorRailGeo = new THREE.BoxGeometry(0.12, 0.12, 3.2);
    const doorRailMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8, roughness: 0.2 });
    const doorRail = new THREE.Mesh(doorRailGeo, doorRailMat);
    doorRail.position.set(11.8, 3.8, 0);
    roomGroup.add(doorRail);

    // Glass Wall Metal Mullions / Posts
    [-9.5, -5.5, -1.5, 1.5].forEach((pz) => {
      const postGeo = new THREE.BoxGeometry(0.14, 5.5, 0.14);
      const postMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8, roughness: 0.2 });
      const post = new THREE.Mesh(postGeo, postMat);
      post.position.set(11.8, 2.75, pz);
      roomGroup.add(post);
    });

    // 5B. CONFERENCE MEETING ROOM INTERIOR
    // Modern Scandinavian Walnut Conference Table
    const confTableGroup = new THREE.Group();
    confTableGroup.position.set(14.5, 0, -6.5);

    const confTableTopGeo = new THREE.BoxGeometry(2.3, 0.08, 4.6);
    const confTableMat = new THREE.MeshStandardMaterial({ color: 0x2e1810, roughness: 0.4, metalness: 0.1 });
    const confTableTop = new THREE.Mesh(confTableTopGeo, confTableMat);
    confTableTop.position.y = 0.74;
    confTableTop.castShadow = true;
    confTableTop.receiveShadow = true;
    confTableGroup.add(confTableTop);

    // Metal Sled Legs for Conference Table
    const sledLegMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.85, roughness: 0.2 });
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

    // Center aluminum cable well with soft glow
    const wellGeo = new THREE.BoxGeometry(0.35, 0.015, 1.6);
    const wellMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.5, metalness: 0.9 });
    const wellMesh = new THREE.Mesh(wellGeo, wellMat);
    wellMesh.position.set(0, 0.785, 0);
    confTableGroup.add(wellMesh);

    roomGroup.add(confTableGroup);

    // 5C. Conference Swivel Chairs (Around the Table)
    const confChairGeo = new THREE.BoxGeometry(0.52, 0.08, 0.52);
    const confBackGeo = new THREE.BoxGeometry(0.5, 0.55, 0.06);
    const chairLeatherMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 });
    const chairBaseMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.2 });

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

    [-8.0, -6.5, -5.0].forEach((cz) => {
      roomGroup.add(createConfChair(13.2, cz, Math.PI / 2));
    });
    [-8.0, -6.5, -5.0].forEach((cz) => {
      roomGroup.add(createConfChair(15.8, cz, -Math.PI / 2));
    });
    roomGroup.add(createConfChair(14.5, -4.0, 0));

    // 5D. 75" 4K Presentation Display TV Wall
    const tvGroup = new THREE.Group();
    tvGroup.position.set(14.5, 3.1, -13.7);

    const tvFrameGeo = new THREE.BoxGeometry(4.0, 2.3, 0.12);
    const tvFrameMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.9, roughness: 0.2 });
    const tvFrame = new THREE.Mesh(tvFrameGeo, tvFrameMat);
    tvGroup.add(tvFrame);

    const tvScreenTex = createMeetingScreenTexture();
    const tvScreenGeo = new THREE.PlaneGeometry(3.88, 2.18);
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

    const meetingLight = new THREE.PointLight(0xbae6fd, 1.2, 8, 2);
    meetingLight.position.set(14.5, 4.8, -6.5);
    roomGroup.add(meetingLight);

    roomGroup.add(tvGroup);

    // 6. Large Glass Whiteboard with System Architecture
    const wbTexture = createWhiteboardTexture();
    const wbFrameGeo = new THREE.BoxGeometry(6.6, 3.4, 0.12);
    const wbFrameMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.8, roughness: 0.3 });
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
    const trayMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8 });
    const tray = new THREE.Mesh(trayGeo, trayMat);
    tray.position.set(0, 1.57, -13.65);
    roomGroup.add(tray);

    // 7. Suspended Architectural Linear LED Downlights (Above Desks)
    [-2, 2].forEach((pz) => {
      const fixtureGeo = new THREE.BoxGeometry(14, 0.15, 0.25);
      const fixtureMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.4 });
      const fixture = new THREE.Mesh(fixtureGeo, fixtureMat);
      fixture.position.set(0, 5.2, pz);
      roomGroup.add(fixture);

      // Light strip
      const stripGeo = new THREE.BoxGeometry(13.8, 0.02, 0.18);
      const stripMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        emissive: 0xfffbeb,
        emissiveIntensity: 1.6,
      });
      const strip = new THREE.Mesh(stripGeo, stripMat);
      strip.position.set(0, 5.12, pz);
      roomGroup.add(strip);

      // Suspension wire
      [-6, 6].forEach((wx) => {
        const wireGeo = new THREE.CylinderGeometry(0.015, 0.015, 1.8, 8);
        const wireMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8 });
        const wire = new THREE.Mesh(wireGeo, wireMat);
        wire.position.set(wx, 6.1, pz);
        roomGroup.add(wire);
      });
    });

    // 8. Executive Breakout Lounge (Sofa Kulit Cognac L-Shape)
    const sofaGroup = new THREE.Group();
    sofaGroup.position.set(8.5, 0, 7.5);

    const leatherMat = new THREE.MeshStandardMaterial({ color: 0x9a3412, roughness: 0.55 }); // Cognac leather
    // Main couch seat
    const couchBaseGeo = new THREE.BoxGeometry(4.2, 0.45, 1.8);
    const couchBase = new THREE.Mesh(couchBaseGeo, leatherMat);
    couchBase.position.set(0, 0.225, 0);
    couchBase.castShadow = true;
    sofaGroup.add(couchBase);

    // Couch Backrest
    const couchBackGeo = new THREE.BoxGeometry(4.2, 0.65, 0.35);
    const couchBack = new THREE.Mesh(couchBackGeo, leatherMat);
    couchBack.position.set(0, 0.775, 0.72);
    couchBack.castShadow = true;
    sofaGroup.add(couchBack);

    // L-Section
    const lSectionGeo = new THREE.BoxGeometry(1.6, 0.45, 2.2);
    const lSection = new THREE.Mesh(lSectionGeo, leatherMat);
    lSection.position.set(1.3, 0.225, -1.8);
    lSection.castShadow = true;
    sofaGroup.add(lSection);

    // Modern Round Marble Coffee Table
    const marbleTableGeo = new THREE.CylinderGeometry(0.9, 0.9, 0.06, 24);
    const marbleMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.15, metalness: 0.1 });
    const marbleTable = new THREE.Mesh(marbleTableGeo, marbleMat);
    marbleTable.position.set(-0.8, 0.48, -0.6);
    marbleTable.castShadow = true;
    sofaGroup.add(marbleTable);

    // Coffee Table Brass Legs
    const brassMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.8, roughness: 0.3 });
    const tableLegGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.48, 12);
    const tableLeg = new THREE.Mesh(tableLegGeo, brassMat);
    tableLeg.position.set(-0.8, 0.24, -0.6);
    sofaGroup.add(tableLeg);

    roomGroup.add(sofaGroup);

    // 9. Modern Pantry & Barista Bar
    const barGeo = new THREE.BoxGeometry(4.6, 1.05, 1.3);
    const barMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.35 });
    const bar = new THREE.Mesh(barGeo, barMat);
    bar.position.set(-12, 0.525, -7.5);
    bar.castShadow = true;
    roomGroup.add(bar);

    const counterGeo = new THREE.BoxGeometry(4.8, 0.08, 1.45);
    const counterMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.18 });
    const counter = new THREE.Mesh(counterGeo, counterMat);
    counter.position.set(-12, 1.09, -7.5);
    counter.castShadow = true;
    roomGroup.add(counter);

    // Espresso Machine (Stainless Steel Dual Group)
    const espressoGeo = new THREE.BoxGeometry(0.85, 0.6, 0.65);
    const espressoMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.15 });
    const espresso = new THREE.Mesh(espressoGeo, espressoMat);
    espresso.position.set(-13, 1.43, -7.5);
    espresso.castShadow = true;
    roomGroup.add(espresso);

    // Stainless Mini Beverage Fridge (Kulkas Minuman Kantor)
    const fridgeGeo = new THREE.BoxGeometry(1.1, 1.2, 0.95);
    const fridgeMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.85, roughness: 0.2 });
    const fridge = new THREE.Mesh(fridgeGeo, fridgeMat);
    fridge.position.set(-14.2, 0.6, -7.5);
    fridge.castShadow = true;
    roomGroup.add(fridge);

    // Kaca pintu kulkas dengan pantulan kaleng minuman
    const fridgeDoorGeo = new THREE.PlaneGeometry(0.95, 1.05);
    const fridgeDoorMat = new THREE.MeshPhysicalMaterial({
      color: 0x93c5fd,
      transmission: 0.8,
      transparent: true,
      roughness: 0.1,
    });
    const fridgeDoor = new THREE.Mesh(fridgeDoorGeo, fridgeDoorMat);
    fridgeDoor.rotation.y = Math.PI / 2;
    fridgeDoor.position.set(-13.64, 0.6, -7.5);
    roomGroup.add(fridgeDoor);

    // Standing Water Cooler with Blue Gallon Bottle
    const coolerGroup = new THREE.Group();
    coolerGroup.position.set(-14.2, 0, -4.5);

    const coolerBodyGeo = new THREE.BoxGeometry(0.55, 1.05, 0.55);
    const coolerBodyMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 });
    const coolerBody = new THREE.Mesh(coolerBodyGeo, coolerBodyMat);
    coolerBody.position.y = 0.525;
    coolerBody.castShadow = true;
    coolerGroup.add(coolerBody);

    // Galon Biru Transparan di Atas
    const gallonGeo = new THREE.CylinderGeometry(0.22, 0.22, 0.65, 18);
    const gallonMat = new THREE.MeshPhysicalMaterial({
      color: 0x0284c7,
      transmission: 0.75,
      transparent: true,
      roughness: 0.1,
      ior: 1.33,
    });
    const gallon = new THREE.Mesh(gallonGeo, gallonMat);
    gallon.position.y = 1.38;
    gallon.castShadow = true;
    coolerGroup.add(gallon);

    // Tutup Galon Putih
    const capGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.08, 14);
    const capMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc });
    const cap = new THREE.Mesh(capGeo, capMat);
    cap.position.y = 1.08;
    coolerGroup.add(cap);

    roomGroup.add(coolerGroup);

    // Glass Water Dispenser on Counter
    const dispenserGeo = new THREE.CylinderGeometry(0.24, 0.24, 0.75, 16);
    const dispenserMat = new THREE.MeshPhysicalMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.65,
      roughness: 0.1,
    });
    const dispenser = new THREE.Mesh(dispenserGeo, dispenserMat);
    dispenser.position.set(-10.5, 1.5, -7.5);
    roomGroup.add(dispenser);

    // Bar Stools
    [-12.8, -11.2].forEach((bx) => {
      const stoolGroup = new THREE.Group();
      stoolGroup.position.set(bx, 0, -6.1);
      const stoolSeatGeo = new THREE.CylinderGeometry(0.25, 0.25, 0.06, 18);
      const stoolSeatMat = new THREE.MeshStandardMaterial({ color: 0xa16207, roughness: 0.6 });
      const stoolSeat = new THREE.Mesh(stoolSeatGeo, stoolSeatMat);
      stoolSeat.position.y = 0.78;
      stoolGroup.add(stoolSeat);

      const stoolLegGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.78, 12);
      const stoolLegMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8 });
      const stoolLeg = new THREE.Mesh(stoolLegGeo, stoolLegMat);
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
      const potMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.25 });
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
    // 🖥️ ERGONOMIC WORKSTATION SETUP
    // ==========================================
    const createWorkstation = (x, z, data) => {
      const deskGroup = new THREE.Group();
      deskGroup.position.set(x, 0, z);

      // Natural Solid Oak Tabletop
      const deskTopGeo = new THREE.BoxGeometry(2.1, 0.07, 1.25);
      const deskTopMat = new THREE.MeshStandardMaterial({
        color: 0xebd9c4,
        roughness: 0.45,
        metalness: 0.02,
      });
      const deskTop = new THREE.Mesh(deskTopGeo, deskTopMat);
      deskTop.position.y = 0.76;
      deskTop.castShadow = true;
      deskTop.receiveShadow = true;
      deskGroup.add(deskTop);

      // Matte Black Steel Desk Frame & Legs
      const legGeo = new THREE.BoxGeometry(0.07, 0.73, 0.07);
      const frameMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.85, roughness: 0.25 });
      [
        [-0.95, -0.52],
        [0.95, -0.52],
        [-0.95, 0.52],
        [0.95, 0.52],
      ].forEach(([lx, lz]) => {
        const leg = new THREE.Mesh(legGeo, frameMat);
        leg.position.set(lx, 0.365, lz);
        leg.castShadow = true;
        deskGroup.add(leg);
      });

      // Cable Grommet
      const grommetGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.08, 16);
      const grommet = new THREE.Mesh(grommetGeo, frameMat);
      grommet.position.set(0.65, 0.77, -0.38);
      deskGroup.add(grommet);

      // Aluminum Laptop Base (MacBook Pro Style)
      const lapBaseGeo = new THREE.BoxGeometry(0.48, 0.016, 0.34);
      const lapBaseMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.92, roughness: 0.2 });
      const lapBase = new THREE.Mesh(lapBaseGeo, lapBaseMat);
      lapBase.position.set(0, 0.805, -0.05);
      lapBase.castShadow = true;
      deskGroup.add(lapBase);

      // Keyboard & Trackpad
      const kbGeo = new THREE.BoxGeometry(0.42, 0.005, 0.16);
      const kbMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 });
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

      // Emissive Laptop Light (Casts on character and desk)
      const lapLight = new THREE.PointLight(data.screenColor, 1.1, 2.5);
      lapLight.position.set(0, 1.05, 0.05);
      deskGroup.add(lapLight);

      // Ceramic Coffee Mug
      const mugGeo = new THREE.CylinderGeometry(0.055, 0.048, 0.11, 16);
      const mugMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.2 });
      const mug = new THREE.Mesh(mugGeo, mugMat);
      mug.position.set(0.55, 0.85, 0.18);
      mug.castShadow = true;
      deskGroup.add(mug);

      // Dual Curved 4K Monitor Setup (Khusus Zaki Backend & Lulu Visual Designer)
      if (data.role.includes("Visual") || data.role.includes("Backend")) {
        const monStandGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.42, 12);
        const monStandMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.9 });
        const monStand = new THREE.Mesh(monStandGeo, monStandMat);
        monStand.position.set(-0.55, 0.98, -0.32);
        deskGroup.add(monStand);

        const monArmGeo = new THREE.BoxGeometry(0.65, 0.02, 0.02);
        const monArm = new THREE.Mesh(monArmGeo, monStandMat);
        monArm.position.set(-0.55, 1.15, -0.32);
        deskGroup.add(monArm);

        // Ultrawide Curved Screen
        const ultrawideGeo = new THREE.BoxGeometry(0.85, 0.42, 0.02);
        const ultrawideMat = new THREE.MeshStandardMaterial({
          color: 0x0f172a,
          emissive: data.screenColor,
          emissiveIntensity: 0.45,
          roughness: 0.1,
        });
        const ultrawide = new THREE.Mesh(ultrawideGeo, ultrawideMat);
        ultrawide.position.set(-0.55, 1.15, -0.28);
        ultrawide.rotation.y = 0.22; // Hadap ke arah wajah karakter
        ultrawide.castShadow = true;
        deskGroup.add(ultrawide);
      }

      // Small Desk Succulent Pot
      const potGeo = new THREE.CylinderGeometry(0.06, 0.045, 0.08, 14);
      const potMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.5 });
      const pot = new THREE.Mesh(potGeo, potMat);
      pot.position.set(-0.72, 0.835, -0.32);
      deskGroup.add(pot);

      const cactusGeo = new THREE.SphereGeometry(0.048, 10, 8);
      const cactusMat = new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.7 });
      const cactus = new THREE.Mesh(cactusGeo, cactusMat);
      cactus.position.set(-0.72, 0.90, -0.32);
      deskGroup.add(cactus);

      // Ergonomic Swivel Mesh Office Chair (Distance 0.58)
      const chairGroup = new THREE.Group();
      chairGroup.position.set(0, 0, 0.58);

      const seatGeo = new THREE.BoxGeometry(0.55, 0.08, 0.52);
      const seatMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
      const seat = new THREE.Mesh(seatGeo, seatMat);
      seat.position.y = 0.46;
      seat.castShadow = true;
      chairGroup.add(seat);

      // Ergonomic Curved Mesh Backrest
      const backGeo = new THREE.BoxGeometry(0.52, 0.62, 0.06);
      const backMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.7 });
      const back = new THREE.Mesh(backGeo, backMat);
      back.position.set(0, 0.78, 0.26);
      back.rotation.x = 0.08;
      back.castShadow = true;
      chairGroup.add(back);

      // Chrome 5-Star Base & Wheels
      const baseStemGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.38, 12);
      const baseStemMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.2 });
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
      sprite.scale.set(2.4, 0.52, 1);
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
        hipPivot.position.set(side * 0.135, 0.46, 0);

        // Thigh
        const thighGeo = new THREE.CapsuleGeometry(0.068, 0.24, 8, 14);
        const thigh = new THREE.Mesh(thighGeo, pantsMat);
        thigh.position.y = -0.12;
        thigh.castShadow = true;
        hipPivot.add(thigh);

        // Knee joint
        const kneePivot = new THREE.Group();
        kneePivot.position.y = -0.24;
        hipPivot.add(kneePivot);

        const kneeBall = new THREE.Mesh(new THREE.SphereGeometry(0.058, 10, 8), pantsMat);
        kneePivot.add(kneeBall);

        // Calf
        const calfGeo = new THREE.CapsuleGeometry(0.056, 0.24, 8, 14);
        const calf = new THREE.Mesh(calfGeo, pantsMat);
        calf.position.y = -0.12;
        calf.castShadow = true;
        kneePivot.add(calf);

        // Sneaker
        const shoeGeo = new THREE.SphereGeometry(0.072, 14, 10);
        shoeGeo.scale(1.0, 0.55, 1.5);
        const shoeMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.6 });
        const shoe = new THREE.Mesh(shoeGeo, shoeMat);
        shoe.position.set(0, -0.24, -0.05);
        shoe.castShadow = true;
        kneePivot.add(shoe);

        // White rubber sole
        const soleGeo = new THREE.BoxGeometry(0.13, 0.03, 0.24);
        const soleMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.4 });
        const sole = new THREE.Mesh(soleGeo, soleMat);
        sole.position.set(0, -0.275, -0.05);
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

        const handGeo = new THREE.SphereGeometry(0.045, 14, 12);
        handGeo.scale(1.2, 0.7, 1.0);
        const hand = new THREE.Mesh(handGeo, skinMat);
        hand.position.y = -0.23;
        hand.castShadow = true;
        elbowPivot.add(hand);

        return { shoulder, elbowPivot };
      };

      const leftArm = makeArm(-1);
      const rightArm = makeArm(1);
      const leftShoulder = leftArm.shoulder;
      const rightShoulder = rightArm.shoulder;
      const leftElbow = leftArm.elbowPivot;
      const rightElbow = rightArm.elbowPivot;
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

    // Instantiate all 8 Wayangs in Studio
    Object.entries(AGENTS).forEach(([id, data]) => {
      createStylizedHuman(id, data);
    });

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

    let clock = new THREE.Clock();
    let animId;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const elapsed = clock.getElapsedTime();
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

        // 1. Waypoint Walking Locomotion with smooth while consumption
        let hasWaypoints = agent.waypoints && agent.waypoints.length > 0;
        while (hasWaypoints) {
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
              hasWaypoints = false;
              break;
            }
          } else {
            agent.isWalking = true;
            const walkSpeed = 6.2;
            const step = Math.min(dist, walkSpeed * delta);
            curPos.x += (dx / dist) * step;
            curPos.z += (dz / dist) * step;

            const walkAngle = Math.atan2(dx, dz) + Math.PI;
            humanRoot.rotation.y = THREE.MathUtils.lerp(humanRoot.rotation.y, walkAngle, 0.25);

            agent.walkTime += delta * 14;
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
            break;
          }
        }

        if (!hasWaypoints) {
          // 2. Stationary State Postures
          agent.isWalking = false;
          humanRoot.rotation.y = THREE.MathUtils.lerp(humanRoot.rotation.y, agent.targetRotationY, 0.08);

          if (agent.currentMode === "WORK") {
            coffeeCup.visible = false;
            leftLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(leftLeg.hipPivot.rotation.x, -Math.PI / 2, 0.1);
            rightLeg.hipPivot.rotation.x = THREE.MathUtils.lerp(rightLeg.hipPivot.rotation.x, -Math.PI / 2, 0.1);
            leftLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(leftLeg.kneePivot.rotation.x, Math.PI / 2, 0.1);
            rightLeg.kneePivot.rotation.x = THREE.MathUtils.lerp(rightLeg.kneePivot.rotation.x, Math.PI / 2, 0.1);

            if (isWorking) {
              torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, 0.18, 0.08);
              headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, 0.32, 0.08);
              headGroup.rotation.y = Math.sin(elapsed * 1.8) * 0.03;

              const leftTyping = Math.sin(elapsed * 24) * 0.10;
              const rightTyping = Math.cos(elapsed * 24 + 1.2) * 0.10;
              leftShoulder.rotation.x = THREE.MathUtils.lerp(leftShoulder.rotation.x, -0.52 + leftTyping, 0.1);
              leftShoulder.rotation.z = THREE.MathUtils.lerp(leftShoulder.rotation.z, -0.18, 0.08);
              rightShoulder.rotation.x = THREE.MathUtils.lerp(rightShoulder.rotation.x, -0.52 + rightTyping, 0.1);
              rightShoulder.rotation.z = THREE.MathUtils.lerp(rightShoulder.rotation.z, 0.18, 0.08);

              leftElbow.rotation.x = THREE.MathUtils.lerp(leftElbow.rotation.x, -0.9 + leftTyping, 0.12);
              rightElbow.rotation.x = THREE.MathUtils.lerp(rightElbow.rotation.x, -0.9 + rightTyping, 0.12);

              deskObjects.displayMat.emissiveIntensity = 0.95 + Math.sin(elapsed * 9) * 0.18;
              deskObjects.lapLight.intensity = 1.1 + Math.sin(elapsed * 7) * 0.2;

              haloRing.material.opacity = THREE.MathUtils.lerp(haloRing.material.opacity, 0.85, 0.06);
              haloRing.rotation.z = elapsed * 1.2;
            } else {
              torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, -0.04, 0.05);
              torsoPivot.position.y = 0.52 + Math.sin(elapsed * 1.6 + id.charCodeAt(0)) * 0.012;
              headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, 0.05, 0.05);

              leftShoulder.rotation.set(-0.2, 0, -0.12);
              rightShoulder.rotation.set(-0.2, 0, 0.12);
              leftElbow.rotation.x = -0.5;
              rightElbow.rotation.x = -0.5;

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

        nameSprite.position.set(humanRoot.position.x, humanRoot.position.y + 2.08, humanRoot.position.z);
      });

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
          const mesh = agentMeshesRef.current[a.agent];
          if (mesh && a.in_progress > 0) {
            mesh.isWorking = true;
            setWorkingMap((prev) => ({ ...prev, [a.agent]: true }));
          }
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

  // Interactive Click Toggle (Test 3D movement by clicking cards)
  const toggleAgentWorkState = (agentId) => {
    const mesh = agentMeshesRef.current[agentId];
    setWorkingMap((prev) => {
      const isCurrentlyWorking = Boolean(prev[agentId]);
      const nextVal = !isCurrentlyWorking;
      const nextMap = { ...prev, [agentId]: nextVal };

      if (mesh) {
        mesh.isWorking = nextVal;
        if (nextVal && mesh.currentMode !== "WORK" && agentNavRef.current) {
          agentNavRef.current(agentId, "WORK");
          setAgentModes((m) => ({ ...m, [agentId]: "WORK" }));
        }
      }

      if (nextVal) {
        setActiveTask({
          agent: agentId,
          id: `LAKON-${Math.floor(Math.random() * 899 + 100)}`,
          task: AGENTS[agentId]?.action || "Menghadap laptop: fokus pengerjaan tugas...",
        });
        setEvents((evs) => [
          {
            agent: agentId,
            event_type: "task_dispatched",
            message: `Menghadap laptop: ${AGENTS[agentId]?.action}`,
            timestamp: new Date().toISOString(),
          },
          ...evs.slice(0, 49),
        ]);
      } else {
        setEvents((evs) => [
          {
            agent: agentId,
            event_type: "task_completed",
            message: `${AGENTS[agentId]?.name} menyelesaikan tugas dan istirahat`,
            timestamp: new Date().toISOString(),
          },
          ...evs.slice(0, 49),
        ]);
      }
      return nextMap;
    });
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
    <div style={{ display: "flex", width: "100vw", height: "100vh", backgroundColor: "#0b0f19", color: "#f8fafc", fontFamily: "'Inter', system-ui, sans-serif", overflow: "hidden" }}>
      {/* LEFT: 3D Studio Canvas */}
      <div style={{ flex: 1, position: "relative" }}>
        <div ref={mountRef} style={{ width: "100%", height: "100%" }} />

        {/* Studio Overlay Header */}
        <div style={{
          position: "absolute",
          top: 20,
          left: 24,
          display: "flex",
          alignItems: "center",
          gap: 16,
          backgroundColor: "rgba(15, 23, 42, 0.85)",
          backdropFilter: "blur(12px)",
          padding: "10px 20px",
          borderRadius: 14,
          border: "1px solid rgba(255, 255, 255, 0.08)",
          boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.4)"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: connected ? "#10b981" : "#ef4444", boxShadow: connected ? "0 0 12px #10b981" : "none" }} />
            <span style={{ fontSize: "0.82rem", fontWeight: "700", letterSpacing: "0.05em", color: "#94a3b8" }}>
              DALANG-AI STUDIO • 3D ISOMETRIK
            </span>
          </div>

          <div style={{ height: 16, width: 1, backgroundColor: "rgba(255, 255, 255, 0.15)" }} />

          <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.82rem", color: "#e2e8f0" }}>
            <span style={{ color: "#38bdf8", fontWeight: "700" }}>● Bekerja: {activeWayangCount}</span>
            <span style={{ color: "#64748b" }}>•</span>
            <span style={{ color: "#94a3b8" }}>Istirahat (Idle): {8 - activeWayangCount}</span>
          </div>

          <div style={{ height: 16, width: 1, backgroundColor: "rgba(255, 255, 255, 0.15)" }} />

          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <button
              onClick={() => handleAllMode("WORK")}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                padding: "6px 12px",
                borderRadius: 8,
                border: officeMode === "WORK" ? "1px solid #38bdf8" : "1px solid rgba(255,255,255,0.1)",
                backgroundColor: officeMode === "WORK" ? "rgba(56, 189, 248, 0.2)" : "rgba(30, 41, 59, 0.6)",
                color: officeMode === "WORK" ? "#38bdf8" : "#94a3b8",
                fontSize: "0.75rem",
                fontWeight: "700",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}
              title="Semua Wayang duduk di meja kerja menghadap laptop"
            >
              <Laptop size={14} /> Meja Kerja
            </button>

            <button
              onClick={() => handleAllMode("MEETING")}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                padding: "6px 12px",
                borderRadius: 8,
                border: officeMode === "MEETING" ? "1px solid #818cf8" : "1px solid rgba(255,255,255,0.1)",
                backgroundColor: officeMode === "MEETING" ? "rgba(99, 102, 241, 0.25)" : "rgba(30, 41, 59, 0.6)",
                color: officeMode === "MEETING" ? "#a5b4fc" : "#94a3b8",
                fontSize: "0.75rem",
                fontWeight: "700",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}
              title="Semua Wayang jalan ke Ruang Rapat kaca untuk Sprint All-Hands Sync"
            >
              <Users size={14} /> Ruang Rapat
            </button>

            <button
              onClick={() => handleAllMode("LOUNGE")}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                padding: "6px 12px",
                borderRadius: 8,
                border: officeMode === "LOUNGE" ? "1px solid #f59e0b" : "1px solid rgba(255,255,255,0.1)",
                backgroundColor: officeMode === "LOUNGE" ? "rgba(245, 158, 11, 0.2)" : "rgba(30, 41, 59, 0.6)",
                color: officeMode === "LOUNGE" ? "#fbbf24" : "#94a3b8",
                fontSize: "0.75rem",
                fontWeight: "700",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}
              title="Tim jalan santai ngopi di sofa cognac & barista bar pantry"
            >
              <Coffee size={14} /> Santai Ngopi
            </button>

            <button
              onClick={() => handleAllMode("AUTONOMOUS")}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                padding: "6px 12px",
                borderRadius: 8,
                border: officeMode === "AUTONOMOUS" ? "1px solid #10b981" : "1px solid rgba(255,255,255,0.1)",
                backgroundColor: officeMode === "AUTONOMOUS" ? "rgba(16, 185, 129, 0.2)" : "rgba(30, 41, 59, 0.6)",
                color: officeMode === "AUTONOMOUS" ? "#34d399" : "#94a3b8",
                fontSize: "0.75rem",
                fontWeight: "700",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}
              title="Mode Otonom: Karakter bergerak dinamis & mandiri di kantor"
            >
              <Sparkles size={14} /> Mode Otonom
            </button>
          </div>
        </div>

        {/* Active Task Floating Bar */}
        {activeTask && (
          <div style={{
            position: "absolute",
            bottom: 24,
            left: 24,
            right: 24,
            maxWidth: 620,
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            backdropFilter: "blur(12px)",
            padding: "14px 20px",
            borderRadius: 14,
            border: "1px solid rgba(56, 189, 248, 0.3)",
            display: "flex",
            alignItems: "center",
            gap: 14,
            boxShadow: "0 12px 30px rgba(0,0,0,0.5)"
          }}>
            <div style={{
              width: 40,
              height: 40,
              borderRadius: 10,
              backgroundColor: AGENTS[activeTask.agent]?.hex || "#38bdf8",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: "bold",
              color: "#fff",
              fontSize: "1.1rem"
            }}>
              {AGENTS[activeTask.agent]?.name[0] || "D"}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontWeight: "700", fontSize: "0.9rem", color: "#f8fafc" }}>
                  {AGENTS[activeTask.agent]?.name} • {AGENTS[activeTask.agent]?.role}
                </span>
                <span style={{ fontSize: "0.72rem", padding: "2px 8px", borderRadius: 4, backgroundColor: "rgba(56, 189, 248, 0.2)", color: "#38bdf8", fontWeight: "600" }}>
                  FOKUS NGETIK DI LAPTOP
                </span>
              </div>
              <p style={{ margin: "2px 0 0 0", fontSize: "0.82rem", color: "#94a3b8", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {activeTask.task}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* RIGHT: Roster & Autonomous Activity Panel */}
      <div style={{
        width: 380,
        backgroundColor: "#0d1322",
        borderLeft: "1px solid rgba(255, 255, 255, 0.08)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden"
      }}>
        {/* Panel Header */}
        <div style={{ padding: "20px 24px", borderBottom: "1px solid rgba(255, 255, 255, 0.08)" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <h2 style={{ margin: 0, fontSize: "1.05rem", fontWeight: "800", color: "#f8fafc", letterSpacing: "-0.01em" }}>
              🎭 Roster 8 Para Wayang
            </h2>
            <span style={{ fontSize: "0.72rem", backgroundColor: "rgba(99, 102, 241, 0.2)", color: "#818cf8", padding: "4px 8px", borderRadius: 6, fontWeight: "700" }}>
              OTONOM
            </span>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: "0.78rem", color: "#64748b" }}>
            Klik kartu Wayang untuk uji coba gerak 3D di laptop
          </p>
        </div>

        {/* Wayang Cards List */}
        <div style={{ flex: 1, overflowY: "auto", padding: "16px 20px", display: "flex", flexDirection: "column", gap: 10 }}>
          {Object.entries(AGENTS).map(([id, info]) => {
            const isWorking = Boolean(workingMap[id]);
            return (
              <div
                key={id}
                onClick={() => toggleAgentWorkState(id)}
                style={{
                  padding: "12px 14px",
                  borderRadius: 12,
                  backgroundColor: isWorking ? "rgba(30, 41, 59, 0.85)" : "rgba(15, 23, 42, 0.55)",
                  borderLeft: `4px solid ${info.hex}`,
                  border: isWorking ? `1px solid ${info.hex}` : "1px solid rgba(255,255,255,0.05)",
                  borderLeftWidth: "4px",
                  cursor: "pointer",
                  transition: "all 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
                  transform: isWorking ? "scale(1.02)" : "scale(1)",
                }}
                title="Klik untuk mensimulasikan tugas ke wayang ini"
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "0.88rem", fontWeight: "700", color: "#f8fafc" }}>{info.name}</span>
                  <span style={{
                    fontSize: "0.65rem",
                    fontWeight: "800",
                    padding: "2px 7px",
                    borderRadius: 4,
                    backgroundColor: isWorking ? "rgba(56, 189, 248, 0.2)" : "rgba(100, 116, 139, 0.18)",
                    color: isWorking ? "#38bdf8" : "#94a3b8"
                  }}>
                    {isWorking ? "💻 NGETIK" : "☕ IDLE"}
                  </span>
                </div>
                <div style={{ fontSize: "0.74rem", color: info.hex, fontWeight: "600", marginTop: 2 }}>
                  {info.role} • {info.title}
                </div>
                <div style={{ fontSize: "0.72rem", color: "#64748b", marginTop: 4, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {info.action}
                </div>

                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 8, paddingTop: 8, borderTop: "1px solid rgba(255,255,255,0.06)" }}>
                  <span style={{ fontSize: "0.68rem", color: "#94a3b8", display: "flex", alignItems: "center", gap: 4 }}>
                    {agentModes[id] === "WORK" && "📍 Di Meja"}
                    {agentModes[id] === "MEETING" && "📍 Di Rapat"}
                    {agentModes[id] === "LOUNGE" && "📍 Di Sofa"}
                    {agentModes[id] === "PANTRY" && "📍 Di Pantry"}
                  </span>

                  <div style={{ display: "flex", gap: 4 }}>
                    <button
                      onClick={(e) => handleAgentNav(id, "WORK", e)}
                      style={{
                        fontSize: "0.65rem",
                        padding: "2px 6px",
                        borderRadius: 4,
                        backgroundColor: agentModes[id] === "WORK" ? "rgba(56, 189, 248, 0.25)" : "rgba(255,255,255,0.05)",
                        color: agentModes[id] === "WORK" ? "#38bdf8" : "#94a3b8",
                        border: "none",
                        cursor: "pointer"
                      }}
                      title="Suruh ke Meja Kerja"
                    >
                      Meja
                    </button>
                    <button
                      onClick={(e) => handleAgentNav(id, "MEETING", e)}
                      style={{
                        fontSize: "0.65rem",
                        padding: "2px 6px",
                        borderRadius: 4,
                        backgroundColor: agentModes[id] === "MEETING" ? "rgba(99, 102, 241, 0.3)" : "rgba(255,255,255,0.05)",
                        color: agentModes[id] === "MEETING" ? "#a5b4fc" : "#94a3b8",
                        border: "none",
                        cursor: "pointer"
                      }}
                      title="Suruh ke Ruang Rapat"
                    >
                      Rapat
                    </button>
                    <button
                      onClick={(e) => handleAgentNav(id, "LOUNGE", e)}
                      style={{
                        fontSize: "0.65rem",
                        padding: "2px 6px",
                        borderRadius: 4,
                        backgroundColor: agentModes[id] === "LOUNGE" ? "rgba(245, 158, 11, 0.25)" : "rgba(255,255,255,0.05)",
                        color: agentModes[id] === "LOUNGE" ? "#fbbf24" : "#94a3b8",
                        border: "none",
                        cursor: "pointer"
                      }}
                      title="Suruh Santai di Sofa"
                    >
                      Sofa
                    </button>
                    <button
                      onClick={(e) => handleAgentNav(id, "PANTRY", e)}
                      style={{
                        fontSize: "0.65rem",
                        padding: "2px 6px",
                        borderRadius: 4,
                        backgroundColor: agentModes[id] === "PANTRY" ? "rgba(16, 185, 129, 0.25)" : "rgba(255,255,255,0.05)",
                        color: agentModes[id] === "PANTRY" ? "#34d399" : "#94a3b8",
                        border: "none",
                        cursor: "pointer"
                      }}
                      title="Suruh Ngopi di Pantry"
                    >
                      Pantry
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Event Stream Feed */}
        <div style={{ height: 210, borderTop: "1px solid rgba(255, 255, 255, 0.08)", padding: "16px 20px", display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <span style={{ fontSize: "0.78rem", fontWeight: "700", color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Aktivitas Studio Live
            </span>
            <span style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: connected ? "#10b981" : "#ef4444" }} />
          </div>

          <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 8 }}>
            {events.length === 0 ? (
              <div style={{ fontSize: "0.75rem", color: "#475569", textAlign: "center", margin: "auto 0" }}>
                Menunggu lakon tugas dari Sang Dalang...
              </div>
            ) : (
              events.slice(0, 15).map((ev, i) => (
                <div key={i} style={{ fontSize: "0.74rem", borderLeft: "2px solid rgba(56, 189, 248, 0.4)", paddingLeft: 8 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.68rem" }}>
                    <span style={{ color: "#38bdf8", fontWeight: "600" }}>{ev.agent?.toUpperCase() || "DALANG"}</span>
                    <span>{new Date(ev.timestamp || Date.now()).toLocaleTimeString()}</span>
                  </div>
                  <div style={{ color: "#cbd5e1", marginTop: 2 }}>{ev.message}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
