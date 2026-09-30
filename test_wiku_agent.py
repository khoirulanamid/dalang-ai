"""
Test Suite — Wiku Agent (Wayang Pematung)
TDD: RED-GREEN-REFACTOR

Non-Commercial — CC BY-NC 4.0 — Dalang-AI by Khoirul Anam
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from wiku_agent import (
    WIKU_VERSION,
    OUTPUT_DIR,
    KNOWLEDGE_BASE,
    query_blender_knowledge,
    generate_build,
    _build_threejs_viewer,
    escape_html,
)


# ─── Knowledge Base ───────────────────────────────────────────────────────────

class TestKnowledgeBase:
    def test_knowledge_base_has_required_categories(self):
        required = {"primitives", "object_ops", "modifiers", "materials", "export", "scene_setup"}
        assert required.issubset(set(KNOWLEDGE_BASE.keys()))

    def test_query_cube_returns_primitives(self):
        result = query_blender_knowledge("cube primitive")
        assert result["found"] > 0
        assert "primitives" in result["results"]

    def test_query_material_returns_materials(self):
        result = query_blender_knowledge("material color shader")
        assert "materials" in result["results"]

    def test_query_export_returns_export(self):
        result = query_blender_knowledge("export glb gltf")
        assert "export" in result["results"]

    def test_query_returns_blender_version(self):
        result = query_blender_knowledge("test")
        assert "blender_version_target" in result
        assert "bpy" in result["blender_version_target"]

    def test_query_empty_returns_zero(self):
        result = query_blender_knowledge("xyznonexistent123")
        assert result["found"] == 0


# ─── Script Generation ────────────────────────────────────────────────────────

class TestScriptGeneration:
    def test_generate_build_creates_script_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="Test cube sederhana",
            object_name="TestCube",
            build_body="bpy.ops.mesh.primitive_cube_add(location=(0,0,0))\nobj = bpy.context.active_object\nobj.name = 'TestCube'",
        )
        assert Path(result["script"]).exists()

    def test_generate_build_creates_spec_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="Spec test",
            object_name="SpecObj",
            build_body="pass",
        )
        spec_path = Path(result["spec"])
        assert spec_path.exists()
        spec = json.loads(spec_path.read_text())
        assert spec["agent"] == "wiku"
        assert spec["version"] == WIKU_VERSION
        assert "AGENT_OK" in spec["contract"]
        assert "AGENT_FAIL" in spec["contract"]

    def test_generate_build_creates_viewer_html(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="Viewer test",
            object_name="ViewObj",
            build_body="pass",
        )
        viewer_path = Path(result["viewer"])
        assert viewer_path.exists()
        content = viewer_path.read_text()
        assert "three" in content.lower()
        assert "GLTFLoader" in content

    def test_script_contains_agent_ok_sentinel(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="Sentinel check",
            object_name="SentObj",
            build_body="pass",
        )
        script = Path(result["script"]).read_text()
        assert "AGENT_OK" in script

    def test_script_contains_agent_fail_sentinel(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="Sentinel fail check",
            object_name="FailObj",
            build_body="pass",
        )
        script = Path(result["script"]).read_text()
        assert "AGENT_FAIL" in script

    def test_script_contains_geometry_gate(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="Gate check",
            object_name="GateObj",
            build_body="pass",
        )
        script = Path(result["script"]).read_text()
        assert "geometry_gate" in script

    def test_script_contains_reset_scene(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="Reset check",
            object_name="ResetObj",
            build_body="pass",
        )
        script = Path(result["script"]).read_text()
        assert "bpy.ops.object.delete" in script

    def test_script_contains_glb_export(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="GLB export check",
            object_name="GLBObj",
            build_body="pass",
        )
        script = Path(result["script"]).read_text()
        assert "export_scene.gltf" in script

    def test_custom_objects_to_check(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="Multi-object build",
            object_name="Table",
            build_body="pass",
            objects_to_check=["Table", "Leg_1", "Leg_2"],
        )
        spec = json.loads(Path(result["spec"]).read_text())
        assert "Leg_1" in spec["objects_to_check"]
        assert "Leg_2" in spec["objects_to_check"]

    def test_build_id_format(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="ID format test",
            object_name="IDObj",
            build_body="pass",
        )
        assert result["build_id"].startswith("wiku_")

    def test_delivery_note_present(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wiku_agent.OUTPUT_DIR", tmp_path)
        result = generate_build(
            description="Delivery note test",
            object_name="NoteObj",
            build_body="pass",
        )
        assert result["delivery_note"]
        assert "Blender" in result["delivery_note"]


# ─── Three.js Viewer ─────────────────────────────────────────────────────────

class TestThreeJsViewer:
    def test_viewer_contains_orbit_controls(self):
        html = _build_threejs_viewer("test_id", "Test Object", "TestObj")
        assert "OrbitControls" in html

    def test_viewer_contains_gltf_loader(self):
        html = _build_threejs_viewer("test_id", "Test Object", "TestObj")
        assert "GLTFLoader" in html

    def test_viewer_contains_drag_drop(self):
        html = _build_threejs_viewer("test_id", "Test Object", "TestObj")
        assert "dragover" in html

    def test_viewer_contains_file_input(self):
        html = _build_threejs_viewer("test_id", "Test Object", "TestObj")
        assert "file-input" in html

    def test_viewer_dark_mode_bg(self):
        html = _build_threejs_viewer("test_id", "Test Object", "TestObj")
        assert "#08090a" in html

    def test_viewer_shows_build_id(self):
        html = _build_threejs_viewer("my_build_123", "Test Object", "TestObj")
        assert "my_build_123" in html

    def test_viewer_shows_wiku_badge(self):
        html = _build_threejs_viewer("test_id", "Test Object", "TestObj")
        assert "Wiku" in html


# ─── Escape HTML ─────────────────────────────────────────────────────────────

class TestEscapeHtml:
    def test_escapes_ampersand(self):
        assert "&amp;" in escape_html("a & b")

    def test_escapes_lt(self):
        assert "&lt;" in escape_html("<script>")

    def test_escapes_gt(self):
        assert "&gt;" in escape_html("a > b")

    def test_escapes_quote(self):
        assert "&quot;" in escape_html('say "hello"')

    def test_plain_text_unchanged(self):
        assert escape_html("Hello World 123") == "Hello World 123"


# ─── Router Integration ───────────────────────────────────────────────────────

class TestRouterIntegration:
    def test_wiku_in_roster(self):
        from wayang_router import WAYANG_ROSTER
        assert "wiku" in WAYANG_ROSTER

    def test_wiku_has_correct_title(self):
        from wayang_router import WAYANG_ROSTER
        assert WAYANG_ROSTER["wiku"]["title"] == "Wayang Pematung"

    def test_wiku_routed_for_3d(self):
        from wayang_router import auto_route_task
        agent, score = auto_route_task("Buat model 3D meja minimalis dalam format GLB")
        assert agent == "wiku"
        assert score > 0

    def test_wiku_routed_for_blender(self):
        from wayang_router import auto_route_task
        agent, score = auto_route_task("Buat bpy script untuk blender membuat kursi")
        assert agent == "wiku"

    def test_wiku_not_routed_for_api(self):
        from wayang_router import auto_route_task
        agent, _ = auto_route_task("Buat REST API endpoint login dengan FastAPI")
        assert agent != "wiku"

    def test_wiku_not_routed_for_database(self):
        from wayang_router import auto_route_task
        agent, _ = auto_route_task("Buat schema database PostgreSQL untuk user")
        assert agent != "wiku"
