"""
Wiku — Wayang Pematung
Subagent Dalang-AI khusus desain 3D Blender.

Mode: Opsi A (Script Generator)
- Wiku generate bpy Python script yang siap dijalankan di Blender lokal user.
- Setiap script wajib mencetak AGENT_OK atau AGENT_FAIL:<alasan> sebagai sentinel.
- Output disertai spec file JSON dan Three.js viewer HTML untuk preview hasil.
- Tidak ada render di server (Opsi B membutuhkan Blender headless terinstall).

AGENT CONTRACT:
  Setiap generated script WAJIB memiliki blok sentinel:
    try:
        ... <logika build> ...
        print("AGENT_OK")
    except Exception as e:
        print(f"AGENT_FAIL: {e}")

Non-Commercial — CC BY-NC 4.0 — Dalang-AI by Khoirul Anam
"""

from __future__ import annotations

import json
import os
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

# ─── Konstanta ───────────────────────────────────────────────────────────────

WIKU_VERSION = "1.0.0"
OUTPUT_DIR = Path(os.getenv("WIKU_OUTPUT_DIR", "/root/storage/projects/dalang-ai/wiku_outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

KNOWLEDGE_BASE: dict[str, dict[str, Any]] = {
    "primitives": {
        "cube": "bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0))",
        "sphere": "bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16)",
        "cylinder": "bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, vertices=32)",
        "plane": "bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,0))",
        "cone": "bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2)",
        "torus": "bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.25)",
        "empty": "bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))",
    },
    "object_ops": {
        "select_all": "bpy.ops.object.select_all(action='SELECT')",
        "delete_all": "bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()",
        "rename": "obj.name = 'NamaObjek'",
        "move": "obj.location = (x, y, z)",
        "scale": "obj.scale = (sx, sy, sz)",
        "rotate_z": "import math; obj.rotation_euler[2] = math.radians(90)",
    },
    "modifiers": {
        "bevel": "mod = obj.modifiers.new('Bevel', 'BEVEL'); mod.width = 0.05; mod.segments = 3",
        "subsurf": "mod = obj.modifiers.new('Subd', 'SUBSURF'); mod.levels = 2; mod.render_levels = 2",
        "solidify": "mod = obj.modifiers.new('Solid', 'SOLIDIFY'); mod.thickness = 0.01",
        "array": "mod = obj.modifiers.new('Array', 'ARRAY'); mod.count = 3; mod.relative_offset_displace[0] = 1.5",
        "mirror": "mod = obj.modifiers.new('Mirror', 'MIRROR'); mod.use_axis[0] = True",
        "boolean_union": "mod = obj.modifiers.new('Bool', 'BOOLEAN'); mod.operation = 'UNION'; mod.object = target_obj",
    },
    "materials": {
        "new_material": "mat = bpy.data.materials.new(name='Material'); mat.use_nodes = True",
        "assign": "if obj.data.materials: obj.data.materials[0] = mat\nelse: obj.data.materials.append(mat)",
        "set_color": "bsdf = mat.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Base Color'].default_value = (r, g, b, 1)",
        "metallic": "bsdf.inputs['Metallic'].default_value = 0.9",
        "roughness": "bsdf.inputs['Roughness'].default_value = 0.2",
    },
    "export": {
        "glb": "bpy.ops.export_scene.gltf(filepath='/path/output.glb', export_format='GLB', export_apply=True)",
        "stl": "bpy.ops.export_mesh.stl(filepath='/path/output.stl', use_selection=True)",
        "fbx": "bpy.ops.export_scene.fbx(filepath='/path/output.fbx', use_selection=True)",
        "obj": "bpy.ops.wm.obj_export(filepath='/path/output.obj')",
    },
    "scene_setup": {
        "unit_mm": "scene.unit_settings.system = 'METRIC'; scene.unit_settings.scale_length = 0.001",
        "clear_scene": (
            "bpy.ops.object.select_all(action='SELECT')\n"
            "bpy.ops.object.delete(use_global=False)\n"
            "for block in bpy.data.meshes: bpy.data.meshes.remove(block)"
        ),
        "world_bg": "bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[0].default_value = (0.02, 0.02, 0.02, 1)",
    },
}


# ─── Knowledge Query ─────────────────────────────────────────────────────────

def query_blender_knowledge(query: str) -> dict[str, Any]:
    """
    Wiku wajib memanggil ini sebelum generate script apapun.
    Mengembalikan snippet API bpy yang relevan berdasarkan query kata kunci.
    """
    query_lower = query.lower()
    results: dict[str, list[str]] = {}

    for category, entries in KNOWLEDGE_BASE.items():
        matched = []
        for key, snippet in entries.items():
            if any(word in key or word in snippet.lower() for word in query_lower.split()):
                matched.append(f"# [{key}]\n{snippet}")
        if matched:
            results[category] = matched

    return {
        "query": query,
        "blender_version_target": "4.x (bpy)",
        "results": results,
        "found": sum(len(v) for v in results.values()),
    }


# ─── Script Template ─────────────────────────────────────────────────────────

SCRIPT_HEADER = """\
\"\"\"
Wiku bpy Script — Generated by Dalang-AI
Build: {build_id}
Deskripsi: {description}
Dibuat: {timestamp}

CARA PAKAI DI BLENDER:
  1. Buka Blender → Scripting tab
  2. Paste seluruh script ini ke editor
  3. Klik Run Script (atau Alt+P)
  4. Cek Output Console: AGENT_OK = berhasil, AGENT_FAIL = ada error

Non-Commercial — CC BY-NC 4.0 — Dalang-AI by Khoirul Anam
\"\"\"

import bpy
import bmesh
import math
import os

# ─── Reset Scene ─────────────────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.meshes):
    bpy.data.meshes.remove(block)

"""

SCRIPT_FOOTER = """\

# ─── Geometry Gate ────────────────────────────────────────────────────────────
def geometry_gate(obj_name, min_verts=4):
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        print("AGENT_FAIL: Object '" + obj_name + "' tidak ditemukan setelah build.")
        return False
    if len(obj.data.vertices) < min_verts:
        print("AGENT_FAIL: Object '" + obj_name + "' hanya punya " + str(len(obj.data.vertices)) + " vertex (min: " + str(min_verts) + ").")
        return False
    return True

# ─── Export ───────────────────────────────────────────────────────────────────
try:
    _gate_pass = all([geometry_gate(n) for n in _objects_to_check])
    if not _gate_pass:
        raise RuntimeError("Geometry gate GAGAL — lihat pesan AGENT_FAIL di atas.")

    _out = os.path.join(os.path.expanduser("~"), "Desktop", "{build_id}.glb")
    bpy.ops.export_scene.gltf(
        filepath=_out,
        export_format='GLB',
        export_apply=True,
        export_materials='EXPORT',
    )
    print(f"AGENT_OK — GLB disimpan ke: {{_out}}")
except Exception as _e:
    print(f"AGENT_FAIL: {{_e}}")
"""


# ─── Generator Utama ─────────────────────────────────────────────────────────

def generate_build(
    description: str,
    object_name: str,
    build_body: str,
    objects_to_check: list[str] | None = None,
) -> dict[str, Any]:
    """
    Generate lengkap: bpy script + spec JSON + Three.js viewer HTML.

    Args:
        description: Deskripsi build yang diinginkan user.
        object_name: Nama objek utama dalam scene.
        build_body: Kode bpy Python inti (tanpa header/footer, tanpa try/except global).
        objects_to_check: List nama objek yang harus lolos Geometry Gate.

    Returns:
        Dict berisi path file yang di-generate.
    """
    # Knowledge-first: query dulu sebelum generate
    kb_result = query_blender_knowledge(description)

    build_id = f"wiku_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    timestamp = datetime.now().isoformat()
    check_list = objects_to_check or [object_name]

    # ── Script ──
    script_content = (
        SCRIPT_HEADER.format(
            build_id=build_id,
            description=description,
            timestamp=timestamp,
        )
        + textwrap.dedent(build_body).strip()
        + "\n\n"
        + f"_objects_to_check = {json.dumps(check_list)}\n"
        + SCRIPT_FOOTER.format(build_id=build_id)
    )

    script_path = OUTPUT_DIR / f"{build_id}.py"
    script_path.write_text(script_content, encoding="utf-8")

    # ── Spec JSON ──
    spec = {
        "build_id": build_id,
        "agent": "wiku",
        "version": WIKU_VERSION,
        "description": description,
        "object_name": object_name,
        "objects_to_check": check_list,
        "timestamp": timestamp,
        "knowledge_base_hits": kb_result["found"],
        "output_mode": "opsi_a_local_render",
        "files": {
            "script": str(script_path),
            "viewer": str(OUTPUT_DIR / f"{build_id}_viewer.html"),
            "spec": str(OUTPUT_DIR / f"{build_id}_spec.json"),
        },
        "contract": {
            "AGENT_OK": "Script selesai, GLB tersimpan di Desktop user.",
            "AGENT_FAIL": "Ada error — pesan detail ada di Blender console.",
        },
        "delivery_note": (
            "Jalankan .py di Blender Scripting tab. "
            "Buka _viewer.html di browser untuk preview Three.js interaktif."
        ),
    }

    spec_path = OUTPUT_DIR / f"{build_id}_spec.json"
    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── Three.js Viewer HTML ──
    viewer_html = _build_threejs_viewer(build_id, description, object_name)
    viewer_path = OUTPUT_DIR / f"{build_id}_viewer.html"
    viewer_path.write_text(viewer_html, encoding="utf-8")

    return {
        "build_id": build_id,
        "script": str(script_path),
        "spec": str(spec_path),
        "viewer": str(viewer_path),
        "knowledge_hits": kb_result["found"],
        "contract": spec["contract"],
        "delivery_note": spec["delivery_note"],
    }


# ─── Three.js Viewer ─────────────────────────────────────────────────────────

def _build_threejs_viewer(build_id: str, description: str, object_name: str) -> str:
    """Generate halaman HTML Three.js viewer interaktif untuk preview model GLB."""
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wiku 3D Viewer — {build_id}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #08090a; --surface: #0f1011; --surface2: #18191b;
    --border: #2a2b2d; --accent: #5e6ad2; --accent2: #7170ff;
    --text: #f7f8f8; --muted: #8b8d97; --ok: #26c97b; --fail: #e5484d;
    --font: 'Inter', system-ui, sans-serif;
  }}
  html, body {{ height: 100%; background: var(--bg); color: var(--text); font-family: var(--font); }}
  #app {{ display: flex; flex-direction: column; height: 100%; }}
  header {{
    padding: 14px 20px; border-bottom: 1px solid var(--border);
    background: var(--surface); display: flex; align-items: center; gap: 12px;
  }}
  .agent-badge {{
    background: var(--accent); color: #fff; font-size: 10px; font-weight: 700;
    letter-spacing: .06em; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;
  }}
  header h1 {{ font-size: 14px; font-weight: 600; letter-spacing: -.011em; }}
  header span {{ font-size: 12px; color: var(--muted); margin-left: auto; }}
  #canvas-wrap {{ flex: 1; position: relative; overflow: hidden; }}
  canvas {{ display: block; width: 100% !important; height: 100% !important; }}
  #overlay {{
    position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    background: var(--bg); flex-direction: column; gap: 16px; z-index: 10;
  }}
  .drop-zone {{
    border: 2px dashed var(--border); border-radius: 12px; padding: 48px 64px;
    text-align: center; cursor: pointer; transition: border-color .2s;
  }}
  .drop-zone:hover {{ border-color: var(--accent); }}
  .drop-zone h2 {{ font-size: 16px; font-weight: 600; margin-bottom: 8px; }}
  .drop-zone p {{ font-size: 13px; color: var(--muted); }}
  .btn {{
    background: var(--accent); color: #fff; border: none; border-radius: 6px;
    padding: 10px 20px; font-size: 13px; font-weight: 500; cursor: pointer;
    transition: background .15s;
  }}
  .btn:hover {{ background: var(--accent2); }}
  #info-bar {{
    padding: 10px 20px; border-top: 1px solid var(--border); background: var(--surface);
    font-size: 12px; color: var(--muted); display: flex; gap: 20px; align-items: center;
  }}
  .tag {{ background: var(--surface2); border-radius: 4px; padding: 2px 8px; color: var(--text); }}
  .ok {{ color: var(--ok); font-weight: 600; }}
  .hint {{ margin-left: auto; }}
  #file-input {{ display: none; }}
  #loading {{
    position: absolute; inset: 0; background: rgba(8,9,10,.85); display: none;
    align-items: center; justify-content: center; color: var(--muted); font-size: 14px; z-index: 20;
  }}
