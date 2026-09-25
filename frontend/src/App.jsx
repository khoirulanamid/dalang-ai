import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { Cpu, Terminal, Sparkles, UserCheck, Coffee, Building2, Monitor, Compass } from "lucide-react";

// 8 Para Wayang Roster & Specialized Outfits
const AGENTS = {
  risko: {
    name: "Risko",
    role: "Sang Dalang",
    title: "Master Orchestrator",
    color: 0x4f46e5, // Indigo Hoodie
    hex: "#4f46e5",
    hairColor: 0x1e1b4b,
    hairStyle: "pompadour",
    pos: [0, 0, 0],
    screenColor: 0x818cf8,
    action: "Memimpin orkestrasi lakon proyek",
  },
  pingot: {
    name: "Pingot",
    role: "Wayang Data",
    title: "Data Architect",
    color: 0x059669, // Forest Green Jacket
    hex: "#10b981",
    hairColor: 0x27272a,
    hairStyle: "fade",
    pos: [-3.8, 0, -2.5],
    screenColor: 0x34d399,
    action: "Audit skema & pipeline data",
  },
  zaki: {
    name: "Zaki",
    role: "Wayang Backend",
    title: "API & System Engineer",
    color: 0xd97706, // Amber Sweater
    hex: "#f59e0b",
    hairColor: 0x451a03,
    hairStyle: "curls",
    pos: [3.8, 0, -2.5],
    screenColor: 0xfbbf24,
    action: "Mengembangkan endpoint FastAPI",
  },
  lulu: {
    name: "Lulu",
    role: "Wayang Visual",
    title: "UI/UX & 3D Designer",
    color: 0xdb2777, // Rose Pink Cardigan
    hex: "#ec4899",
    hairColor: 0x831843,
    hairStyle: "bob",
    pos: [-3.8, 0, 3],
    screenColor: 0xf472b6,
    action: "Merancang desain & 3D isometrik",
  },
  mika: {
    name: "Mika",
    role: "Wayang Pujangga",
    title: "Technical Writer",
    color: 0x0891b2, // Cyan Turtleneck
    hex: "#06b6d4",
    hairColor: 0x1e293b,
    hairStyle: "ponytail",
    pos: [3.8, 0, 3],
    screenColor: 0x38bdf8,
    action: "Menulis dokumentasi & standar",
  },
  nova: {
    name: "Nova",
    role: "Wayang Patih",
    title: "DevOps & CI/CD",
    color: 0xea580c, // Rust Orange Vest
    hex: "#f97316",
    hairColor: 0x171717,
    hairStyle: "buzz",
    pos: [0, 0, -5.5],
    screenColor: 0xfb923c,
    action: "Pipeline CI/CD & Docker build",
  },
  kai: {
    name: "Kai",
    role: "Wayang Senopati",
    title: "Security Auditor",
    color: 0xdc2626, // Crimson Bomber Jacket
    hex: "#ef4444",
    hairColor: 0x18181b,
    hairStyle: "sidepart",
    pos: [-7.2, 0, 0],
    screenColor: 0xf87171,
    action: "Audit keamanan OWASP & token",
  },
  ren: {
    name: "Ren",
    role: "Wayang Jaksa",
    title: "QA & Test Automation",
    color: 0x7c3aed, // Violet Blazer
    hex: "#8b5cf6",
    hairColor: 0x2e1065,
    hairStyle: "parted",
    pos: [7.2, 0, 0],
    screenColor: 0xa78bfa,
    action: "Menjalankan 182 test suite",
  },
};

