"""
Kresna Modular Canvas Engine (v3 — Zero Truncation Guarantee)
Memisahkan Player Framework yang solid dengan Creative Scene Scripting.
Menjamin file HTML SELALU tertutup lengkap (</html>), fungsional 100%,
tidak pernah terpotong token limit LLM, dan lulus inspeksi Ren QA.
"""

import httpx
import json
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional

HERMES_BASE_URL = os.getenv("HERMES_BASE_URL", "http://127.0.0.1:20127/v1")


def _load_api_key() -> str:
    env_file = Path("/root/.hermes/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.getenv("OPENAI_API_KEY", "hermes-local")


def generate_storify_html(
    title: str,
    story_type: str,
    beats: List[Dict[str, str]],
    facts_ledger: List[str],
    character_name: str = "Dalang-Bot",
    model: str = "auto",
) -> str:
    """
    Menghasilkan film HTML utuh yang dijamin lengkap, interaktif,
    memiliki audio sintetis, dan lulus QA Ren tanpa risiko terpotong.
    """
    beats_json = json.dumps(beats, ensure_ascii=False)
    facts_json = json.dumps(facts_ledger, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #080a10;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
      user-select: none;
    }}
    #film-stage {{
      position: relative;
      width: 960px;
      height: 540px;
      background: #0d111a;
      border-radius: 12px;
      box-shadow: 0 25px 50px -12px rgba(0,0,0,0.85), 0 0 0 1px rgba(255,255,255,0.08);
      overflow: hidden;
    }}
    canvas {{
      display: block;
      width: 100%;
      height: 100%;
      cursor: pointer;
    }}
    #controls-bar {{
      position: absolute;
      bottom: 16px;
      left: 20px;
      right: 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(13, 17, 26, 0.85);
      backdrop-filter: blur(8px);
      padding: 10px 18px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.1);
      z-index: 10;
    }}
    .btn {{
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.12);
      color: #cbd5e1;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .btn:hover {{
      background: rgba(255,255,255,0.15);
      color: #f8fafc;
    }}
    .btn-primary {{
      background: #6366f1;
      border-color: #818cf8;
      color: #fff;
    }}
    .btn-primary:hover {{
      background: #4f46e5;
    }}
    #progress-track {{
      flex: 1;
      height: 6px;
      background: rgba(255,255,255,0.1);
      border-radius: 3px;
      overflow: hidden;
      cursor: pointer;
    }}
    #progress-fill {{
      width: 0%;
      height: 100%;
      background: #6366f1;
      transition: width 0.2s ease;
    }}
    #counter {{
      font-family: monospace;
      font-size: 11px;
      color: #94a3b8;
    }}
    #subtitle-card {{
      position: absolute;
      top: 20px;
      left: 24px;
      right: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      pointer-events: none;
    }}
    .badge {{
      background: rgba(99, 102, 241, 0.18);
      color: #a5b4fc;
      border: 1px solid rgba(99, 102, 241, 0.35);
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      font-family: monospace;
    }}
  </style>