</style>
</head>
<body>
<div id="app">
  <header>
    <span class="agent-badge">Wiku</span>
    <h1>3D Viewer — {escape_html(description)}</h1>
    <span>{build_id}</span>
  </header>
  <div id="canvas-wrap">
    <div id="overlay">
      <div class="drop-zone" id="drop-zone">
        <h2>Drop file GLB di sini</h2>
        <p>Atau klik tombol di bawah untuk memilih file hasil render Blender</p>
      </div>
      <button class="btn" onclick="document.getElementById('file-input').click()">
        📂 Pilih File GLB
      </button>
      <input type="file" id="file-input" accept=".glb,.gltf">
    </div>
    <div id="loading">⏳ Memuat model…</div>
  </div>
  <div id="info-bar">
    <span>Build: <span class="tag">{build_id}</span></span>
    <span>Objek: <span class="tag">{escape_html(object_name)}</span></span>
    <span>Agent: <span class="tag ok">Wiku v{WIKU_VERSION}</span></span>
    <span class="hint">Scroll = zoom · Drag = orbit · Shift+Drag = pan</span>
  </div>
</div>

<script type="importmap">
{{
  "imports": {{
    "three": "https://cdn.jsdelivr.net/npm/three@0.168.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.168.0/examples/jsm/"
  }}
}}
</script>
<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';
import {{ RGBELoader }} from 'three/addons/loaders/RGBELoader.js';

