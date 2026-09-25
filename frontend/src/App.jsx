import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { Cpu, Terminal, Sparkles, UserCheck, Coffee } from "lucide-react";

// 8 Wayang Roster & Visual Styles
const AGENTS = {
  risko: { name: "Risko", role: "Sang Dalang", title: "Master Orchestrator", color: 0x6366f1, hex: "#6366f1", pos: [0, 0, 0] },
  pingot: { name: "Pingot", role: "Wayang Data", title: "Data Architect", color: 0x10b981, hex: "#10b981", pos: [-3, 0, -2.5] },
  zaki: { name: "Zaki", role: "Wayang Backend", title: "API & System Engineer", color: 0xf59e0b, hex: "#f59e0b", pos: [3, 0, -2.5] },
  lulu: { name: "Lulu", role: "Wayang Visual", title: "UI/UX & 3D Designer", color: 0xec4899, hex: "#ec4899", pos: [-3, 0, 3] },
  mika: { name: "Mika", role: "Wayang Pujangga", title: "Technical Writer", color: 0x06b6d4, hex: "#06b6d4", pos: [3, 0, 3] },
  nova: { name: "Nova", role: "Wayang Patih", title: "DevOps & CI/CD", color: 0xf97316, hex: "#f97316", pos: [0, 0, -5] },
  kai: { name: "Kai", role: "Wayang Senopati", title: "Security Auditor", color: 0xef4444, hex: "#ef4444", pos: [-5.5, 0, 0] },
  ren: { name: "Ren", role: "Wayang Jaksa", title: "QA & Test Automation", color: 0x8b5cf6, hex: "#8b5cf6", pos: [5.5, 0, 0] },
};

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

  // 1. Setup Three.js 3D Isometric Office Studio
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0f1d);
    scene.fog = new THREE.FogExp2(0x0a0f1d, 0.025);
    sceneRef.current = scene;

    // Camera: Isometric perspective
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(16, 18, 22);
    camera.lookAt(0, 1, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    container.appendChild(renderer.domElement);

    // OrbitControls for smooth interactive navigation
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2.1;
    controls.minDistance = 8;
    controls.maxDistance = 45;
    controls.target.set(0, 1, 0);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xdbeafe, 0.85);
    scene.add(ambientLight);

    const mainLight = new THREE.DirectionalLight(0xffffff, 1.8);
    mainLight.position.set(15, 25, 12);
    mainLight.castShadow = true;
    mainLight.shadow.mapSize.width = 2048;
    mainLight.shadow.mapSize.height = 2048;
    mainLight.shadow.camera.near = 0.5;
    mainLight.shadow.camera.far = 60;
    mainLight.shadow.camera.left = -15;
    mainLight.shadow.camera.right = 15;
    mainLight.shadow.camera.top = 15;
    mainLight.shadow.camera.bottom = -15;
    mainLight.shadow.bias = -0.0005;
    scene.add(mainLight);

    // Subtle blue fill light
    const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.6);
    fillLight.position.set(-15, 10, -10);
    scene.add(fillLight);

    // Grid Floor
    const grid = new THREE.GridHelper(24, 24, 0x1e293b, 0x0f172a);
    grid.position.y = 0.01;
    scene.add(grid);

    // Main Studio Floor
    const floorGeo = new THREE.PlaneGeometry(28, 28);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      roughness: 0.6,
      metalness: 0.1,
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);

    // Outer Room Border Ring
    const borderGeo = new THREE.RingGeometry(13.8, 14.2, 64);
    const borderMat = new THREE.MeshBasicMaterial({ color: 0x1e293b, side: THREE.DoubleSide });
    const border = new THREE.Mesh(borderGeo, borderMat);
    border.rotation.x = -Math.PI / 2;
    border.position.y = 0.02;
    scene.add(border);

    // Function to create a Modern Workspace Desk + Opened Laptop
    const createDeskWithLaptop = (x, z) => {
      const deskGroup = new THREE.Group();
      deskGroup.position.set(x, 0, z);

      // Desk Top (Matte Charcoal Wood)
      const topGeo = new THREE.BoxGeometry(1.9, 0.08, 1.1);
      const topMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 });
      const top = new THREE.Mesh(topGeo, topMat);
      top.position.y = 0.76;
      top.castShadow = true;
      top.receiveShadow = true;
      deskGroup.add(top);

      // Desk Metal Legs
      const legGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.74, 12);
      const legMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8, roughness: 0.2 });
      [
        [-0.85, -0.45],
        [0.85, -0.45],
        [-0.85, 0.45],
        [0.85, 0.45],
      ].forEach(([lx, lz]) => {
        const leg = new THREE.Mesh(legGeo, legMat);
        leg.position.set(lx, 0.37, lz);
        leg.castShadow = true;
        deskGroup.add(leg);
      });

      // Laptop Base
      const lapBaseGeo = new THREE.BoxGeometry(0.52, 0.02, 0.38);
      const lapBaseMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.6, roughness: 0.3 });
      const lapBase = new THREE.Mesh(lapBaseGeo, lapBaseMat);
      lapBase.position.set(0, 0.81, 0.05);
      lapBase.castShadow = true;
      deskGroup.add(lapBase);

      // Laptop Keyboard Area
      const kbGeo = new THREE.BoxGeometry(0.44, 0.005, 0.2);
      const kbMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.9 });
      const kb = new THREE.Mesh(kbGeo, kbMat);
      kb.position.set(0, 0.825, 0.08);
      deskGroup.add(kb);

      // Laptop Screen (Opened & Tilted 105 degrees)
      const screenGroup = new THREE.Group();
      screenGroup.position.set(0, 0.82, -0.14);

      // Screen Lid
      const lidGeo = new THREE.BoxGeometry(0.52, 0.35, 0.015);
      const lidMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.6, roughness: 0.3 });
      const lid = new THREE.Mesh(lidGeo, lidMat);
      lid.position.set(0, 0.175, 0);
      lid.castShadow = true;
      screenGroup.add(lid);

      // Screen Display Face (Emissive — glows brighter when coding!)
      const displayGeo = new THREE.PlaneGeometry(0.48, 0.31);
      const displayMat = new THREE.MeshStandardMaterial({
        color: 0x000000,
        emissive: 0x38bdf8,
        emissiveIntensity: 0.15,
        roughness: 0.2,
      });
      const display = new THREE.Mesh(displayGeo, displayMat);
      display.position.set(0, 0.175, 0.009);
      screenGroup.add(display);

      // Tilt screen backward like an open laptop
      screenGroup.rotation.x = THREE.MathUtils.degToRad(-15);
      deskGroup.add(screenGroup);

      // Screen Glow PointLight (Illuminates face when working)
      const screenLight = new THREE.PointLight(0x38bdf8, 0.1, 1.8);
      screenLight.position.set(0, 1.0, -0.05);
      deskGroup.add(screenLight);

      // Modern Ergonomic Office Chair
      const chairGroup = new THREE.Group();
      chairGroup.position.set(0, 0, 0.72);

      // Chair Seat
      const seatGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.06, 24);
      const seatMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
      const seat = new THREE.Mesh(seatGeo, seatMat);
      seat.position.y = 0.45;
      seat.castShadow = true;
      chairGroup.add(seat);

      // Chair Backrest
      const backGeo = new THREE.BoxGeometry(0.42, 0.45, 0.06);
      const backMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.8 });
      const back = new THREE.Mesh(backGeo, backMat);
      back.position.set(0, 0.75, 0.25);
      back.castShadow = true;
      chairGroup.add(back);

      // Chair Stem & Wheels Base
      const stemGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.45, 12);
      const stemMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.8 });
      const stem = new THREE.Mesh(stemGeo, stemMat);
      stem.position.y = 0.225;
      chairGroup.add(stem);

      const baseGeo = new THREE.CylinderGeometry(0.32, 0.32, 0.02, 5);
      const base = new THREE.Mesh(baseGeo, stemMat);
      base.position.y = 0.02;
      chairGroup.add(base);

      deskGroup.add(chairGroup);
      scene.add(deskGroup);

      return { displayMat, screenLight };
    };

    // Function to create an Articulated Human Avatar (Wayang)
    const createWayangHuman = (id, data) => {
      const [x, y, z] = data.pos;
      const deskObjects = createDeskWithLaptop(x, z);

      // Human root group sits at the chair position
      const humanGroup = new THREE.Group();
      humanGroup.position.set(x, 0, z + 0.72);

      // 1. Lower Body / Legs (Sitting pose)
      const pantsMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.7 });

      // Thighs (horizontal forward towards desk)
      const thighGeo = new THREE.BoxGeometry(0.12, 0.12, 0.34);
      const leftThigh = new THREE.Mesh(thighGeo, pantsMat);
      leftThigh.position.set(-0.11, 0.45, -0.14);
      humanGroup.add(leftThigh);

      const rightThigh = new THREE.Mesh(thighGeo, pantsMat);
      rightThigh.position.set(0.11, 0.45, -0.14);
      humanGroup.add(rightThigh);

      // Calves (vertical down to floor)
      const calfGeo = new THREE.BoxGeometry(0.11, 0.38, 0.11);
      const leftCalf = new THREE.Mesh(calfGeo, pantsMat);
      leftCalf.position.set(-0.11, 0.22, -0.28);
      humanGroup.add(leftCalf);

      const rightCalf = new THREE.Mesh(calfGeo, pantsMat);
      rightCalf.position.set(0.11, 0.22, -0.28);
      humanGroup.add(rightCalf);

      // Shoes
      const shoeGeo = new THREE.BoxGeometry(0.12, 0.06, 0.18);
      const shoeMat = new THREE.MeshStandardMaterial({ color: 0x020617 });
      const leftShoe = new THREE.Mesh(shoeGeo, shoeMat);
      leftShoe.position.set(-0.11, 0.03, -0.31);
      humanGroup.add(leftShoe);

      const rightShoe = new THREE.Mesh(shoeGeo, shoeMat);
      rightShoe.position.set(0.11, 0.03, -0.31);
      humanGroup.add(rightShoe);

      // 2. Upper Body Pivot (for leaning & swiveling)
      const torsoPivot = new THREE.Group();
      torsoPivot.position.set(0, 0.52, 0);

      // Torso / Shirt (Color of the Wayang)
      const shirtMat = new THREE.MeshStandardMaterial({
        color: data.color,
        roughness: 0.4,
        metalness: 0.1,
      });
      const torsoGeo = new THREE.BoxGeometry(0.36, 0.42, 0.22);
      const torso = new THREE.Mesh(torsoGeo, shirtMat);
      torso.position.y = 0.21;
      torso.castShadow = true;
      torsoPivot.add(torso);

      // Neck & Head
      const skinMat = new THREE.MeshStandardMaterial({ color: 0xfbd0b3, roughness: 0.6 });

      const neckGeo = new THREE.CylinderGeometry(0.06, 0.07, 0.1, 12);
      const neck = new THREE.Mesh(neckGeo, skinMat);
      neck.position.y = 0.45;
      torsoPivot.add(neck);

      // Head Group (for tilting & nodding)
      const headGroup = new THREE.Group();
      headGroup.position.set(0, 0.58, 0);

      const headGeo = new THREE.SphereGeometry(0.14, 20, 20);
      const head = new THREE.Mesh(headGeo, skinMat);
      head.castShadow = true;
      headGroup.add(head);

      // Hair / Tech Visor (gives clear visual facing orientation)
      const hairMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.9 });
      const hairGeo = new THREE.SphereGeometry(0.145, 16, 16, 0, Math.PI * 2, 0, Math.PI / 1.8);
      const hair = new THREE.Mesh(hairGeo, hairMat);
      hair.position.y = 0.03;
      headGroup.add(hair);

      // Face Visor / Eyewear (Tech Accent)
      const visorGeo = new THREE.BoxGeometry(0.18, 0.05, 0.08);
      const visorMat = new THREE.MeshStandardMaterial({
        color: 0x020617,
        emissive: data.color,
        emissiveIntensity: 0.4,
        metalness: 0.9,
      });
      const visor = new THREE.Mesh(visorGeo, visorMat);
      visor.position.set(0, 0.02, -0.12); // Front of face is negative Z
      headGroup.add(visor);

      torsoPivot.add(headGroup);

      // 3. Arms & Hands with Articulated Shoulders
      // Left Arm
      const leftShoulder = new THREE.Group();
      leftShoulder.position.set(-0.23, 0.38, 0);
      const leftArmGeo = new THREE.CylinderGeometry(0.05, 0.045, 0.32, 12);
      const leftArm = new THREE.Mesh(leftArmGeo, shirtMat);
      leftArm.position.y = -0.16;
      leftArm.castShadow = true;
      leftShoulder.add(leftArm);

      const leftHandGeo = new THREE.SphereGeometry(0.045, 12, 12);
      const leftHand = new THREE.Mesh(leftHandGeo, skinMat);
      leftHand.position.y = -0.33;
      leftShoulder.add(leftHand);
      torsoPivot.add(leftShoulder);

      // Right Arm
      const rightShoulder = new THREE.Group();
      rightShoulder.position.set(0.23, 0.38, 0);
      const rightArmGeo = new THREE.CylinderGeometry(0.05, 0.045, 0.32, 12);
      const rightArm = new THREE.Mesh(rightArmGeo, shirtMat);
      rightArm.position.y = -0.16;
      rightArm.castShadow = true;
      rightShoulder.add(rightArm);

      const rightHandGeo = new THREE.SphereGeometry(0.045, 12, 12);
      const rightHand = new THREE.Mesh(rightHandGeo, skinMat);
      rightHand.position.y = -0.33;
      rightShoulder.add(rightHand);
      torsoPivot.add(rightShoulder);

      humanGroup.add(torsoPivot);

      // Active Energy Floor Ring
      const ringGeo = new THREE.RingGeometry(0.65, 0.75, 36);
      const ringMat = new THREE.MeshBasicMaterial({
        color: data.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0,
      });
      const energyRing = new THREE.Mesh(ringGeo, ringMat);
      energyRing.rotation.x = -Math.PI / 2;
      energyRing.position.y = 0.03;
      humanGroup.add(energyRing);

      scene.add(humanGroup);

      // Store in Ref with animation state
      agentMeshesRef.current[id] = {
        humanGroup,
        torsoPivot,
        headGroup,
        leftShoulder,
        rightShoulder,
        energyRing,
        deskObjects,
        // State flags
        isWorking: false,
        // Target Rotations
        // Idle: Facing outward / toward user (rotation.y = 0 or slightly angled)
        // Working: Swiveled facing directly into the laptop (rotation.y = PI)
        targetRotationY: 0,
        currentRotationY: 0,
      };
    };

    // Spawn 8 Wayangs in Studio
    Object.entries(AGENTS).forEach(([id, data]) => {
      createWayangHuman(id, data);
    });

    // Main 60FPS Three.js Animation Loop
    let clock = new THREE.Clock();
    let animId;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();
      controls.update();

      Object.entries(agentMeshesRef.current).forEach(([id, agent]) => {
        const {
          humanGroup,
          torsoPivot,
          headGroup,
          leftShoulder,
          rightShoulder,
          energyRing,
          deskObjects,
          isWorking,
        } = agent;

        // Smooth Swivel Animation (Lerp rotation)
        const targetRot = isWorking ? 0 : Math.PI * 0.75; 
        // Note on coordinates: Desk is at (0, 0, 0) relative to chair which is at +0.72 Z.
        // Facing desk is towards -Z (rotation.y = 0).
        // Facing away/idle is turned towards the room/camera (rotation.y = ~135 deg).
        agent.targetRotationY = isWorking ? 0 : Math.PI * 0.75;
        agent.currentRotationY = THREE.MathUtils.lerp(agent.currentRotationY, agent.targetRotationY, 0.06);
        humanGroup.rotation.y = agent.currentRotationY;

        if (isWorking) {
          // ==========================================
          // 💻 WORKING MODE: Menghadap Laptop & Ngetik
          // ==========================================
          // 1. Torso leans forward toward the desk
          torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, 0.16, 0.08);

          // 2. Head looks down at laptop display
          headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, 0.28, 0.08);
          headGroup.rotation.y = Math.sin(elapsed * 2) * 0.04;

          // 3. Arms extended forward onto the keyboard typing
          const leftTyping = Math.sin(elapsed * 22) * 0.12;
          const rightTyping = Math.cos(elapsed * 22 + 1) * 0.12;
          leftShoulder.rotation.x = -1.1 + leftTyping;
          leftShoulder.rotation.z = -0.2;
          rightShoulder.rotation.x = -1.1 + rightTyping;
          rightShoulder.rotation.z = 0.2;

          // 4. Laptop screen lights up with vivid pulse
          deskObjects.displayMat.emissiveIntensity = 0.85 + Math.sin(elapsed * 8) * 0.15;
          deskObjects.screenLight.intensity = 0.9 + Math.sin(elapsed * 6) * 0.2;

          // 5. Active Energy Ring glows and rotates on floor
          energyRing.material.opacity = THREE.MathUtils.lerp(energyRing.material.opacity, 0.8, 0.05);
          energyRing.rotation.z = elapsed * 1.5;
        } else {
          // ==========================================
          // ☕ IDLE MODE: Santai & Menghadap ke Luar
          // ==========================================
          // 1. Torso leans back comfortably in the chair
          torsoPivot.rotation.x = THREE.MathUtils.lerp(torsoPivot.rotation.x, -0.05, 0.05);
          torsoPivot.position.y = 0.52 + Math.sin(elapsed * 1.8 + id.charCodeAt(0)) * 0.01; // gentle breathing

          // 2. Head looks around casually
          headGroup.rotation.x = THREE.MathUtils.lerp(headGroup.rotation.x, 0, 0.05);
          headGroup.rotation.y = Math.sin(elapsed * 0.7 + id.charCodeAt(1)) * 0.35; // looks left & right

          // 3. Arms rest down naturally at sides
          leftShoulder.rotation.x = THREE.MathUtils.lerp(leftShoulder.rotation.x, 0.15, 0.08);
          leftShoulder.rotation.z = THREE.MathUtils.lerp(leftShoulder.rotation.z, -0.15, 0.08);
          rightShoulder.rotation.x = THREE.MathUtils.lerp(rightShoulder.rotation.x, 0.15, 0.08);
          rightShoulder.rotation.z = THREE.MathUtils.lerp(rightShoulder.rotation.z, 0.15, 0.08);

          // 4. Laptop Screen is dim (Screen Saver / Sleep)
          deskObjects.displayMat.emissiveIntensity = 0.1;
          deskObjects.screenLight.intensity = 0.05;

          // 5. Energy Ring fades out
          energyRing.material.opacity = THREE.MathUtils.lerp(energyRing.material.opacity, 0, 0.08);
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

  // 2. Connect to Dalang-AI Live Backend WebSocket Event Stream
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

          // Active count is derived from workingMap
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

  // 3. Periodic Sync with Backend Agent Status API
  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:8765/agents/status");
      if (!res.ok) return;
      const data = await res.json();
      const statusMap = {};
      let workingNow = 0;

      data.forEach((a) => {
        statusMap[a.agent] = a;
        const mesh = agentMeshesRef.current[a.agent];
        if (mesh) {
          // If agent has active/in_progress tasks, set working = true
          const isActive = a.in_progress > 0;
          mesh.isWorking = isActive;
          if (isActive) workingNow++;
        }
      });

      setAgentStatus(statusMap);
      // activeWayangCount is derived from workingMap
    } catch (e) {
      // Backend maybe offline
    }
  };

  useEffect(() => {
    fetchStatus();
    const iv = setInterval(fetchStatus, 3500);
    return () => clearInterval(iv);
  }, []);

  // Demo Trigger: Click on an agent card to toggle them working/idle (for instant visual testing)
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
          task: `Menghadap laptop: fokus pengerjaan tugas & kode...`,
        });
        setEvents((evs) => [
          {
            agent: agentId,
            event_type: "task_dispatched",
            message: `Menghadap laptop: mulai bekerja mandiri.`,
            timestamp: new Date().toISOString(),
          },
          ...evs.slice(0, 49),
        ]);
      } else {
        setEvents((evs) => [
          {
            agent: agentId,
            event_type: "task_completed",
            message: `Tugas selesai. Menghadap santai (idle).`,
            timestamp: new Date().toISOString(),
          },
          ...evs.slice(0, 49),
        ]);
      }

      return nextMap;
    });
  };

  return (
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#060913", color: "#f8fafc", fontFamily: "system-ui, -apple-system, sans-serif", overflow: "hidden" }}>
      {/* LEFT: 3D Isometric Studio Viewport */}
      <div style={{ flex: 1, position: "relative", display: "flex", flexDirection: "column" }}>
        
        {/* Top Header Bar: Clean & Autonomous (Tanpa Tombol Start/Stop) */}
        <div style={{
          padding: "14px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          backgroundColor: "rgba(10, 15, 29, 0.95)",
          backdropFilter: "blur(12px)",
          zIndex: 10
        }}>
          {/* Logo & Autonomous Dalang Badge */}
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "1.3rem" }}>🎭</span>
              <h1 style={{ margin: 0, fontSize: "1.15rem", fontWeight: "800", letterSpacing: "0.5px" }}>
                DALANG<span style={{ color: "#38bdf8" }}>-AI</span>
              </h1>
              <span style={{
                fontSize: "0.68rem",
                letterSpacing: "1px",
                textTransform: "uppercase",
                backgroundColor: "#1e293b",
                color: "#94a3b8",
                padding: "2px 8px",
                borderRadius: "4px",
                border: "1px solid #334155"
              }}>
                Studio 3D Isometrik
              </span>
            </div>

            {/* Live Autopilot Status */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "4px 12px",
              backgroundColor: "rgba(16, 185, 129, 0.1)",
              border: "1px solid rgba(16, 185, 129, 0.3)",
              borderRadius: "20px"
            }}>
              <div style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: "#10b981",
                boxShadow: "0 0 8px #10b981"
              }} />
              <span style={{ fontSize: "0.75rem", fontWeight: "600", color: "#34d399", letterSpacing: "0.5px" }}>
                OTONOM REALTIME
              </span>
            </div>
          </div>

          {/* Realtime Studio Summary (Active vs Idle) */}
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.8rem", color: "#cbd5e1" }}>
              <UserCheck size={15} style={{ color: "#38bdf8" }} />
              <span>Bekerja: <strong style={{ color: "#38bdf8" }}>{activeWayangCount}</strong></span>
            </div>

            <div style={{ width: 1, height: 16, backgroundColor: "#334155" }} />

            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.8rem", color: "#94a3b8" }}>
              <Coffee size={15} style={{ color: "#64748b" }} />
              <span>Istirahat (Idle): <strong style={{ color: "#cbd5e1" }}>{8 - activeWayangCount}</strong></span>
            </div>

            <div style={{ width: 1, height: 16, backgroundColor: "#334155" }} />

            {/* Connection Indicator */}
            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.75rem", color: connected ? "#10b981" : "#ef4444" }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: connected ? "#10b981" : "#ef4444" }} />
              <span>{connected ? "Server Terhubung" : "Menghubungkan..."}</span>
            </div>
          </div>
        </div>

        {/* 3D Canvas Mounting Area */}
        <div ref={mountRef} style={{ flex: 1, width: "100%", height: "100%", cursor: "grab" }} />

        {/* Floating Active Task Card (Pop-up saat ada wayang ngetik di laptop) */}
        {activeTask && (
          <div style={{
            position: "absolute",
            bottom: 24,
            left: 24,
            backgroundColor: "rgba(15, 23, 42, 0.92)",
            border: `1px solid ${AGENTS[activeTask.agent]?.hex || "#38bdf8"}`,
            padding: "14px 20px",
            borderRadius: 10,
            maxWidth: 480,
            boxShadow: "0 20px 40px rgba(0,0,0,0.6)",
            backdropFilter: "blur(16px)",
            animation: "fadeIn 0.3s ease-out"
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  backgroundColor: AGENTS[activeTask.agent]?.hex || "#38bdf8",
                  boxShadow: `0 0 10px ${AGENTS[activeTask.agent]?.hex || "#38bdf8"}`
                }} />
                <span style={{ fontSize: "0.75rem", fontWeight: "700", color: AGENTS[activeTask.agent]?.hex || "#38bdf8", textTransform: "uppercase", letterSpacing: "1px" }}>
                  {AGENTS[activeTask.agent]?.name} • {AGENTS[activeTask.agent]?.role}
                </span>
              </div>
              <span style={{ fontSize: "0.7rem", color: "#64748b", fontFamily: "monospace" }}>{activeTask.id}</span>
            </div>
            <div style={{ fontSize: "0.92rem", fontWeight: "600", color: "#f8fafc", lineHeight: "1.4" }}>
              {activeTask.task}
            </div>
            <div style={{ marginTop: 8, fontSize: "0.72rem", color: "#94a3b8", display: "flex", alignItems: "center", gap: 4 }}>
              <Sparkles size={12} style={{ color: "#38bdf8" }} /> Menghadap laptop & menjalankan tugas secara otonom
            </div>
          </div>
        )}

        {/* Camera Navigation Tip */}
        <div style={{
          position: "absolute",
          bottom: 24,
          right: 24,
          backgroundColor: "rgba(10, 15, 29, 0.75)",
          border: "1px solid rgba(255,255,255,0.06)",
          padding: "6px 12px",
          borderRadius: 6,
          fontSize: "0.7rem",
          color: "#64748b",
          pointerEvents: "none"
        }}>
          💡 Klik & geser mouse untuk putar ruangan 3D • Scroll untuk zoom
        </div>
      </div>

      {/* RIGHT SIDEBAR: Roster Para Wayang & Live Terminal Feed */}
      <div style={{
        width: 450,
        borderLeft: "1px solid rgba(255,255,255,0.08)",
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#0a0f1d"
      }}>
        {/* Roster Para Wayang */}
        <div style={{ padding: "18px 20px", borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ fontSize: "0.78rem", color: "#94a3b8", fontWeight: "700", letterSpacing: "1px", textTransform: "uppercase", marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
            <Cpu size={15} style={{ color: "#38bdf8" }} />
            ROSTER 8 WAYANG (KLIK KARTU UNTUK TES GERAK)
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {Object.entries(AGENTS).map(([id, info]) => {
              const isWorking = Boolean(workingMap[id]);
              const st = agentStatus[id] || { completed: 0, total_tasks: 0 };

              return (
                <div
                  key={id}
                  onClick={() => toggleAgentWorkState(id)}
                  style={{
                    backgroundColor: isWorking ? "rgba(30, 41, 59, 0.9)" : "rgba(15, 23, 42, 0.6)",
                    padding: "10px 12px",
                    borderRadius: 8,
                    borderLeft: `4px solid ${info.hex}`,
                    border: isWorking ? `1px solid ${info.hex}` : "1px solid rgba(255,255,255,0.04)",
                    borderLeftWidth: "4px",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                  title="Klik untuk mensimulasikan tugas ke wayang ini"
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "0.85rem", fontWeight: "700", color: "#f8fafc" }}>{info.name}</span>
                    <span style={{
                      fontSize: "0.65rem",
                      fontWeight: "700",
                      padding: "2px 6px",
                      borderRadius: 4,
                      backgroundColor: isWorking ? "rgba(56, 189, 248, 0.2)" : "rgba(100, 116, 139, 0.2)",
                      color: isWorking ? "#38bdf8" : "#94a3b8"
                    }}>
                      {isWorking ? "💻 NGETIK" : "☕ IDLE"}
                    </span>
                  </div>
                  <div style={{ fontSize: "0.72rem", color: "#94a3b8", marginTop: 2 }}>{info.role}</div>
                  <div style={{ fontSize: "0.68rem", color: "#64748b", marginTop: 4 }}>
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
            padding: "12px 20px",
            borderBottom: "1px solid rgba(255,255,255,0.08)",
            fontSize: "0.78rem",
            color: "#94a3b8",
            fontWeight: "700",
            letterSpacing: "1px",
            textTransform: "uppercase",
            display: "flex",
            alignItems: "center",
            gap: 8
          }}>
            <Terminal size={15} style={{ color: "#38bdf8" }} />
            LOG AKTIVITAS STUDIO ({events.length})
          </div>

          <div style={{ flex: 1, overflowY: "auto", padding: 14, display: "flex", flexDirection: "column", gap: 8 }}>
            {events.length === 0 ? (
              <div style={{ textAlign: "center", color: "#64748b", marginTop: 60, fontSize: "0.85rem" }}>
                <Coffee size={28} style={{ margin: "0 auto 10px", opacity: 0.5 }} />
                Semua Wayang saat ini sedang santai (Idle).<br />
                Karakter akan otomatis berputar menghadap laptop saat ada lakon tugas baru!
              </div>
            ) : (
              events.map((ev, idx) => (
                <div
                  key={idx}
                  style={{
                    backgroundColor: "rgba(15, 23, 42, 0.7)",
                    padding: "10px 12px",
                    borderRadius: 6,
                    fontSize: "0.78rem",
                    borderLeft: `3px solid ${AGENTS[ev.agent]?.hex || "#64748b"}`,
                    border: "1px solid rgba(255,255,255,0.04)",
                    borderLeftWidth: "3px"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                    <span style={{ fontWeight: "700", color: AGENTS[ev.agent]?.hex || "#f8fafc" }}>
                      {AGENTS[ev.agent]?.name || ev.agent?.toUpperCase()}
                    </span>
                    <span style={{ color: "#64748b", fontSize: "0.68rem" }}>
                      {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : ""}
                    </span>
                  </div>
                  <div style={{ color: "#cbd5e1", lineHeight: "1.35" }}>{ev.message}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