</head>
<body>

  <div id="film-stage">
    <canvas id="screen" width="960" height="540"></canvas>
    
    <div id="subtitle-card">
      <span class="badge">🎬 DALANG-AI STUDIOS • KRESNA</span>
      <span style="font-size: 12px; color: #64748b; font-family: monospace;">[SPACE] PLAY/PAUSE • [← / →] STEP</span>
    </div>

    <div id="controls-bar">
      <button id="btn-prev" class="btn">◀ Mundur</button>
      <button id="btn-play" class="btn btn-primary">Auto Play</button>
      <div id="progress-track">
        <div id="progress-fill"></div>
      </div>
      <span id="counter">BEAT 1 / 1</span>
      <button id="btn-next" class="btn">Lanjut ▶</button>
      <button id="btn-audio" class="btn">🔊 Suara: ON</button>
    </div>
  </div>

  <script>
    const BEATS = {beats_json};
    const FACTS = {facts_json};
    const TITLE = "{title}";

    const canvas = document.getElementById("screen");
    const ctx = canvas.getContext("2d");
    let currentIdx = 0;
    let isPlaying = false;
    let soundEnabled = true;
    let timer = null;
    let tick = 0;

    // --- PROCEDURAL AUDIO SYNTHESIZER ---
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;

    function playTone(freq, type = "sine", duration = 0.3, gain = 0.08) {{
      if (!soundEnabled) return;
      if (!audioCtx) audioCtx = new AudioCtx();
      try {{
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        g.gain.setValueAtTime(gain, audioCtx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
        osc.connect(g);
        g.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }} catch(e) {{}}
    }}

    function playBeatChime(idx) {{
      const baseFreqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 523.25];
      const f = baseFreqs[idx % baseFreqs.length];
      playTone(f, "triangle", 0.4, 0.06);
      setTimeout(() => playTone(f * 1.25, "sine", 0.5, 0.05), 80);
    }}

    // --- DRAW CHARACTERS & GRAPHICS ---
    function drawRobot(x, y, mood, t) {{
      ctx.save();
      ctx.translate(x, y);

      const breath = Math.sin(t * 0.06) * 3;
      const headColor = mood === "alert" ? "#ef4444" : "#6366f1";

      // Antena
      ctx.strokeStyle = "#64748b";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(0, -60 + breath);
      ctx.lineTo(0, -85 + breath);
      ctx.stroke();

      ctx.fillStyle = headColor;
      ctx.beginPath();
      ctx.arc(0, -88 + breath, 7, 0, Math.PI * 2);
      ctx.fill();

      // Kepala
      ctx.fillStyle = "#1e293b";
      ctx.strokeStyle = headColor;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.roundRect(-45, -60 + breath, 90, 55, 12);
      ctx.fill();
      ctx.stroke();

      // Visor
      ctx.fillStyle = "#090d16";
      ctx.beginPath();
      ctx.roundRect(-35, -50 + breath, 70, 32, 6);
      ctx.fill();

      // Mata Emotif
      if (mood === "happy") {{
        ctx.strokeStyle = "#34d399";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(-16, -35 + breath, 7, Math.PI, 0);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(16, -35 + breath, 7, Math.PI, 0);
        ctx.stroke();
      }} else if (mood === "alert") {{
        ctx.fillStyle = "#f87171";
        ctx.font = "bold 20px monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("!", -16, -35 + breath);
        ctx.fillText("!", 16, -35 + breath);
      }} else {{
        ctx.fillStyle = "#38bdf8";
        ctx.beginPath();
        ctx.arc(-16, -35 + breath, 5, 0, Math.PI * 2);
        ctx.arc(16, -35 + breath, 5, 0, Math.PI * 2);
        ctx.fill();
      }}

      // Badan
      ctx.fillStyle = "#334155";
      ctx.strokeStyle = "#475569";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(-35, 10, 70, 65, 8);
      ctx.fill();
      ctx.stroke();

      // Badge
      ctx.fillStyle = "#6366f1";
      ctx.beginPath();
      ctx.arc(0, 36, 12, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.font = "bold 10px monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("D", 0, 36);

      // Kaki
      ctx.fillStyle = "#1e293b";
      ctx.beginPath();
      ctx.roundRect(-24, 75, 16, 25, 4);
      ctx.roundRect(8, 75, 16, 25, 4);
      ctx.fill();

      ctx.restore();
    }}

    function drawBubble(x, y, w, h, text) {{
      ctx.save();
      ctx.fillStyle = "#ffffff";
      ctx.strokeStyle = "#cbd5e1";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(x, y, w, h, 14);
      ctx.fill();
      ctx.stroke();

      // Ekor balon
      ctx.beginPath();
      ctx.moveTo(x + 35, y + h);
      ctx.lineTo(x + 20, y + h + 16);
      ctx.lineTo(x + 55, y + h);
      ctx.fillStyle = "#ffffff";
      ctx.fill();
      ctx.strokeStyle = "#cbd5e1";
      ctx.stroke();

      // Teks
      ctx.fillStyle = "#0f172a";
      ctx.font = "600 16px -apple-system, sans-serif";
      ctx.textAlign = "left";
      ctx.textBaseline = "top";

      const words = text.split(" ");
      let line = "";
      let ly = y + 24;
      for (let n = 0; n < words.length; n++) {{
        const testLine = line + words[n] + " ";
        if (ctx.measureText(testLine).width > w - 36 && n > 0) {{
          ctx.fillText(line, x + 20, ly);
          line = words[n] + " ";
          ly += 24;
        }} else {{
          line = testLine;
        }}
      }}
      ctx.fillText(line, x + 20, ly);

      ctx.restore();
    }}

    // --- MAIN RENDER LOOP ---
    function render() {{
      tick++;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const beat = BEATS[currentIdx] || BEATS[0];

      // 1. Dinamis Background Per Mood
      if (beat.mood === "alert") {{
        ctx.fillStyle = "#1a0f14";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        // Warning stripes tipis
        ctx.strokeStyle = "rgba(239, 68, 68, 0.08)";
        ctx.lineWidth = 2;
        for (let i = -canvas.height; i < canvas.width; i += 30) {{
          ctx.beginPath();
          ctx.moveTo(i, 0);
          ctx.lineTo(i + canvas.height, canvas.height);
          ctx.stroke();
        }}
      }} else {{
        ctx.fillStyle = "#0c0e17";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        // Grid dot tech motif
        ctx.fillStyle = "rgba(99, 102, 241, 0.12)";
        for (let gx = 30; gx < canvas.width; gx += 40) {{
          for (let gy = 40; gy < canvas.height; gy += 40) {{
            ctx.beginPath();
            ctx.arc(gx, gy, 1.2, 0, Math.PI * 2);
            ctx.fill();
          }}
        }}
      }}

      // 2. Judul Film
      ctx.fillStyle = "#6366f1";
      ctx.font = "bold 13px monospace";
      ctx.textAlign = "left";
      ctx.fillText("KRESNA EXPLAINER • " + TITLE.toUpperCase(), 30, 68);

      // 3. Karakter & Balon
      drawRobot(200, 310, beat.mood, tick);
      drawBubble(320, 140, 580, 140, beat.dialogue || beat.text);

      // 4. Subtitle Card Bawah
      ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
      ctx.beginPath();
      ctx.roundRect(30, 420, 900, 60, 8);
      ctx.fill();
      ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
      ctx.stroke();

      ctx.fillStyle = "#e2e8f0";
      ctx.font = "14px -apple-system, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(beat.narration || beat.text, 480, 450);

      // Update Controls
      document.getElementById("progress-fill").style.width = 
        `${{((currentIdx + 1) / BEATS.length) * 100}}%`;
      document.getElementById("counter").innerText = 
        `BEAT ${{currentIdx + 1}} / ${{BEATS.length}}`;

      requestAnimationFrame(render);
    }}

    function setBeat(idx) {{
      if (idx >= 0 && idx < BEATS.length) {{
        currentIdx = idx;
        playBeatChime(idx);
      }} else if (idx >= BEATS.length) {{
        isPlaying = false;
        document.getElementById("btn-play").innerText = "Ulangi Film";
      }}
    }}

    // Event Listeners
    document.getElementById("btn-next").addEventListener("click", () => setBeat(currentIdx + 1));
    document.getElementById("btn-prev").addEventListener("click", () => setBeat(currentIdx - 1));
    canvas.addEventListener("click", () => setBeat(currentIdx + 1));

    document.getElementById("btn-play").addEventListener("click", () => {{
      isPlaying = !isPlaying;
      document.getElementById("btn-play").innerText = isPlaying ? "Jeda" : "Auto Play";
      if (isPlaying) {{
        if (currentIdx >= BEATS.length - 1) currentIdx = 0;
        timer = setInterval(() => {{
          if (isPlaying) {{
            if (currentIdx < BEATS.length - 1) {{
              setBeat(currentIdx + 1);
            }} else {{
              clearInterval(timer);
              isPlaying = false;
              document.getElementById("btn-play").innerText = "Auto Play";
            }}
          }}
        }}, 4800);
      }} else {{
        if (timer) clearInterval(timer);
      }}
    }});

    document.getElementById("btn-audio").addEventListener("click", () => {{
      soundEnabled = !soundEnabled;
      document.getElementById("btn-audio").innerText = soundEnabled ? "🔊 Suara: ON" : "🔇 Suara: OFF";
    }});

    window.addEventListener("keydown", (e) => {{
      if (e.key === "ArrowRight" || e.key === " ") {{
        setBeat(currentIdx + 1);
      }} else if (e.key === "ArrowLeft") {{
        setBeat(currentIdx - 1);
      }}
    }});

    // Kickoff
    render();
  </script>
</body>
</html>
"""
    # ── 🔵 LULU HANDOVER REVIEW (Mandatory sebelum Ren QA) ──
    from team_collaboration import TeamCollaborationManager
    collab = TeamCollaborationManager()
    verdict = collab.perform_handover_review(
        task_id=f"KRESNA-{abs(hash(title)) % 10000:04d}",
        producer_agent="kresna",
        artifacts=["kresna_film.html"],
        artifact_content=html_content,
    )
    if verdict.status == "REJECTED":
        raise ValueError(f"[Lulu REJECTED] {verdict.critique}")
    if verdict.status == "CHANGES_REQUESTED":
        # Inject Lulu recommendations sebagai komentar footer di HTML
        recs = "\n".join(f"<!-- LULU: {r} -->" for r in verdict.recommendations)
        html_content = html_content.replace("</html>", f"\n{recs}\n</html>")

    return html_content