const wrap = document.getElementById('canvas-wrap');
const overlay = document.getElementById('overlay');
const loading = document.getElementById('loading');

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x08090a);

// Lighting
const ambient = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambient);
const key = new THREE.DirectionalLight(0xffffff, 1.2);
key.position.set(5, 10, 7);
key.castShadow = true;
scene.add(key);
const fill = new THREE.DirectionalLight(0x4466ff, 0.3);
fill.position.set(-5, 3, -5);
scene.add(fill);
const rim = new THREE.DirectionalLight(0xffffff, 0.5);
rim.position.set(0, -5, -10);
scene.add(rim);

// Grid
const grid = new THREE.GridHelper(10, 20, 0x2a2b2d, 0x1a1b1d);
scene.add(grid);

// Camera
const camera = new THREE.PerspectiveCamera(45, wrap.clientWidth / wrap.clientHeight, 0.01, 1000);
camera.position.set(3, 2.5, 4);

// Renderer
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(wrap.clientWidth, wrap.clientHeight);
renderer.shadowMap.enabled = true;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
wrap.appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.target.set(0, 0.5, 0);
controls.update();

// Resize
window.addEventListener('resize', () => {{
  camera.aspect = wrap.clientWidth / wrap.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(wrap.clientWidth, wrap.clientHeight);
}});