// Procedural Parquet Wood Floor Texture (MengTo Standard PBR)
function createParquetTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 1024;
  const ctx = canvas.getContext("2d");

  // Warm Oak Base
  ctx.fillStyle = "#a27b5c";
  ctx.fillRect(0, 0, 1024, 1024);

  const plankW = 128;
  const plankH = 32;

  for (let y = 0; y < 1024; y += plankH) {
    const rowOffset = (Math.floor(y / plankH) % 2) * (plankW / 2);
    for (let x = -plankW; x < 1024 + plankW; x += plankW) {
      const px = x + rowOffset;
      // Slight plank shade variation
      const shade = 0.92 + Math.random() * 0.16;
      ctx.fillStyle = `rgb(${Math.floor(162 * shade)}, ${Math.floor(123 * shade)}, ${Math.floor(92 * shade)})`;
      ctx.fillRect(px + 1, y + 1, plankW - 2, plankH - 2);

      // Subtle grain lines
      ctx.fillStyle = "rgba(74, 53, 37, 0.15)";
      for (let g = 0; g < 4; g++) {
        const gy = y + 4 + Math.random() * (plankH - 8);
        ctx.fillRect(px + 2, gy, plankW - 4, 1);
      }
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(4, 4);
  return texture;
}

// Procedural Carpet Rug Texture
function createRugTexture(baseColorHex, patternColorHex) {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = baseColorHex;
  ctx.fillRect(0, 0, 512, 512);

  ctx.strokeStyle = patternColorHex;
  ctx.lineWidth = 4;
  // Modern Scandinavian Diamond Grid
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

  // Border
  ctx.strokeStyle = patternColorHex;
  ctx.lineWidth = 16;
  ctx.strokeRect(8, 8, 496, 496);

  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}

export default function App() {
  const mountRef = useRef(null);
  const [events, setEvents] = useState([]);
  const [agentStatus, setAgentStatus] = useState({});
  const [activeTask, setActiveTask] = useState(null);
  const [connected, setConnected] = useState(false);
  const [workingMap, setWorkingMap] = useState({});

  const activeWayangCount = Object.values(workingMap).filter(Boolean).length;
  const sceneRef = useRef(null);
  const agentMeshesRef = useRef({});

  // 1. Setup Three.js Cinematic Isometric Studio (MengTo PBR Standards)
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    // Warm, welcoming ambient background instead of pitch black void
    scene.background = new THREE.Color(0x13192b);
    scene.fog = new THREE.FogExp2(0x13192b, 0.015);
    sceneRef.current = scene;

    // Cinematic Isometric Camera Setup
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
    renderer.toneMappingExposure = 1.15;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2.15;
    controls.minDistance = 10;
    controls.maxDistance = 55;
    controls.target.set(0, 1.2, 0);

    // ==========================================
    // 💡 THREE-POINT CINEMATIC PBR LIGHTING
    // ==========================================
    // 1. Warm Golden Daylight Sun (Key Light)
    const sunLight = new THREE.DirectionalLight(0xfff5e6, 2.4);
    sunLight.position.set(20, 32, 18);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 1024;
    sunLight.shadow.mapSize.height = 1024;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 75;
    sunLight.shadow.camera.left = -22;
    sunLight.shadow.camera.right = 22;
    sunLight.shadow.camera.top = 22;
    sunLight.shadow.camera.bottom = -22;
    sunLight.shadow.bias = -0.0003;
    scene.add(sunLight);

    // 2. Soft Sky Blue Ambient Fill (Prevents harsh dark shadows)
    const ambientLight = new THREE.AmbientLight(0xdbeafe, 0.95);
    scene.add(ambientLight);

    // 3. Cool Rim / Edge Backlight (Carves out characters & edges)
    const rimLight = new THREE.DirectionalLight(0x7dd3fc, 0.8);
    rimLight.position.set(-20, 16, -18);
    scene.add(rimLight);

    // 4. Warm Interior Pendants (Cozy Office Glow)
    const interiorGlow = new THREE.PointLight(0xfef08a, 1.2, 18);
    interiorGlow.position.set(0, 6, 0);
    scene.add(interiorGlow);

    // ==========================================
    // 🏢 ARCHITECTURAL OFFICE ROOM (Cutaway Style)
    // ==========================================
    const roomGroup = new THREE.Group();

    // 1. Warm Oak Parquet Floor
    const parquetTexture = createParquetTexture();
    const floorGeo = new THREE.PlaneGeometry(30, 26);
    const floorMat = new THREE.MeshStandardMaterial({
      map: parquetTexture,
      roughness: 0.65,
      metalness: 0.05,
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    roomGroup.add(floor);

    // 2. Central Scandinavian Area Rug
    const rugTexture = createRugTexture("#2e384d", "#4b5563");
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

    // 3. Back Wall (Nordic Sage Slate with Wood Paneling)
    const backWallGeo = new THREE.BoxGeometry(30, 5.5, 0.4);
    const wallMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.85 });
    const backWall = new THREE.Mesh(backWallGeo, wallMat);
    backWall.position.set(0, 2.75, -13);
    backWall.receiveShadow = true;
    roomGroup.add(backWall);

    // Left Wall with Big Modern Industrial Windows
    const leftWallGeo = new THREE.BoxGeometry(0.4, 5.5, 26);
    const leftWall = new THREE.Mesh(leftWallGeo, wallMat);
    leftWall.position.set(-15, 2.75, 0);
    leftWall.receiveShadow = true;
    roomGroup.add(leftWall);

    // Wall Baseboard (Skirting)
    const baseboardGeo = new THREE.BoxGeometry(30, 0.25, 0.45);
    const baseboardMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5 });
    const baseboard = new THREE.Mesh(baseboardGeo, baseboardMat);
    baseboard.position.set(0, 0.125, -12.8);
    roomGroup.add(baseboard);

    // 4. Large Sunlight Window Frame on Left Wall
    const windowFrameGeo = new THREE.BoxGeometry(0.3, 3.2, 10);
    const windowFrameMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8, roughness: 0.3 });
    const windowFrame = new THREE.Mesh(windowFrameGeo, windowFrameMat);
    windowFrame.position.set(-14.8, 3.2, 0);
    roomGroup.add(windowFrame);

    // Luminous Window Glass (Sky Daylight emission)
    const glassPaneGeo = new THREE.PlaneGeometry(9.6, 2.8);
    const glassPaneMat = new THREE.MeshStandardMaterial({
      color: 0xbae6fd,
      emissive: 0x38bdf8,
      emissiveIntensity: 0.6,
      roughness: 0.1,
    });
    const glassPane = new THREE.Mesh(glassPaneGeo, glassPaneMat);
    glassPane.rotation.y = Math.PI / 2;
    glassPane.position.set(-14.7, 3.2, 0);
    roomGroup.add(glassPane);

    // 5. Motivational Neon Wall Sign ("DALANG STUDIO • OTONOM")
    const signBoardGeo = new THREE.BoxGeometry(7, 1.2, 0.08);
    const signBoardMat = new THREE.MeshStandardMaterial({ color: 0x090d16, roughness: 0.4 });
    const signBoard = new THREE.Mesh(signBoardGeo, signBoardMat);
    signBoard.position.set(0, 4.2, -12.75);
    roomGroup.add(signBoard);

    // Neon Glow Strip
    const neonGeo = new THREE.BoxGeometry(6.6, 0.06, 0.12);
    const neonMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: 0x38bdf8,
      emissiveIntensity: 1.8,
    });
    const neonStrip = new THREE.Mesh(neonGeo, neonMat);
    neonStrip.position.set(0, 4.2, -12.7);
    roomGroup.add(neonStrip);

    // 6. Wall Bookshelf & Storage Cabinet
    const shelfGeo = new THREE.BoxGeometry(5.5, 3.4, 0.7);
    const shelfMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.5 });
    const shelf = new THREE.Mesh(shelfGeo, shelfMat);
    shelf.position.set(9.5, 1.7, -12.4);
    shelf.castShadow = true;
    shelf.receiveShadow = true;
    roomGroup.add(shelf);

    // Books & Folders inside Shelf
    for (let b = 0; b < 14; b++) {
      const bookColors = [0xef4444, 0x3b82f6, 0x10b981, 0xf59e0b, 0x8b5cf6, 0xec4899];
      const bColor = bookColors[b % bookColors.length];
      const bookGeo = new THREE.BoxGeometry(0.12, 0.55 + Math.random() * 0.2, 0.45);
      const bookMat = new THREE.MeshStandardMaterial({ color: bColor, roughness: 0.6 });
      const book = new THREE.Mesh(bookGeo, bookMat);
      book.position.set(7.4 + b * 0.32, 2.4, -12.3);
      roomGroup.add(book);
    }

    // 7. Indoor Plants (Biophilic Office Greenery)
    const makePottedPlant = (px, pz, scale = 1) => {
      const plantGroup = new THREE.Group();
      plantGroup.position.set(px, 0, pz);
      plantGroup.scale.set(scale, scale, scale);

      // Ceramic Planter Pot
      const potGeo = new THREE.CylinderGeometry(0.42, 0.3, 0.75, 18);
      const potMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 });
      const pot = new THREE.Mesh(potGeo, potMat);
      pot.position.y = 0.375;
      pot.castShadow = true;
      plantGroup.add(pot);

      // Soil
      const soilGeo = new THREE.CylinderGeometry(0.4, 0.4, 0.1, 16);
      const soilMat = new THREE.MeshStandardMaterial({ color: 0x3f2e1e, roughness: 0.9 });
      const soil = new THREE.Mesh(soilGeo, soilMat);
      soil.position.y = 0.72;
      plantGroup.add(soil);

      // Lush Monstera Leaves
      const leafMat = new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.4 });
      for (let l = 0; l < 8; l++) {
        const leafGeo = new THREE.SphereGeometry(0.35, 8, 8);
        leafGeo.scale(1.2, 0.1, 0.7);
        const leaf = new THREE.Mesh(leafGeo, leafMat);
        const angle = (l / 8) * Math.PI * 2;
        leaf.position.set(Math.cos(angle) * 0.45, 0.85 + (l % 3) * 0.2, Math.sin(angle) * 0.45);
        leaf.rotation.set(0.3, angle, 0.4);
        leaf.castShadow = true;
        plantGroup.add(leaf);
      }
      return plantGroup;
    };

    roomGroup.add(makePottedPlant(-13.5, -11.5, 1.3)); // Corner plant
    roomGroup.add(makePottedPlant(13.2, 10.5, 1.2)); // Front right plant
    roomGroup.add(makePottedPlant(-13.5, 10.5, 1.1)); // Front left plant

    // 8. Pantry & Coffee Breakout Corner
    const barGeo = new THREE.BoxGeometry(4.2, 1.05, 1.2);
    const barMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.3 });
    const bar = new THREE.Mesh(barGeo, barMat);
    bar.position.set(-11.5, 0.525, -6.5);
    bar.castShadow = true;
    roomGroup.add(bar);

    // Marble Countertop
    const counterGeo = new THREE.BoxGeometry(4.4, 0.08, 1.35);
    const counterMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.15 });
    const counter = new THREE.Mesh(counterGeo, counterMat);
    counter.position.set(-11.5, 1.09, -6.5);
    counter.castShadow = true;
    roomGroup.add(counter);

    // Espresso Machine
    const espressoGeo = new THREE.BoxGeometry(0.7, 0.55, 0.55);
    const espressoMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.85, roughness: 0.2 });
    const espresso = new THREE.Mesh(espressoGeo, espressoMat);
    espresso.position.set(-12.5, 1.4, -6.5);
    espresso.castShadow = true;
    roomGroup.add(espresso);

    // Glass Water Dispenser
    const dispenserGeo = new THREE.CylinderGeometry(0.22, 0.22, 0.7, 16);
    const dispenserMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.6,
      roughness: 0.1,
    });
    const dispenser = new THREE.Mesh(dispenserGeo, dispenserMat);
    dispenser.position.set(-10.2, 1.48, -6.5);
    roomGroup.add(dispenser);

    // Bar Stools
    [-12.2, -10.8].forEach((bx) => {
      const stoolGroup = new THREE.Group();
      stoolGroup.position.set(bx, 0, -5.2);
      const stoolSeatGeo = new THREE.CylinderGeometry(0.24, 0.24, 0.06, 16);
      const stoolSeatMat = new THREE.MeshStandardMaterial({ color: 0xa16207, roughness: 0.6 });
      const stoolSeat = new THREE.Mesh(stoolSeatGeo, stoolSeatMat);
      stoolSeat.position.y = 0.78;
      stoolGroup.add(stoolSeat);

      const stoolLegGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.78, 8);
      const stoolLegMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8 });
      const stoolLeg = new THREE.Mesh(stoolLegGeo, stoolLegMat);
      stoolLeg.position.y = 0.39;
      stoolGroup.add(stoolLeg);
      roomGroup.add(stoolGroup);
    });

    scene.add(roomGroup);

    // ==========================================
    // 🪑 WORKSPACE DESKS & WORKSTATIONS
    // ==========================================
    const createWorkstation = (x, z, agentData) => {
      const deskGroup = new THREE.Group();
      deskGroup.position.set(x, 0, z);

      // 1. Premium Matte Wood Desk
      const topGeo = new THREE.BoxGeometry(2.1, 0.08, 1.25);
      const topMat = new THREE.MeshStandardMaterial({ color: 0x232d3f, roughness: 0.3, metalness: 0.05 });
      const top = new THREE.Mesh(topGeo, topMat);
      top.position.y = 0.76;
      top.castShadow = true;
      top.receiveShadow = true;
      deskGroup.add(top);

      // Chamfered Desk Edge Trim
      const trimGeo = new THREE.BoxGeometry(2.14, 0.02, 1.29);
      const trimMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5 });
      const trim = new THREE.Mesh(trimGeo, trimMat);
      trim.position.y = 0.72;
      deskGroup.add(trim);

      // Steel Matte Desk Legs
      const legGeo = new THREE.CylinderGeometry(0.035, 0.035, 0.74, 14);
      const legMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.9, roughness: 0.2 });
      [
        [-0.95, -0.52],
        [0.95, -0.52],
        [-0.95, 0.52],
        [0.95, 0.52],
      ].forEach(([lx, lz]) => {
        const leg = new THREE.Mesh(legGeo, legMat);
        leg.position.set(lx, 0.37, lz);
        leg.castShadow = true;
        deskGroup.add(leg);
      });

      // Leather Desk Mat (Blotter)
      const matGeo = new THREE.BoxGeometry(1.2, 0.008, 0.75);
      const matMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.85 });
      const blotter = new THREE.Mesh(matGeo, matMat);
      blotter.position.set(0, 0.804, 0.02);
      deskGroup.add(blotter);

      // Sleek Modern Laptop
      const laptopBaseGeo = new THREE.BoxGeometry(0.56, 0.018, 0.4);
      const laptopBaseMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.75, roughness: 0.25 });
      const lapBase = new THREE.Mesh(laptopBaseGeo, laptopBaseMat);
      lapBase.position.set(0, 0.815, 0.08);
      lapBase.castShadow = true;
      deskGroup.add(lapBase);

      // Opened Tilted Screen Lid
      const screenPivot = new THREE.Group();
      screenPivot.position.set(0, 0.824, -0.12);

      const lidGeo = new THREE.BoxGeometry(0.56, 0.38, 0.015);
      const lidMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.75, roughness: 0.25 });
      const lid = new THREE.Mesh(lidGeo, lidMat);
      lid.position.set(0, 0.19, 0);
      lid.castShadow = true;
      screenPivot.add(lid);

      // Glowing Code Display
      const displayGeo = new THREE.PlaneGeometry(0.52, 0.34);
      const displayMat = new THREE.MeshStandardMaterial({
        color: 0x020617,
        emissive: agentData.screenColor,
        emissiveIntensity: 0.15,
        roughness: 0.1,
      });
      const display = new THREE.Mesh(displayGeo, displayMat);
      display.position.set(0, 0.19, 0.009);
      screenPivot.add(display);

      screenPivot.rotation.x = THREE.MathUtils.degToRad(-14);
      deskGroup.add(screenPivot);

      // Face Spotlight from Laptop Screen
      const lapLight = new THREE.PointLight(agentData.screenColor, 0.1, 2.0);
      lapLight.position.set(0, 1.05, 0.0);
      deskGroup.add(lapLight);

      // Ceramic Coffee Mug with Wayang Accent
      const mugGeo = new THREE.CylinderGeometry(0.065, 0.055, 0.12, 14);
      const mugMat = new THREE.MeshStandardMaterial({ color: agentData.color, roughness: 0.3 });
      const mug = new THREE.Mesh(mugGeo, mugMat);
      mug.position.set(0.68, 0.86, 0.22);
      mug.castShadow = true;
      deskGroup.add(mug);

      // Desk Mini Succulent Plant
      const plantPotGeo = new THREE.CylinderGeometry(0.07, 0.05, 0.09, 12);
      const plantPotMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.5 });
      const plantPot = new THREE.Mesh(plantPotGeo, plantPotMat);
      plantPot.position.set(-0.72, 0.845, -0.32);
      plantPot.castShadow = true;
      deskGroup.add(plantPot);

      const cactusGeo = new THREE.SphereGeometry(0.06, 8, 8);
      const cactusMat = new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.7 });
      const cactus = new THREE.Mesh(cactusGeo, cactusMat);
      cactus.position.set(-0.72, 0.92, -0.32);
      deskGroup.add(cactus);

      // Ergonomic Swivel Mesh Office Chair (jarak ergonomis ke meja)
      const chairGroup = new THREE.Group();
      chairGroup.position.set(0, 0, 0.58);

      const seatGeo = new THREE.BoxGeometry(0.55, 0.08, 0.52);
      const seatMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
      const seat = new THREE.Mesh(seatGeo, seatMat);
      seat.position.y = 0.46;
      seat.castShadow = true;
      chairGroup.add(seat);

      const backrestGeo = new THREE.BoxGeometry(0.52, 0.58, 0.06);
      const backrestMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.85 });
      const backrest = new THREE.Mesh(backrestGeo, backrestMat);
      backrest.position.set(0, 0.82, 0.26);
      backrest.castShadow = true;
      chairGroup.add(backrest);

      // Chrome Chair Base
      const stemGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.44, 12);
      const stemMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.1 });
      const stem = new THREE.Mesh(stemGeo, stemMat);
      stem.position.y = 0.22;
      chairGroup.add(stem);

      const casterGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.02, 5);
      const caster = new THREE.Mesh(casterGeo, stemMat);
      caster.position.y = 0.02;
      chairGroup.add(caster);

      deskGroup.add(chairGroup);
      scene.add(deskGroup);

      return { displayMat, lapLight };
    };

    // ==========================================
    // 👤 STYLIZED HUMAN CHARACTER RIGGING (MengTo)
    // ==========================================
    // ==========================================
    // 🏷️ FLOATING NAME LABEL (Canvas Sprite)
    // ==========================================
    const createNameLabel = (name, role, color) => {
      const canvas = document.createElement("canvas");
      canvas.width = 512;
      canvas.height = 112;
      const ctx = canvas.getContext("2d");

      // Background pill
      ctx.clearRect(0, 0, 512, 112);
      const colorHex = "#" + color.toString(16).padStart(6, "0");
      ctx.fillStyle = "rgba(10, 15, 29, 0.82)";
      ctx.beginPath();
      ctx.roundRect(8, 8, 496, 96, 20);
      ctx.fill();

      // Accent left bar
      ctx.fillStyle = colorHex;
      ctx.beginPath();
      ctx.roundRect(8, 8, 8, 96, [20, 0, 0, 20]);
      ctx.fill();

      // Name text
      ctx.fillStyle = "#f8fafc";
      ctx.font = "bold 44px system-ui, -apple-system, sans-serif";
      ctx.textBaseline = "middle";
      ctx.fillText(name, 36, 42);

      // Role text
      ctx.fillStyle = colorHex;
      ctx.font = "500 30px system-ui, -apple-system, sans-serif";
      ctx.fillText(role, 36, 80);

      const texture = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthWrite: false,
      });
      const sprite = new THREE.Sprite(spriteMat);
      // Scale: width = 2.4 world units, height proportional
      sprite.scale.set(2.4, 0.52, 1);
      return sprite;
    };

    // ==========================================
    // 👤 ORGANIC STYLIZED HUMAN (No Roblox Boxes)
    // CapsuleGeometry for limbs, ellipsoid head,
    // rounded torso — zero BoxGeometry on body.
    // ==========================================
    const createStylizedHuman = (id, data) => {
      const [x, y, z] = data.pos;
      const deskObjects = createWorkstation(x, z, data);

      const humanRoot = new THREE.Group();
      humanRoot.position.set(x, 0, z + 0.58);

      // PBR Materials
      const skinMat = new THREE.MeshStandardMaterial({
        color: 0xf0c4a0, // warm peach skin
        roughness: 0.62,
        metalness: 0.0,
      });
      const clothesMat = new THREE.MeshStandardMaterial({
        color: data.color,
        roughness: 0.88,
        metalness: 0.04,
      });
      const pantsMat = new THREE.MeshStandardMaterial({
        color: 0x1e293b,
        roughness: 0.92,
      });
      const hairMat = new THREE.MeshStandardMaterial({
        color: data.hairColor,
        roughness: 0.82,
      });

      // ---- LOWER BODY (Seated — Organic Capsule Legs) ----
      // DEPAN = -Z (menuju laptop/meja), BELAKANG = +Z (menuju sandaran kursi)
      // Thighs: horizontal capsule menjulur ke depan (-Z) dari panggul ke lutut
      const thighGeo = new THREE.CapsuleGeometry(0.065, 0.28, 8, 14);
      [-0.13, 0.13].forEach((sx) => {
        const thigh = new THREE.Mesh(thighGeo, pantsMat);
        thigh.rotation.x = Math.PI / 2;
        thigh.position.set(sx, 0.455, -0.16); // -Z = menjulur ke depan arah meja
        thigh.castShadow = true;
        humanRoot.add(thigh);
      });

      // Calves: dari lutut (-0.30) turun ke lantai agak miring ke depan (-0.38)
      const calfGeo = new THREE.CapsuleGeometry(0.055, 0.3, 8, 14);
      [-0.13, 0.13].forEach((sx) => {
        const calf = new THREE.Mesh(calfGeo, pantsMat);
        calf.rotation.x = -0.22; // miring sedikit ke depan
        calf.position.set(sx, 0.2, -0.36);
        calf.castShadow = true;
        humanRoot.add(calf);
      });

      // Sneakers — di ujung kaki, di bawah kolong meja (-Z)
      [-0.13, 0.13].forEach((sx) => {
        const shoeGeo = new THREE.SphereGeometry(0.075, 14, 10);
        shoeGeo.scale(1.0, 0.55, 1.6);
        const shoe = new THREE.Mesh(shoeGeo, new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.65 }));
        shoe.position.set(sx, 0.055, -0.48); // di bawah meja
        shoe.castShadow = true;
        humanRoot.add(shoe);
      });

      // ---- UPPER BODY PIVOT ----
      const torsoPivot = new THREE.Group();
      torsoPivot.position.set(0, 0.52, 0);

      // Torso: Capsule scaled to oval shoulder shape (not box!)
      const torsoGeo = new THREE.CapsuleGeometry(0.19, 0.28, 10, 20);
      torsoGeo.scale(1.15, 1.0, 0.72);
      const torso = new THREE.Mesh(torsoGeo, clothesMat);
      torso.position.y = 0.22;
      torso.castShadow = true;
      torsoPivot.add(torso);

      // Shoulder width pads (natural shoulder slope)
      [-0.22, 0.22].forEach((sx) => {
        const shoulderPadGeo = new THREE.SphereGeometry(0.1, 12, 10);
        shoulderPadGeo.scale(1.0, 0.7, 0.8);
        const pad = new THREE.Mesh(shoulderPadGeo, clothesMat);
        pad.position.set(sx, 0.4, 0);
        pad.castShadow = true;
        torsoPivot.add(pad);
      });

      // Neck: slim capsule
      const neckGeo = new THREE.CapsuleGeometry(0.058, 0.06, 8, 12);
      const neck = new THREE.Mesh(neckGeo, skinMat);
      neck.position.y = 0.52;
      torsoPivot.add(neck);

      // ---- HEAD GROUP ----
      const headGroup = new THREE.Group();
      headGroup.position.set(0, 0.63, 0);

      // Head: non-uniform sphere (taller, slightly wider jaw)
      const headGeo = new THREE.SphereGeometry(0.155, 28, 22);
      headGeo.scale(1.0, 1.18, 0.97);
      const head = new THREE.Mesh(headGeo, skinMat);
      head.castShadow = true;
      headGroup.add(head);

      // Jaw / Chin rounding
      const chinGeo = new THREE.SphereGeometry(0.09, 14, 10);
      chinGeo.scale(0.85, 0.55, 0.75);
      const chin = new THREE.Mesh(chinGeo, skinMat);
      chin.position.set(0, -0.12, -0.04);
      headGroup.add(chin);

      // Cheeks (subtle volume)
      [-0.1, 0.1].forEach((cx) => {
        const cheekGeo = new THREE.SphereGeometry(0.065, 10, 10);
        cheekGeo.scale(1.0, 0.72, 0.7);
        const cheek = new THREE.Mesh(cheekGeo, skinMat);
        cheek.position.set(cx, -0.02, -0.12);
        headGroup.add(cheek);
      });

      // Nose (small sphere bump, not box)
      const noseGeo = new THREE.SphereGeometry(0.028, 10, 8);
      noseGeo.scale(1.0, 0.85, 1.2);
      const nose = new THREE.Mesh(noseGeo, skinMat);
      nose.position.set(0, 0.01, -0.175);
      headGroup.add(nose);

      // Eyes (dark sphere inset)
      [-0.065, 0.065].forEach((ex) => {
        const eyeGeo = new THREE.SphereGeometry(0.022, 10, 8);
        const eyeMat = new THREE.MeshStandardMaterial({ color: 0x1a1a2e, roughness: 0.2 });
        const eye = new THREE.Mesh(eyeGeo, eyeMat);
        eye.position.set(ex, 0.045, -0.155);
        headGroup.add(eye);

        // Eye white
        const scleraGeo = new THREE.SphereGeometry(0.03, 10, 8);
        const scleraMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 });
        const sclera = new THREE.Mesh(scleraGeo, scleraMat);
        sclera.position.set(ex, 0.045, -0.148);
        headGroup.add(sclera);
      });

      // Hair — full sculpted dome + side volume
      const hairDomeGeo = new THREE.SphereGeometry(0.168, 20, 18, 0, Math.PI * 2, 0, Math.PI / 1.75);
      const hairDome = new THREE.Mesh(hairDomeGeo, hairMat);
      hairDome.position.set(0, 0.038, 0);
      hairDome.castShadow = true;
      headGroup.add(hairDome);

      // Side hair volume (temples)
      [-0.13, 0.13].forEach((hx) => {
        const sideGeo = new THREE.SphereGeometry(0.09, 12, 10);
        sideGeo.scale(0.6, 0.85, 0.9);
        const side = new THREE.Mesh(sideGeo, hairMat);
        side.position.set(hx, 0.02, 0.02);
        headGroup.add(side);
      });

      // Over-Ear Headphones (curved torus band)
      const headphoneMat = new THREE.MeshStandardMaterial({
        color: 0x090d16,
        metalness: 0.82,
        roughness: 0.18,
      });
      const bandGeo = new THREE.TorusGeometry(0.185, 0.018, 12, 30, Math.PI);
      const band = new THREE.Mesh(bandGeo, headphoneMat);
      band.rotation.z = Math.PI;
      band.position.y = 0.07;
      headGroup.add(band);

      // Ear cups (round disc, not cylinder slab)
      [-0.185, 0.185].forEach((hx) => {
        const cupGeo = new THREE.SphereGeometry(0.055, 14, 12);
        cupGeo.scale(0.45, 1.0, 1.0);
        const cup = new THREE.Mesh(cupGeo, headphoneMat);
        cup.rotation.z = Math.PI / 2;
        cup.position.set(hx, 0.02, 0);
        headGroup.add(cup);

        // LED Accent ring
        const ledGeo = new THREE.TorusGeometry(0.038, 0.007, 8, 18);
        const ledMat = new THREE.MeshStandardMaterial({
          color: data.color,
          emissive: data.color,
          emissiveIntensity: 0.9,
        });
        const led = new THREE.Mesh(ledGeo, ledMat);
        led.rotation.y = Math.PI / 2;
        led.position.set(hx > 0 ? hx + 0.028 : hx - 0.028, 0.02, 0);
        headGroup.add(led);
      });

      torsoPivot.add(headGroup);

      // ---- ARMS (CapsuleGeometry — artikulasi siku 2-segment) ----
      // makeArm() returns { shoulder, elbowPivot } sehingga animasi bisa
      // mengontrol siku secara terpisah untuk pose mengetik yang natural.
      const makeArm = (side) => {
        // === BAHU (shoulder pivot) ===
        const shoulder = new THREE.Group();
        shoulder.position.set(side * 0.255, 0.38, 0);

        // Lengan atas: capsule menggantung ke bawah dari pivot bahu
        const upperArmGeo = new THREE.CapsuleGeometry(0.055, 0.18, 8, 14);
        const upperArm = new THREE.Mesh(upperArmGeo, clothesMat);
        upperArm.position.y = -0.1;
        upperArm.castShadow = true;
        shoulder.add(upperArm);

        // === SIKU (elbow pivot — child dari shoulder) ===
        const elbowPivot = new THREE.Group();
        elbowPivot.position.y = -0.23; // posisi siku relatif ke bahu
        shoulder.add(elbowPivot);

        // Bola siku
        const elbowGeo = new THREE.SphereGeometry(0.05, 12, 10);
        const elbowBall = new THREE.Mesh(elbowGeo, clothesMat);
        elbowBall.position.y = 0;
        elbowBall.castShadow = true;
        elbowPivot.add(elbowBall);

        // Lengan bawah (forearm)
        const forearmGeo = new THREE.CapsuleGeometry(0.04, 0.17, 8, 14);
        const forearm = new THREE.Mesh(forearmGeo, skinMat);
        forearm.position.y = -0.12;
        forearm.castShadow = true;
        elbowPivot.add(forearm);

        // Tangan (hand) — di ujung forearm
        const handGeo = new THREE.SphereGeometry(0.044, 14, 12);
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

      // ---- FLOATING NAME LABEL SPRITE (above head) ----
      const nameSprite = createNameLabel(data.name, data.role, data.color & 0xffffff);
      nameSprite.position.set(0, 2.55, 0);
      humanRoot.add(nameSprite);

      // ---- ACTIVE FLOOR HALO RING ----
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
        haloRing,
        nameSprite,
        deskObjects,
        isWorking: false,
        targetRotationY: Math.PI, // idle = badan menghadap kamera
        currentRotationY: Math.PI,
      };
    };

    // Instantiate all 8 Wayangs in Studio
    Object.entries(AGENTS).forEach(([id, data]) => {
      createStylizedHuman(id, data);
    });

    // 60FPS RAF Render Loop (MengTo Optimization)
    let clock = new THREE.Clock();
    let animId;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();
      controls.update();

      Object.entries(agentMeshesRef.current).forEach(([id, agent]) => {
        const {
          humanRoot,
          torsoPivot,
          headGroup,
          leftShoulder,
          rightShoulder,
          leftElbow,
          rightElbow,
          haloRing,
          deskObjects,
          isWorking,
        } = agent;

        // Smooth Swivel transition between Idle and Working
        // rotation.y = 0   saat WORKING → wajah (-Z) langsung menghadap meja/laptop
        // rotation.y = PI  saat IDLE    → badan berbalik menghadap kamera/ruangan
        agent.targetRotationY = isWorking ? 0 : Math.PI;
        agent.currentRotationY = THREE.MathUtils.lerp(agent.currentRotationY, agent.targetRotationY, 0.07);
        humanRoot.rotation.y = agent.currentRotationY;

        if (isWorking) {
          // ==========================================
          // 💻 WORKING STATE: Menghadap Laptop & Ngetik
          // ==========================================
          // Torso leans forward focused into the desk
          torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, 0.18, 0.08);

          // Head looks directly down at the screen
          headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, 0.32, 0.08);
          headGroup.rotation.y = Math.sin(elapsed * 1.8) * 0.03; // slight focus drift

          // Arms resting on desk typing — 2-segment articulation
          // Bahu turun ke depan (sedikit, agar lengan atas tidak terlalu tegak)
          const leftTyping = Math.sin(elapsed * 24) * 0.10;
          const rightTyping = Math.cos(elapsed * 24 + 1.2) * 0.10;
          leftShoulder.rotation.x = THREE.MathUtils.lerp(leftShoulder.rotation.x, -0.52 + leftTyping, 0.1);
          leftShoulder.rotation.z = THREE.MathUtils.lerp(leftShoulder.rotation.z, -0.18, 0.08);
          rightShoulder.rotation.x = THREE.MathUtils.lerp(rightShoulder.rotation.x, -0.52 + rightTyping, 0.1);
          rightShoulder.rotation.z = THREE.MathUtils.lerp(rightShoulder.rotation.z, 0.18, 0.08);

          // Siku: tekuk 90° ke arah meja (ke depan), tangan di atas keyboard
          leftElbow.rotation.x = THREE.MathUtils.lerp(leftElbow.rotation.x, -0.9 + leftTyping, 0.12);
          rightElbow.rotation.x = THREE.MathUtils.lerp(rightElbow.rotation.x, -0.9 + rightTyping, 0.12);

          // Laptop screen emits bright coding light with screen flicker
          deskObjects.displayMat.emissiveIntensity = 0.95 + Math.sin(elapsed * 9) * 0.18;
          deskObjects.lapLight.intensity = 1.1 + Math.sin(elapsed * 7) * 0.2;

          // Active floor halo rotates
          haloRing.material.opacity = THREE.MathUtils.lerp(haloRing.material.opacity, 0.85, 0.06);
          haloRing.rotation.z = elapsed * 1.2;
        } else {
          // ==========================================
          // ☕ IDLE STATE: Santai Menghadap Ruangan
          // ==========================================
          // Torso leans back comfortably
          torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, -0.06, 0.05);
          torsoPivot.position.y = 0.52 + Math.sin(elapsed * 1.6 + id.charCodeAt(0)) * 0.012; // breathing

          // Head looks around casually at the room
          headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, 0, 0.05);
          headGroup.rotation.y = Math.sin(elapsed * 0.6 + id.charCodeAt(1)) * 0.32;

          // Arms rest down naturally at sides
          leftShoulder.rotation.x = THREE.MathUtils.lerp(leftShoulder.rotation.x, 0.12, 0.08);
          leftShoulder.rotation.z = THREE.MathUtils.lerp(leftShoulder.rotation.z, -0.16, 0.08);
          rightShoulder.rotation.x = THREE.MathUtils.lerp(rightShoulder.rotation.x, 0.12, 0.08);
          rightShoulder.rotation.z = THREE.MathUtils.lerp(rightShoulder.rotation.z, 0.16, 0.08);
          leftElbow.rotation.x = THREE.MathUtils.lerp(leftElbow.rotation.x, -0.15, 0.08);
          rightElbow.rotation.x = THREE.MathUtils.lerp(rightElbow.rotation.x, -0.15, 0.08);

          // Screen in low-power idle
          deskObjects.displayMat.emissiveIntensity = 0.12;
          deskObjects.lapLight.intensity = 0.05;

          // Halo fades away
          haloRing.material.opacity = THREE.MathUtils.lerp(haloRing.material.opacity, 0, 0.08);
        }
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

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  // 2. WebSocket Realtime Events Stream
  useEffect(() => {
    let ws;
    let reconnectTimer;

    const connect = () => {
      ws = new WebSocket("ws://localhost:8765/ws/events");

      ws.onopen = () => {
        setConnected(true);
      };

      ws.onmessage = (e) => {
        try {
          const ev = JSON.parse(e.data);
          setEvents((prev) => [ev, ...prev.slice(0, 49)]);

          const agentMesh = agentMeshesRef.current[ev.agent];
          if (agentMesh) {
            if (ev.event_type === "task_dispatched") {
              agentMesh.isWorking = true;
              setWorkingMap((prev) => ({ ...prev, [ev.agent]: true }));
              setActiveTask({ agent: ev.agent, task: ev.message, id: ev.task_id });
            } else if (ev.event_type === "task_completed" || ev.event_type === "task_failed" || ev.event_type === "wayang_idle") {
              agentMesh.isWorking = false;
              setWorkingMap((prev) => ({ ...prev, [ev.agent]: false }));
            }
          }

          if (ev.event_type === "orchestration_finished") {
            setActiveTask(null);
            setWorkingMap({});
            Object.values(agentMeshesRef.current).forEach((m) => {
              m.isWorking = false;
            });
          }
        } catch (err) {
          console.error("WS Parse Error", err);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        reconnectTimer = setTimeout(connect, 3000);
      };
    };

    connect();
    return () => {
      clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

  // 3. Periodic Sync with Backend API
  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:8765/agents/status");
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
    } catch (e) {
      // Backend maybe offline
    }
  };

  useEffect(() => {
    fetchStatus();
    const iv = setInterval(fetchStatus, 3500);
    return () => clearInterval(iv);
  }, []);

  // Interactive Click Toggle (Allows user to click any Wayang card to test their real 3D movement)
  const toggleAgentWorkState = (agentId) => {
    const mesh = agentMeshesRef.current[agentId];
    setWorkingMap((prev) => {
      const isCurrentlyWorking = Boolean(prev[agentId]);
      const nextVal = !isCurrentlyWorking;
      const nextMap = { ...prev, [agentId]: nextVal };

      if (mesh) {
        mesh.isWorking = nextVal;
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
            message: `Tugas selesai. Menghadap santai menikmati kopi.`,
            timestamp: new Date().toISOString(),
          },
          ...evs.slice(0, 49),
        ]);
      }

      return nextMap;
    });
  };

  return (
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#0b0f19", color: "#f8fafc", fontFamily: "system-ui, -apple-system, sans-serif", overflow: "hidden" }}>
      {/* LEFT: Cinematic 3D Studio Canvas */}
      <div style={{ flex: 1, position: "relative", display: "flex", flexDirection: "column" }}>
        
        {/* Top Header: Clean, Architectural & Autonomous */}
        <div style={{
          padding: "14px 28px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          backgroundColor: "rgba(11, 15, 25, 0.92)",
          backdropFilter: "blur(14px)",
          zIndex: 10
        }}>
          {/* Logo & Studio Badge */}
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <span style={{ fontSize: "1.4rem" }}>🎭</span>
              <div>
                <h1 style={{ margin: 0, fontSize: "1.18rem", fontWeight: "800", letterSpacing: "0.5px" }}>
                  DALANG<span style={{ color: "#38bdf8" }}>-AI</span>
                </h1>
                <div style={{ fontSize: "0.68rem", color: "#94a3b8", display: "flex", alignItems: "center", gap: 4 }}>
                  <Building2 size={12} style={{ color: "#38bdf8" }} />
                  Studio Kantor Isometrik • Karya Bos Muda
                </div>
              </div>
            </div>

            {/* Autonomous Realtime Indicator */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "4px 12px",
              backgroundColor: "rgba(16, 185, 129, 0.12)",
              border: "1px solid rgba(16, 185, 129, 0.35)",
              borderRadius: "20px"
            }}>
              <div style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: "#10b981",
                boxShadow: "0 0 10px #10b981"
              }} />
              <span style={{ fontSize: "0.75rem", fontWeight: "700", color: "#34d399", letterSpacing: "0.5px" }}>
                OTONOM REALTIME
              </span>
            </div>
          </div>

          {/* Realtime Metrics Summary */}
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.82rem", color: "#cbd5e1" }}>
              <UserCheck size={16} style={{ color: "#38bdf8" }} />
              <span>Bekerja: <strong style={{ color: "#38bdf8", fontSize: "0.95rem" }}>{activeWayangCount}</strong></span>
            </div>

            <div style={{ width: 1, height: 18, backgroundColor: "rgba(255,255,255,0.12)" }} />

            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.82rem", color: "#94a3b8" }}>
              <Coffee size={16} style={{ color: "#a16207" }} />
              <span>Istirahat (Idle): <strong style={{ color: "#cbd5e1", fontSize: "0.95rem" }}>{8 - activeWayangCount}</strong></span>
            </div>

            <div style={{ width: 1, height: 18, backgroundColor: "rgba(255,255,255,0.12)" }} />

            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.75rem", color: connected ? "#10b981" : "#ef4444" }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: connected ? "#10b981" : "#ef4444" }} />
              <span>{connected ? "Server Terhubung" : "Menghubungkan..."}</span>
            </div>
          </div>
        </div>

        {/* 3D Canvas Mounting Area */}
        <div ref={mountRef} style={{ flex: 1, width: "100%", height: "100%", cursor: "grab" }} />

        {/* Floating Active Task Card */}
        {activeTask && (
          <div style={{
            position: "absolute",
            bottom: 26,
            left: 26,
            backgroundColor: "rgba(15, 23, 42, 0.95)",
            border: `1px solid ${AGENTS[activeTask.agent]?.hex || "#38bdf8"}`,
            padding: "16px 22px",
            borderRadius: 12,
            maxWidth: 500,
            boxShadow: "0 25px 50px -12px rgba(0,0,0,0.7)",
            backdropFilter: "blur(18px)",
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{
                  width: 10,
                  height: 10,
                  borderRadius: "50%",
                  backgroundColor: AGENTS[activeTask.agent]?.hex || "#38bdf8",
                  boxShadow: `0 0 12px ${AGENTS[activeTask.agent]?.hex || "#38bdf8"}`
                }} />
                <span style={{ fontSize: "0.8rem", fontWeight: "800", color: AGENTS[activeTask.agent]?.hex || "#38bdf8", textTransform: "uppercase", letterSpacing: "1px" }}>
                  {AGENTS[activeTask.agent]?.name} • {AGENTS[activeTask.agent]?.role}
                </span>
              </div>
              <span style={{ fontSize: "0.72rem", color: "#64748b", fontFamily: "monospace" }}>{activeTask.id}</span>
            </div>
            <div style={{ fontSize: "0.95rem", fontWeight: "600", color: "#f8fafc", lineHeight: "1.4" }}>
              {activeTask.task}
            </div>
            <div style={{ marginTop: 10, fontSize: "0.74rem", color: "#94a3b8", display: "flex", alignItems: "center", gap: 6 }}>
              <Sparkles size={13} style={{ color: "#38bdf8" }} /> Menghadap laptop & mengetik kode secara otonom
            </div>
          </div>
        )}

        {/* Camera Navigation Tip */}
        <div style={{
          position: "absolute",
          bottom: 24,
          right: 24,
          backgroundColor: "rgba(11, 15, 25, 0.8)",
          border: "1px solid rgba(255,255,255,0.08)",
          padding: "8px 14px",
          borderRadius: 8,
          fontSize: "0.72rem",
          color: "#94a3b8",
          pointerEvents: "none",
          display: "flex",
          alignItems: "center",
          gap: 6
        }}>
          <Compass size={14} style={{ color: "#38bdf8" }} /> Putar ruangan: Klik & geser mouse • Zoom: Scroll
        </div>
      </div>

      {/* RIGHT SIDEBAR: Roster 8 Wayang & Activity Feed */}
      <div style={{
        width: 460,
        borderLeft: "1px solid rgba(255,255,255,0.08)",
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#0d1322"
      }}>
        {/* Roster 8 Wayang */}
        <div style={{ padding: "20px 22px", borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ fontSize: "0.8rem", color: "#94a3b8", fontWeight: "800", letterSpacing: "1px", textTransform: "uppercase", marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
            <Cpu size={16} style={{ color: "#38bdf8" }} />
            ROSTER 8 PARA WAYANG (KLIK UNTUK TES GERAK)
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 9 }}>
            {Object.entries(AGENTS).map(([id, info]) => {
              const isWorking = Boolean(workingMap[id]);
              return (
                <div
                  key={id}
                  onClick={() => toggleAgentWorkState(id)}
                  style={{
                    backgroundColor: isWorking ? "rgba(30, 41, 59, 0.95)" : "rgba(15, 23, 42, 0.6)",
                    padding: "11px 13px",
                    borderRadius: 8,
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
                  <div style={{ fontSize: "0.73rem", color: "#94a3b8", marginTop: 2 }}>{info.role}</div>
                  <div style={{ fontSize: "0.68rem", color: isWorking ? "#38bdf8" : "#64748b", marginTop: 5, fontWeight: "500" }}>
                    {isWorking ? "Menghadap Laptop" : "Menghadap Santai"}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Live Activity Feed */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
          <div style={{
            padding: "14px 22px",
            borderBottom: "1px solid rgba(255,255,255,0.08)",
            fontSize: "0.8rem",
            color: "#94a3b8",
            fontWeight: "800",
            letterSpacing: "1px",
            textTransform: "uppercase",
            display: "flex",
            alignItems: "center",
            gap: 8
          }}>
            <Terminal size={16} style={{ color: "#38bdf8" }} />
            LOG AKTIVITAS LAKON ({events.length})
          </div>

          <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            {events.length === 0 ? (
              <div style={{ textAlign: "center", color: "#64748b", marginTop: 70, fontSize: "0.85rem", padding: "0 20px" }}>
                <Coffee size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
                Semua Wayang saat ini sedang santai di kantor isometrik.<br />
                Karakter otomatis memutar kursi dan mengetik di laptop saat ada tugas masuk!
              </div>
            ) : (
              events.map((ev, idx) => (
                <div
                  key={idx}
                  style={{
                    backgroundColor: "rgba(15, 23, 42, 0.75)",
                    padding: "11px 14px",
                    borderRadius: 8,
                    fontSize: "0.8rem",
                    borderLeft: `3px solid ${AGENTS[ev.agent]?.hex || "#64748b"}`,
                    border: "1px solid rgba(255,255,255,0.04)",
                    borderLeftWidth: "3px"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontWeight: "700", color: AGENTS[ev.agent]?.hex || "#f8fafc" }}>
                      {AGENTS[ev.agent]?.name || ev.agent?.toUpperCase()}
                    </span>
                    <span style={{ color: "#64748b", fontSize: "0.7rem" }}>
                      {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : ""}
                    </span>
                  </div>
                  <div style={{ color: "#cbd5e1", lineHeight: "1.4" }}>{ev.message}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
