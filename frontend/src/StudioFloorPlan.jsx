/**
 * StudioFloorPlan.jsx
 * Dalang-AI Bird's Eye View — Canvas 2D, zero Three.js, 60fps
 * Tiap agent punya ruangan sendiri, reaktif terhadap status task
 */

import React, { useEffect, useRef, useState, useCallback } from "react";

// ─── Konstanta Warna & Tema ─────────────────────────────────────────────────
const THEME = {
  bg: "#0a0c12",
  floor: "#0e1118",
  wall: "#1a1d2e",
  wallStroke: "#2a2d42",
  corridor: "#0c0e18",
  corridorStroke: "#1e2130",
  doorOpen: "#334155",
  grid: "rgba(99,102,241,0.06)",
  labelText: "#94a3b8",
  labelActive: "#f8fafc",
  roomNameText: "#cbd5e1",
  highlight: "rgba(99,102,241,0.15)",
  highlightActive: "rgba(99,102,241,0.3)",
};

// ─── Data Wayang & Ruangan ──────────────────────────────────────────────────
const ROOMS = [
  {
    id: "command",
    name: "Command Room",
    label: "🎭 Command",
    agent: "risko",
    agentName: "Risko",
    agentRole: "Sang Dalang",
    color: "#4f46e5",
    accentLight: "rgba(79,70,229,0.18)",
    x: 0.34, y: 0.28, w: 0.28, h: 0.38,
    furniture: [
      { type: "roundTable", rx: 0.5, ry: 0.45, r: 0.18 },
      { type: "chair", rx: 0.5, ry: 0.2, rot: 0 },
      { type: "chair", rx: 0.78, ry: 0.45, rot: Math.PI * 0.5 },
      { type: "chair", rx: 0.5, ry: 0.7, rot: Math.PI },
      { type: "chair", rx: 0.22, ry: 0.45, rot: Math.PI * 1.5 },
      { type: "whiteboard", rx: 0.5, ry: 0.88, w: 0.55, h: 0.07 },
    ],
    doors: [{ side: "bottom", pos: 0.5 }, { side: "right", pos: 0.55 }],
  },
  {
    id: "backend",
    name: "Backend Workshop",
    label: "⚙️ Backend",
    agent: "zaki",
    agentName: "Zaki",
    agentRole: "API & System Engineer",
    color: "#f59e0b",
    accentLight: "rgba(245,158,11,0.15)",
    x: 0.04, y: 0.07, w: 0.27, h: 0.38,
    furniture: [
      { type: "desk", rx: 0.2, ry: 0.25, w: 0.55, h: 0.14 },
      { type: "desk", rx: 0.2, ry: 0.55, w: 0.55, h: 0.14 },
      { type: "monitor", rx: 0.18, ry: 0.22 },
      { type: "monitor", rx: 0.32, ry: 0.22 },
      { type: "monitor", rx: 0.18, ry: 0.52 },
      { type: "rack", rx: 0.82, ry: 0.45, w: 0.1, h: 0.45 },
    ],
    doors: [{ side: "right", pos: 0.5 }],
  },
  {
    id: "frontend",
    name: "Frontend Lab",
    label: "🎨 Frontend",
    agent: "lulu",
    agentName: "Lulu",
    agentRole: "UI/UX & 3D Designer",
    color: "#ec4899",
    accentLight: "rgba(236,72,153,0.15)",
    x: 0.68, y: 0.07, w: 0.27, h: 0.38,
    furniture: [
      { type: "desk", rx: 0.5, ry: 0.25, w: 0.65, h: 0.14 },
      { type: "monitor", rx: 0.35, ry: 0.22 },
      { type: "monitor", rx: 0.52, ry: 0.22 },
      { type: "monitor", rx: 0.68, ry: 0.22 },
      { type: "draftBoard", rx: 0.5, ry: 0.72, w: 0.5, h: 0.2 },
    ],
    doors: [{ side: "left", pos: 0.5 }],
  },
  {
    id: "data",
    name: "Data Vault",
    label: "🗄 Data",
    agent: "pingot",
    agentName: "Pingot",
    agentRole: "Data Architect",
    color: "#10b981",
    accentLight: "rgba(16,185,129,0.15)",
    x: 0.04, y: 0.56, w: 0.27, h: 0.36,
    furniture: [
      { type: "desk", rx: 0.5, ry: 0.25, w: 0.65, h: 0.14 },
      { type: "monitor", rx: 0.38, ry: 0.22 },
      { type: "monitor", rx: 0.56, ry: 0.22 },
      { type: "rack", rx: 0.82, ry: 0.6, w: 0.1, h: 0.55 },
      { type: "rack", rx: 0.68, ry: 0.6, w: 0.1, h: 0.55 },
    ],
    doors: [{ side: "right", pos: 0.45 }],
  },
  {
    id: "devops",
    name: "DevOps Bay",
    label: "🚀 DevOps",
    agent: "nova",
    agentName: "Nova",
    agentRole: "DevOps & CI/CD",
    color: "#f97316",
    accentLight: "rgba(249,115,22,0.15)",
    x: 0.68, y: 0.56, w: 0.27, h: 0.36,
    furniture: [
      { type: "desk", rx: 0.5, ry: 0.25, w: 0.65, h: 0.14 },
      { type: "monitor", rx: 0.38, ry: 0.22 },
      { type: "monitor", rx: 0.56, ry: 0.22 },
      { type: "rack", rx: 0.18, ry: 0.6, w: 0.1, h: 0.55 },
      { type: "rack", rx: 0.32, ry: 0.6, w: 0.1, h: 0.55 },
    ],
    doors: [{ side: "left", pos: 0.45 }],
  },
  {
    id: "security",
    name: "Security Bunker",
    label: "🔒 Security",
    agent: "kai",
    agentName: "Kai",
    agentRole: "Security Auditor",
    color: "#ef4444",
    accentLight: "rgba(239,68,68,0.15)",
    x: 0.34, y: 0.07, w: 0.12, h: 0.18,
    furniture: [
      { type: "desk", rx: 0.5, ry: 0.42, w: 0.55, h: 0.2 },
      { type: "monitor", rx: 0.38, ry: 0.38 },
      { type: "monitor", rx: 0.62, ry: 0.38 },
    ],
    doors: [{ side: "bottom", pos: 0.5 }],
  },
  {
    id: "qa",
    name: "QA Lab",
    label: "🧪 QA",
    agent: "ren",
    agentName: "Ren",
    agentRole: "QA & Test Automation",
    color: "#8b5cf6",
    accentLight: "rgba(139,92,246,0.15)",
    x: 0.54, y: 0.07, w: 0.12, h: 0.18,
    furniture: [
      { type: "desk", rx: 0.5, ry: 0.42, w: 0.55, h: 0.2 },
      { type: "monitor", rx: 0.38, ry: 0.38 },
      { type: "monitor", rx: 0.62, ry: 0.38 },
    ],
    doors: [{ side: "bottom", pos: 0.5 }],
  },
  {
    id: "docs",
    name: "Docs Studio",
    label: "📝 Docs",
    agent: "mika",
    agentName: "Mika",
    agentRole: "Technical Writer",
    color: "#06b6d4",
    accentLight: "rgba(6,182,212,0.15)",
    x: 0.34, y: 0.72, w: 0.15, h: 0.2,
    furniture: [
      { type: "desk", rx: 0.5, ry: 0.35, w: 0.65, h: 0.18 },
      { type: "monitor", rx: 0.38, ry: 0.3 },
      { type: "bookshelf", rx: 0.82, ry: 0.65, w: 0.12, h: 0.5 },
    ],
    doors: [{ side: "top", pos: 0.5 }],
  },
  {
    id: "pantry",
    name: "Pantry",
    label: "☕ Pantry",
    agent: null,
    agentName: null,
    agentRole: null,
    color: "#64748b",
    accentLight: "rgba(100,116,139,0.1)",
    x: 0.51, y: 0.72, w: 0.15, h: 0.2,
    furniture: [
      { type: "counter", rx: 0.5, ry: 0.2, w: 0.7, h: 0.16 },
      { type: "sofa", rx: 0.5, ry: 0.72, w: 0.65, h: 0.18 },
      { type: "coffeeTable", rx: 0.5, ry: 0.52, r: 0.1 },
    ],
    doors: [{ side: "top", pos: 0.5 }],
  },
  {
    id: "screening",
    name: "Screening Studio",
    label: "🎬 Screening",
    agent: "kresna",
    agentName: "Kresna",
    agentRole: "Narrative & Motion Designer",
    color: "#a855f7",
    accentLight: "rgba(168,85,247,0.18)",
    x: 0.68, y: 0.72, w: 0.27, h: 0.2,
    furniture: [
      { type: "whiteboard", rx: 0.5, ry: 0.12, w: 0.65, h: 0.09 },
      { type: "desk", rx: 0.5, ry: 0.38, w: 0.6, h: 0.16 },
      { type: "monitor", rx: 0.32, ry: 0.33 },
      { type: "monitor", rx: 0.5, ry: 0.33 },
      { type: "monitor", rx: 0.68, ry: 0.33 },
      { type: "sofa", rx: 0.5, ry: 0.8, w: 0.6, h: 0.16 },
    ],
    doors: [{ side: "top", pos: 0.5 }],
  },
  {
    id: "vault",
    name: "Gudang Vault",
    label: "📦 Gudang Vault",
    agent: "bagong",
    agentName: "Bagong",
    agentRole: "Asset & Release Custodian",
    color: "#d97706",
    accentLight: "rgba(217,119,6,0.18)",
    x: 0.04, y: 0.72, w: 0.27, h: 0.2,
    furniture: [
      { type: "rack", rx: 0.18, ry: 0.45, w: 0.1, h: 0.65 },
      { type: "rack", rx: 0.32, ry: 0.45, w: 0.1, h: 0.65 },
      { type: "rack", rx: 0.46, ry: 0.45, w: 0.1, h: 0.65 },
      { type: "desk", rx: 0.75, ry: 0.45, w: 0.4, h: 0.2 },
      { type: "monitor", rx: 0.75, ry: 0.38 },
    ],
    doors: [{ side: "top", pos: 0.5 }],
  },
];

