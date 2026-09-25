import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { Play, Square, Activity, Cpu, CheckCircle2, Clock, Terminal } from "lucide-react";

// Agent definitions & theme colors
const AGENTS = {
  risko: { name: "Risko", role: "Sang Dalang", color: 0x6366f1, hex: "#6366f1", pos: [0, 0, 0] },
  pingot: { name: "Pingot", role: "Wayang Data", color: 0x10b981, hex: "#10b981", pos: [-2, 0, -2] },
  zaki: { name: "Zaki", role: "Wayang Backend", color: 0xf59e0b, hex: "#f59e0b", pos: [2, 0, -2] },
  lulu: { name: "Lulu", role: "Wayang Visual", color: 0xec4899, hex: "#ec4899", pos: [-2, 0, 3] },
  mika: { name: "Mika", role: "Wayang Pujangga", color: 0x06b6d4, hex: "#06b6d4", pos: [2, 0, 3] },
  nova: { name: "Nova", role: "Wayang Patih", color: 0xf97316, hex: "#f97316", pos: [0, 0, -4] },
  kai: { name: "Kai", role: "Wayang Senopati", color: 0xef4444, hex: "#ef4444", pos: [-4, 0, -3] },
  ren: { name: "Ren", role: "Wayang Jaksa", color: 0x8b5cf6, hex: "#8b5cf6", pos: [4, 0, -3] },
};