// Load GLB
const loader = new GLTFLoader();
let currentModel = null;

function loadGLB(url) {{
  loading.style.display = 'flex';
  loader.load(url, (gltf) => {{
    if (currentModel) scene.remove(currentModel);
    currentModel = gltf.scene;
    currentModel.traverse(c => {{
      if (c.isMesh) {{ c.castShadow = true; c.receiveShadow = true; }}
    }});
    scene.add(currentModel);

    // Auto-center + fit camera
    const box = new THREE.Box3().setFromObject(currentModel);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    camera.position.set(center.x + maxDim * 1.5, center.y + maxDim, center.z + maxDim * 1.5);
    controls.target.copy(center);
    controls.update();

    overlay.style.display = 'none';
    loading.style.display = 'none';
  }}, undefined, (err) => {{
    loading.style.display = 'none';
    alert('Gagal load GLB: ' + err.message);
  }});
}}

// File input
document.getElementById('file-input').addEventListener('change', (e) => {{
  const file = e.target.files[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  loadGLB(url);
}});

// Drag-drop
const dropZone = document.getElementById('drop-zone');
dropZone.addEventListener('dragover', (e) => {{ e.preventDefault(); dropZone.style.borderColor = '#5e6ad2'; }});
dropZone.addEventListener('dragleave', () => {{ dropZone.style.borderColor = ''; }});
dropZone.addEventListener('drop', (e) => {{
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file && (file.name.endsWith('.glb') || file.name.endsWith('.gltf'))) {{
    loadGLB(URL.createObjectURL(file));
  }}
}});

// Animate
function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
animate();
</script>
</body>
</html>"""


def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ─── CLI sederhana ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print(f"Wiku Agent v{WIKU_VERSION} — Wayang Pematung Dalang-AI")
    print("=" * 60)

    # Demo build: meja kerja minimalis
    demo_body = """
# ── Meja Kerja Minimalis ──────────────────────────────────────
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001  # 1 BU = 1mm

def make_box(name, loc, dim):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dim[0]/2, dim[1]/2, dim[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    return obj

# Tabletop — 1200mm x 600mm x 25mm
tabletop = make_box('Tabletop', (0, 0, 0.7375), (1.200, 0.600, 0.025))

# 4 Kaki meja — 40mm x 40mm x 720mm
leg_positions = [
    ( 0.560,  0.260, 0.360),
    (-0.560,  0.260, 0.360),
    ( 0.560, -0.260, 0.360),
    (-0.560, -0.260, 0.360),
]
legs = []
for i, pos in enumerate(leg_positions):
    leg = make_box(f'Leg_{i+1}', pos, (0.040, 0.040, 0.720))
    legs.append(leg)

# Material kayu
mat = bpy.data.materials.new(name='Wood')
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.45, 0.28, 0.15, 1)
bsdf.inputs['Roughness'].default_value = 0.7
tabletop.data.materials.append(mat)
for leg in legs:
    leg.data.materials.append(mat)
"""

    result = generate_build(
        description="Meja kerja minimalis industrial 1200x600mm",
        object_name="Tabletop",
        build_body=demo_body,
        objects_to_check=["Tabletop", "Leg_1", "Leg_2", "Leg_3", "Leg_4"],
    )

    print(f"\n✅ Build selesai: {result['build_id']}")
    print(f"   Script  : {result['script']}")
    print(f"   Spec    : {result['spec']}")
    print(f"   Viewer  : {result['viewer']}")
    print(f"   KB Hits : {result['knowledge_hits']}")
    print(f"\n   {result['delivery_note']}")