// ─── Agent State (simulasi / live dari WebSocket) ───────────────────────────
const AGENT_STATES = {
  idle: { label: "Idle", color: "#64748b", pulse: false },
  working: { label: "Working", color: "#f59e0b", pulse: true },
  done: { label: "Done", color: "#10b981", pulse: false },
  error: { label: "Error", color: "#ef4444", pulse: true },
  waiting: { label: "Waiting", color: "#6366f1", pulse: false },
};

// ─── Helper: gambar rounded rect ────────────────────────────────────────────
function roundRect(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.arcTo(x + w, y, x + w, y + r, r);
  ctx.lineTo(x + w, y + h - r);
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h);
  ctx.arcTo(x, y + h, x, y + h - r, r);
  ctx.lineTo(x, y + r);
  ctx.arcTo(x, y, x + r, y, r);
  ctx.closePath();
}

// ─── Gambar furniture per tipe ───────────────────────────────────────────────
function drawFurniture(ctx, type, ax, ay, aw, ah, params, color, tick) {
  const { rx, ry, r, w: fw, h: fh, rot } = params;
  const px = ax + rx * aw;
  const py = ay + ry * ah;

  ctx.save();
  switch (type) {
    case "desk": {
      const dw = (fw || 0.5) * aw;
      const dh = (fh || 0.12) * ah;
      ctx.fillStyle = "#1e2235";
      ctx.strokeStyle = "#2d3252";
      ctx.lineWidth = 1;
      roundRect(ctx, px - dw / 2, py - dh / 2, dw, dh, 4);
      ctx.fill();
      ctx.stroke();
      break;
    }
    case "monitor": {
      const mw = aw * 0.09;
      const mh = ah * 0.07;
      // layar
      ctx.fillStyle = "#0f172a";
      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 1;
      roundRect(ctx, px - mw / 2, py - mh / 2, mw, mh, 2);
      ctx.fill();
      ctx.stroke();
      // screen glow — berkedip saat tick
      const blink = 0.5 + 0.5 * Math.sin(tick * 0.04 + px);
      ctx.fillStyle = color + "55";
      roundRect(ctx, px - mw / 2 + 1, py - mh / 2 + 1, mw - 2, mh - 2, 2);
      ctx.globalAlpha = 0.3 + 0.3 * blink;
      ctx.fill();
      ctx.globalAlpha = 1;
      break;
    }
    case "rack": {
      const rw = (fw || 0.08) * aw;
      const rh = (fh || 0.4) * ah;
      ctx.fillStyle = "#111827";
      ctx.strokeStyle = "#1e293b";
      ctx.lineWidth = 1;
      roundRect(ctx, px - rw / 2, py - rh / 2, rw, rh, 2);
      ctx.fill();
      ctx.stroke();
      // LED dots
      for (let i = 0; i < 6; i++) {
        const ledOn = Math.sin(tick * 0.07 + i * 1.3 + px) > 0;
        ctx.fillStyle = ledOn ? "#22c55e" : "#14532d";
        ctx.beginPath();
        ctx.arc(px, py - rh / 2 + 6 + i * (rh / 7), 1.5, 0, Math.PI * 2);
        ctx.fill();
      }
      break;
    }
    case "roundTable": {
      const tr = (r || 0.12) * Math.min(aw, ah);
      ctx.fillStyle = "#1e2235";
      ctx.strokeStyle = "#2d3252";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(px, py, tr, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      break;
    }
    case "chair": {
      const cr = aw * 0.03;
      ctx.fillStyle = "#252a3d";
      ctx.strokeStyle = "#3b4268";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(px, py, cr, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      break;
    }
    case "whiteboard": {
      const ww = (fw || 0.5) * aw;
      const wh = (fh || 0.07) * ah;
      ctx.fillStyle = "#f8fafc";
      ctx.strokeStyle = "#cbd5e1";
      ctx.lineWidth = 1;
      roundRect(ctx, px - ww / 2, py - wh / 2, ww, wh, 2);
      ctx.fill();
      ctx.stroke();
      // marker lines
      ctx.strokeStyle = "#94a3b8";
      ctx.lineWidth = 0.5;
      for (let i = 0; i < 3; i++) {
        ctx.beginPath();
        ctx.moveTo(px - ww / 2 + 6 + i * ww * 0.3, py);
        ctx.lineTo(px - ww / 2 + 6 + i * ww * 0.3 + ww * 0.2, py);
        ctx.stroke();
      }
      break;
    }
    case "draftBoard": {
      const dw = (fw || 0.4) * aw;
      const dh = (fh || 0.18) * ah;
      ctx.fillStyle = "#0f172a";
      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 1;
      roundRect(ctx, px - dw / 2, py - dh / 2, dw, dh, 3);
      ctx.fill();
      ctx.stroke();
      // wireframe mock
      ctx.strokeStyle = color + "88";
      ctx.lineWidth = 0.8;
      ctx.strokeRect(px - dw / 2 + 4, py - dh / 2 + 3, dw * 0.4, dh * 0.5);
      ctx.beginPath();
      ctx.arc(px + dw * 0.2, py, dh * 0.25, 0, Math.PI * 2);
      ctx.stroke();
      break;
    }
    case "bookshelf": {
      const bw = (fw || 0.1) * aw;
      const bh = (fh || 0.4) * ah;
      ctx.fillStyle = "#1a1d2e";
      ctx.strokeStyle = "#2a2d42";
      ctx.lineWidth = 1;
      roundRect(ctx, px - bw / 2, py - bh / 2, bw, bh, 2);
      ctx.fill();
      ctx.stroke();
      // shelf lines
      for (let i = 1; i < 4; i++) {
        ctx.strokeStyle = "#334155";
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(px - bw / 2, py - bh / 2 + i * (bh / 4));
        ctx.lineTo(px + bw / 2, py - bh / 2 + i * (bh / 4));
        ctx.stroke();
      }
      break;
    }
    case "counter": {
      const cw = (fw || 0.6) * aw;
      const ch = (fh || 0.14) * ah;
      ctx.fillStyle = "#1e2235";
      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 1;
      roundRect(ctx, px - cw / 2, py - ch / 2, cw, ch, 3);
      ctx.fill();
      ctx.stroke();
      // coffee machine icon
      ctx.fillStyle = "#334155";
      roundRect(ctx, px - cw * 0.08, py - ch * 0.35, cw * 0.14, ch * 0.7, 2);
      ctx.fill();
      break;
    }
    case "sofa": {
      const sw = (fw || 0.5) * aw;
      const sh = (fh || 0.16) * ah;
      ctx.fillStyle = "#1e293b";
      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 1;
      roundRect(ctx, px - sw / 2, py - sh / 2, sw, sh, 5);
      ctx.fill();
      ctx.stroke();
      break;
    }
    case "coffeeTable": {
      const tr2 = (r || 0.08) * Math.min(aw, ah);
      ctx.fillStyle = "#1e2235";
      ctx.strokeStyle = "#2d3252";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(px, py, tr2, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      break;
    }
    default:
      break;
  }
  ctx.restore();
}

// ─── Gambar 1 ruangan ────────────────────────────────────────────────────────
function drawRoom(ctx, room, cw, ch, agentStatus, tick, hovered, zoomed) {
  const ax = room.x * cw;
  const ay = room.y * ch;
  const aw = room.w * cw;
  const ah = room.h * ch;

  const isActive = agentStatus === "working" || agentStatus === "error";
  const isHovered = hovered === room.id;

  // ── Background ruangan
  ctx.save();
  roundRect(ctx, ax, ay, aw, ah, 8);
  ctx.fillStyle = THEME.floor;
  ctx.fill();

  // Accent glow kalau active
  if (isActive || isHovered) {
    const grd = ctx.createRadialGradient(
      ax + aw / 2, ay + ah / 2, 0,
      ax + aw / 2, ay + ah / 2, Math.max(aw, ah) * 0.7
    );
    grd.addColorStop(0, room.accentLight);
    grd.addColorStop(1, "transparent");
    ctx.fillStyle = grd;
    roundRect(ctx, ax, ay, aw, ah, 8);
    ctx.fill();
  }

  // ── Grid lantai
  ctx.strokeStyle = THEME.grid;
  ctx.lineWidth = 0.5;
  const gridSize = 18;
  for (let gx = ax; gx < ax + aw; gx += gridSize) {
    ctx.beginPath(); ctx.moveTo(gx, ay); ctx.lineTo(gx, ay + ah); ctx.stroke();
  }
  for (let gy = ay; gy < ay + ah; gy += gridSize) {
    ctx.beginPath(); ctx.moveTo(ax, gy); ctx.lineTo(ax + aw, gy); ctx.stroke();
  }

  // ── Border ruangan
  roundRect(ctx, ax, ay, aw, ah, 8);
  ctx.strokeStyle = isHovered ? room.color + "cc" : (isActive ? room.color + "66" : THEME.wallStroke);
  ctx.lineWidth = isHovered ? 2 : 1.5;
  ctx.stroke();

  // ── Furniture
  for (const f of room.furniture) {
    drawFurniture(ctx, f.type, ax, ay, aw, ah, f, room.color, tick);
  }

  // ── Pintu (gap di border)
  for (const door of room.doors) {
    const doorW = 18;
    ctx.clearRect(
      door.side === "left" ? ax - 1 :
        door.side === "right" ? ax + aw - 1 :
          ax + door.pos * aw - doorW / 2,
      door.side === "top" ? ay - 1 :
        door.side === "bottom" ? ay + ah - 1 :
          ay + door.pos * ah - doorW / 2,
      door.side === "left" || door.side === "right" ? 3 : doorW,
      door.side === "top" || door.side === "bottom" ? 3 : doorW
    );
    // Gambar ulang gap dengan warna koridor
    ctx.fillStyle = THEME.corridor;
    if (door.side === "left" || door.side === "right") {
      ctx.fillRect(
        door.side === "left" ? ax - 1 : ax + aw - 1,
        ay + door.pos * ah - doorW / 2, 2, doorW
      );
    } else {
      ctx.fillRect(
        ax + door.pos * aw - doorW / 2,
        door.side === "top" ? ay - 1 : ay + ah - 1,
        doorW, 2
      );
    }
  }

  // ── Label ruangan (kiri atas)
  ctx.fillStyle = isHovered ? room.color : THEME.roomNameText;
  ctx.font = `bold ${Math.max(9, aw * 0.1)}px 'Inter', sans-serif`;
  ctx.textAlign = "left";
  ctx.fillText(room.label, ax + 8, ay + 14);

  // ── Nama agent kecil
  if (room.agentName) {
    ctx.fillStyle = room.color + "bb";
    ctx.font = `${Math.max(7, aw * 0.075)}px 'Inter', sans-serif`;
    ctx.fillText(room.agentName, ax + 8, ay + 24);
  }

  // ── Status indicator (pojok kanan atas)
  if (room.agent) {
    const stateInfo = AGENT_STATES[agentStatus] || AGENT_STATES.idle;
    const pulse = stateInfo.pulse
      ? 0.65 + 0.35 * Math.sin(tick * 0.12)
      : 1;
    ctx.globalAlpha = pulse;
    ctx.fillStyle = stateInfo.color;
    ctx.beginPath();
    ctx.arc(ax + aw - 10, ay + 10, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;

    // Halo ring saat error/working
    if (stateInfo.pulse) {
      ctx.strokeStyle = stateInfo.color + "55";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(ax + aw - 10, ay + 10, 6 + 2 * Math.sin(tick * 0.1), 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  // ── Avatar agent (mini dot + initial) di tengah bawah
  if (room.agentName) {
    const avatarX = ax + aw / 2;
    const avatarY = ay + ah - 20;
    const avatarR = 9;

    // idle breathing
    const breathScale = 1 + 0.04 * Math.sin(tick * 0.05 + ax);
    ctx.save();
    ctx.translate(avatarX, avatarY);
    ctx.scale(breathScale, breathScale);

    ctx.fillStyle = room.color;
    ctx.beginPath();
    ctx.arc(0, 0, avatarR, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#fff";
    ctx.font = `bold ${avatarR}px 'Inter', sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(room.agentName[0], 0, 0.5);
    ctx.restore();
    ctx.textBaseline = "alphabetic";
  }

  ctx.restore();
}

// ─── Gambar koridor penghubung ────────────────────────────────────────────────
function drawCorridor(ctx, cw, ch) {
  // Area tengah = koridor
  const midX = 0.34 * cw;
  const midW = 0.32 * cw;
  const top = 0.07 * ch;
  const bot = (0.56 + 0.36) * ch;

  ctx.fillStyle = THEME.corridor;
  ctx.strokeStyle = THEME.corridorStroke;
  ctx.lineWidth = 1;

  // Koridor vertikal tengah
  roundRect(ctx, midX, top, midW, bot - top, 0);
  ctx.fill();

  // Koridor horizontal tengah
  const midY = 0.46 * ch;
  const midH = 0.08 * ch;
  roundRect(ctx, 0.04 * cw, midY, 0.92 * cw, midH, 0);
  ctx.fill();
}

// ─── Komponen Utama ──────────────────────────────────────────────────────────
export default function StudioFloorPlan({ agentStatuses = {}, onRoomClick }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const tickRef = useRef(0);
  const [hovered, setHovered] = useState(null);
  const [selected, setSelected] = useState(null);
  const [tooltip, setTooltip] = useState(null);

  // Merge default states
  const getStatus = (agentId) =>
    agentId ? (agentStatuses[agentId] || "idle") : "idle";

  // Hit test
  const hitRoom = useCallback((mx, my, cw, ch) => {
    for (const room of ROOMS) {
      const ax = room.x * cw;
      const ay = room.y * ch;
      const aw = room.w * cw;
      const ah = room.h * ch;
      if (mx >= ax && mx <= ax + aw && my >= ay && my <= ay + ah) return room;
    }
    return null;
  }, []);

  // Mouse events
  const handleMouseMove = useCallback(
    (e) => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
      const my = (e.clientY - rect.top) * (canvas.height / rect.height);
      const room = hitRoom(mx, my, canvas.width, canvas.height);
      setHovered(room ? room.id : null);
      if (room) {
        setTooltip({
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
          room,
        });
      } else {
        setTooltip(null);
      }
    },
    [hitRoom]
  );

  const handleClick = useCallback(
    (e) => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
      const my = (e.clientY - rect.top) * (canvas.height / rect.height);
      const room = hitRoom(mx, my, canvas.width, canvas.height);
      if (room) {
        setSelected(room.id === selected ? null : room.id);
        onRoomClick && onRoomClick(room);
      }
    },
    [hitRoom, selected, onRoomClick]
  );

  const handleMouseLeave = () => {
    setHovered(null);
    setTooltip(null);
  };

  // Resize
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const resize = () => {
      const parent = canvas.parentElement;
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement);
    return () => ro.disconnect();
  }, []);

  // Render loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const loop = () => {
      tickRef.current += 1;
      const tick = tickRef.current;
      const ctx = canvas.getContext("2d");
      const cw = canvas.width;
      const ch = canvas.height;
      if (!cw || !ch) { animRef.current = requestAnimationFrame(loop); return; }

      // Clear
      ctx.clearRect(0, 0, cw, ch);
      ctx.fillStyle = THEME.bg;
      ctx.fillRect(0, 0, cw, ch);

      // Koridor
      drawCorridor(ctx, cw, ch);

      // Ruangan
      for (const room of ROOMS) {
        drawRoom(
          ctx, room, cw, ch,
          getStatus(room.agent),
          tick,
          hovered,
          selected === room.id
        );
      }

      // Label "DALANG-AI STUDIO" di tengah atas koridor
      ctx.fillStyle = "rgba(99,102,241,0.6)";
      ctx.font = "bold 11px 'Inter', monospace";
      ctx.textAlign = "center";
      ctx.fillText("◆ DALANG-AI STUDIO", cw / 2, 18);

      animRef.current = requestAnimationFrame(loop);
    };

    animRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(animRef.current);
  }, [hovered, selected, agentStatuses]);

  // ── Tooltip content
  const tooltipRoom = tooltip?.room;
  const tooltipStatus = tooltipRoom
    ? AGENT_STATES[getStatus(tooltipRoom.agent)] || AGENT_STATES.idle
    : null;

  return (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <canvas
        ref={canvasRef}
        style={{ display: "block", width: "100%", height: "100%", cursor: hovered ? "pointer" : "default" }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
      />

      {/* Tooltip */}
      {tooltip && tooltipRoom && (
        <div
          style={{
            position: "absolute",
            left: tooltip.x + 14,
            top: tooltip.y - 10,
            background: "#0f111a",
            border: `1px solid ${tooltipRoom.color}55`,
            borderRadius: 8,
            padding: "8px 12px",
            pointerEvents: "none",
            zIndex: 10,
            minWidth: 160,
          }}
        >
          <div style={{ color: tooltipRoom.color, fontWeight: 700, fontSize: 12 }}>
            {tooltipRoom.label}
          </div>
          {tooltipRoom.agentName && (
            <div style={{ color: "#94a3b8", fontSize: 11, marginTop: 2 }}>
              {tooltipRoom.agentName} · {tooltipRoom.agentRole}
            </div>
          )}
          {tooltipStatus && (
            <div style={{ display: "flex", alignItems: "center", gap: 5, marginTop: 5 }}>
              <span style={{
                width: 7, height: 7, borderRadius: "50%",
                background: tooltipStatus.color, display: "inline-block"
              }} />
              <span style={{ color: tooltipStatus.color, fontSize: 11, fontWeight: 600 }}>
                {tooltipStatus.label}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Legend status */}
      <div style={{
        position: "absolute", bottom: 10, right: 12,
        display: "flex", gap: 10, alignItems: "center",
      }}>
        {Object.entries(AGENT_STATES).map(([k, v]) => (
          <div key={k} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: v.color, display: "inline-block" }} />
            <span style={{ color: "#64748b", fontSize: 9, fontFamily: "monospace" }}>{v.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