export default function App() {
  const mountRef = useRef(null);
  const [events, setEvents] = useState([]);
  const [agentStatus, setAgentStatus] = useState({});
  const [isRunning, setIsRunning] = useState(false);
  const [activeTask, setActiveTask] = useState(null);
  const [connected, setConnected] = useState(false);

  const sceneRef = useRef(null);
  const agentMeshesRef = useRef({});

  // 1. Setup Three.js Isometric Office
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);
    sceneRef.current = scene;

    // Isometric Orthographic Camera
    const aspect = width / height;
    const d = 6;
    const camera = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 1, 1000);
    camera.position.set(20, 20, 20);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // Lights
    const ambient = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambient);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(10, 20, 10);
    dirLight.castShadow = true;
    scene.add(dirLight);

    // Grid Floor
    const grid = new THREE.GridHelper(12, 12, 0x334155, 0x1e293b);
    grid.position.y = -0.01;
    scene.add(grid);

    // Floor plane
    const floorGeo = new THREE.PlaneGeometry(12, 12);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);

    // Desk helper
    const makeDesk = (x, z) => {
      const deskGeo = new THREE.BoxGeometry(1.6, 0.8, 1.0);
      const deskMat = new THREE.MeshStandardMaterial({ color: 0x334155 });
      const desk = new THREE.Mesh(deskGeo, deskMat);
      desk.position.set(x, 0.4, z);
      desk.castShadow = true;
      scene.add(desk);

      // Laptop
      const lapGeo = new THREE.BoxGeometry(0.5, 0.05, 0.4);
      const lapMat = new THREE.MeshStandardMaterial({ color: 0x64748b, emissive: 0x38bdf8, emissiveIntensity: 0.2 });
      const lap = new THREE.Mesh(lapGeo, lapMat);
      lap.position.set(x, 0.83, z);
      scene.add(lap);
    };

    // Spawn Desks & Agent Avatars
    Object.entries(AGENTS).forEach(([id, data]) => {
      const [x, y, z] = data.pos;
      makeDesk(x, z);

      // Agent Mesh (Cute cylinder/capsule avatar)
      const group = new THREE.Group();

      const bodyGeo = new THREE.CylinderGeometry(0.25, 0.25, 0.7, 16);
      const bodyMat = new THREE.MeshStandardMaterial({ color: data.color, roughness: 0.3 });
      const body = new THREE.Mesh(bodyGeo, bodyMat);
      body.position.y = 1.1;
      body.castShadow = true;
      group.add(body);

      // Head
      const headGeo = new THREE.SphereGeometry(0.2, 16, 16);
      const headMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc });
      const head = new THREE.Mesh(headGeo, headMat);
      head.position.y = 1.6;
      head.castShadow = true;
      group.add(head);

      // Status Halo (glows when active)
      const haloGeo = new THREE.RingGeometry(0.4, 0.5, 32);
      const haloMat = new THREE.MeshBasicMaterial({ color: data.color, side: THREE.DoubleSide });
      const halo = new THREE.Mesh(haloGeo, haloMat);
      halo.rotation.x = Math.PI / 2;
      halo.position.y = 0.02;
      halo.visible = false;
      group.add(halo);

      group.position.set(x, 0, z + 0.8);
      scene.add(group);

      agentMeshesRef.current[id] = { group, halo, isBouncing: false, originY: 1.1 };
    });

    // Animation Loop
    let clock = new THREE.Clock();
    let animId;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      // Idle / Working bounce animation for agents
      Object.entries(agentMeshesRef.current).forEach(([id, item]) => {
        if (item.isBouncing) {
          item.group.position.y = Math.sin(elapsed * 8) * 0.15;
          item.halo.rotation.z = elapsed * 2;
        } else {
          item.group.position.y = 0;
        }
      });

      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      const a = w / h;
      camera.left = -d * a;
      camera.right = d * a;
      camera.top = d;
      camera.bottom = -d;
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

  // 2. Connect to WebSocket Event Stream
  useEffect(() => {
    let ws;
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
              agentMesh.isBouncing = true;
              agentMesh.halo.visible = true;
              setActiveTask({ agent: ev.agent, task: ev.message, id: ev.task_id });
            } else if (ev.event_type === "task_completed" || ev.event_type === "task_failed") {
              agentMesh.isBouncing = false;
              agentMesh.halo.visible = false;
            }
          }

          if (ev.event_type === "orchestration_finished") {
            setIsRunning(false);
            setActiveTask(null);
            Object.values(agentMeshesRef.current).forEach((m) => {
              m.isBouncing = false;
              m.halo.visible = false;
            });
          }
        } catch (err) {
          console.error("WS Parse Error", err);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        setTimeout(connect, 3000);
      };
    };

    connect();
    return () => ws && ws.close();
  }, []);

  // Fetch initial agent status
  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:8765/agents/status");
      const data = await res.json();
      const statusMap = {};
      data.forEach((a) => (statusMap[a.agent] = a));
      setAgentStatus(statusMap);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchStatus();
    const iv = setInterval(fetchStatus, 4000);
    return () => clearInterval(iv);
  }, []);

  // Trigger Orchestration
  const handleStart = async () => {
    try {
      setIsRunning(true);
      await fetch("http://localhost:8765/orchestrate/start?max_cycles=10", { method: "POST" });
    } catch (e) {
      console.error(e);
      setIsRunning(false);
    }
  };

  const handleStop = async () => {
    try {
      await fetch("http://localhost:8765/orchestrate/stop", { method: "POST" });
      setIsRunning(false);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#090d16", color: "#f8fafc", fontFamily: "sans-serif", overflow: "hidden" }}>
      {/* LEFT: 3D Isometric View */}
      <div style={{ flex: 1, position: "relative", display: "flex", flexDirection: "column" }}>
        {/* Top Bar */}
        <div style={{ padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #1e293b", backgroundColor: "#0f172a" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: connected ? "#10b981" : "#ef4444" }} />
            <h1 style={{ margin: 0, fontSize: "1.2rem", fontWeight: "bold", letterSpacing: "1px" }}>🎭 DALANG<span style={{ color: "#f59e0b" }}>-AI</span> <span style={{ color: "#64748b", fontSize: "0.85rem", fontWeight: "normal" }}>MULTI-AGENT AUTONOMOUS STUDIO</span></h1>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={handleStart}
              disabled={isRunning}
              style={{
                display: "flex", alignItems: "center", gap: 6,
                backgroundColor: isRunning ? "#334155" : "#4f46e5",
                color: "#fff", border: "none", padding: "8px 16px", borderRadius: 6, cursor: isRunning ? "not-allowed" : "pointer", fontWeight: "bold"
              }}
            >
              <Play size={16} /> Start Sprint
            </button>
            <button
              onClick={handleStop}
              disabled={!isRunning}
              style={{
                display: "flex", alignItems: "center", gap: 6,
                backgroundColor: !isRunning ? "#334155" : "#ef4444",
                color: "#fff", border: "none", padding: "8px 16px", borderRadius: 6, cursor: !isRunning ? "not-allowed" : "pointer", fontWeight: "bold"
              }}
            >
              <Square size={16} /> Stop
            </button>
          </div>
        </div>

        {/* Three.js Canvas Container */}
        <div ref={mountRef} style={{ flex: 1, width: "100%", height: "100%" }} />

        {/* Floating Active Task Overlay */}
        {activeTask && (
          <div style={{ position: "absolute", bottom: 20, left: 20, backgroundColor: "#1e293b", border: "1px solid #3b82f6", padding: "12px 18px", borderRadius: 8, maxWidth: 450, boxShadow: "0 10px 25px rgba(0,0,0,0.5)" }}>
            <div style={{ fontSize: "0.75rem", color: "#94a3b8", textTransform: "uppercase", marginBottom: 4 }}>
              Active Task • {activeTask.agent.toUpperCase()}
            </div>
            <div style={{ fontSize: "0.95rem", fontWeight: "bold", color: "#f8fafc" }}>
              [{activeTask.id}] {activeTask.task}
            </div>
          </div>
        )}
      </div>

      {/* RIGHT: Status Panels (Roadmap + Live Events) */}
      <div style={{ width: 440, borderLeft: "1px solid #1e293b", display: "flex", flexDirection: "column", backgroundColor: "#0f172a" }}>
        {/* Agent Cards */}
        <div style={{ padding: 16, borderBottom: "1px solid #1e293b" }}>
          <div style={{ fontSize: "0.8rem", color: "#94a3b8", fontWeight: "bold", marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
            <Cpu size={14} /> AGENT STATUS
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {Object.entries(AGENTS).map(([id, info]) => {
              const st = agentStatus[id] || { completed: 0, total_tasks: 0 };
              return (
                <div key={id} style={{ backgroundColor: "#1e293b", padding: "10px 12px", borderRadius: 6, borderLeft: `4px solid ${info.hex}` }}>
                  <div style={{ fontSize: "0.85rem", fontWeight: "bold", color: "#f8fafc" }}>{info.name}</div>
                  <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>{info.role}</div>
                  <div style={{ fontSize: "0.75rem", marginTop: 6, color: "#cbd5e1" }}>
                    {st.completed} / {st.total_tasks} tasks done
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Live Event Log */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
          <div style={{ padding: "12px 16px", borderBottom: "1px solid #1e293b", fontSize: "0.8rem", color: "#94a3b8", fontWeight: "bold", display: "flex", alignItems: "center", gap: 6 }}>
            <Terminal size={14} /> LIVE ACTIVITY FEED ({events.length})
          </div>
          <div style={{ flex: 1, overflowY: "auto", padding: 12, display: "flex", flexDirection: "column", gap: 8 }}>
            {events.length === 0 ? (
              <div style={{ textAlign: "center", color: "#64748b", marginTop: 40, fontSize: "0.85rem" }}>
                Waiting for agent events... Click "Start Sprint" to run.
              </div>
            ) : (
              events.map((ev, idx) => (
                <div key={idx} style={{ backgroundColor: "#1e293b", padding: "8px 12px", borderRadius: 6, fontSize: "0.8rem", borderLeft: `3px solid ${AGENTS[ev.agent]?.hex || "#64748b"}` }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 2 }}>
                    <span style={{ fontWeight: "bold", color: AGENTS[ev.agent]?.hex || "#f8fafc" }}>{ev.agent?.toUpperCase()}</span>
                    <span style={{ color: "#64748b", fontSize: "0.7rem" }}>{new Date(ev.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div style={{ color: "#cbd5e1" }}>{ev.message}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
