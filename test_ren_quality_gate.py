"""
Test Suite: Ren Quality Gate — Mandatory QA sebelum masuk Gudang Bagong
"""

import tempfile
import os
import pytest
from ren_quality_gate import RenQualityGate

ren = RenQualityGate()


class TestHtmlFilmQA:

    def test_valid_html_film_passes(self, tmp_path):
        """Film HTML lengkap: DOCTYPE + canvas + script + AudioContext → PASSED."""
        f = tmp_path / "film.html"
        f.write_text("""<!DOCTYPE html>
<html><head></head><body>
<canvas id="stage" width="960" height="540"></canvas>
<script>
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  const canvas = document.getElementById('stage');
  const ctx = canvas.getContext('2d');
</script>
</body></html>""")
        v = ren.inspect_artifact(str(f), "html_film", "kresna")
        assert v.status == "PASSED"
        assert v.score >= 70.0

    def test_html_missing_canvas_rejected(self, tmp_path):
        """Film tanpa canvas → REJECTED."""
        f = tmp_path / "bad_film.html"
        f.write_text("""<!DOCTYPE html><html><body>
<script>console.log('test');</script>
</body></html>""")
        v = ren.inspect_artifact(str(f), "html_film", "kresna")
        assert v.status == "REJECTED"
        assert any("canvas" in i.lower() for i in v.issues)

    def test_html_missing_doctype_rejected(self, tmp_path):
        """Film tanpa DOCTYPE → skor berkurang, mungkin REJECTED."""
        f = tmp_path / "no_doctype.html"
        f.write_text("""<html><body>
<canvas id="stage"></canvas>
<script>
  const AudioCtx = window.AudioContext;
  const c = document.getElementById('stage');
</script>
</body></html>""")
        v = ren.inspect_artifact(str(f), "html_film", "kresna")
        assert any("DOCTYPE" in i for i in v.issues)

    def test_empty_file_rejected(self, tmp_path):
        """File kosong → REJECTED langsung."""
        f = tmp_path / "empty.html"
        f.write_text("")
        v = ren.inspect_artifact(str(f), "html_film", "kresna")
        assert v.status == "REJECTED"
        assert v.score == 0.0

    def test_nonexistent_file_rejected(self):
        """File tidak ada → REJECTED."""
        v = ren.inspect_artifact("/tmp/tidak_ada.html", "html_film", "kresna")
        assert v.status == "REJECTED"


class TestCodeQA:

    def test_valid_python_passed(self, tmp_path):
        """Python syntax valid → PASSED."""
        f = tmp_path / "modul.py"
        f.write_text("def hello():\n    return 'Halo Bos Muda'\n\nhello()\n")
        v = ren.inspect_artifact(str(f), "code", "zaki")
        assert v.status == "PASSED"

    def test_invalid_python_rejected(self, tmp_path):
        """Python syntax error → REJECTED."""
        f = tmp_path / "broken.py"
        f.write_text("def hello(\n    return 'broken'\n")
        v = ren.inspect_artifact(str(f), "code", "zaki")
        assert v.status == "REJECTED"
        assert any("syntax" in i.lower() for i in v.issues)

    def test_valid_json_passed(self, tmp_path):
        """JSON valid → PASSED."""
        f = tmp_path / "data.json"
        f.write_text('{"name": "Dalang-AI", "version": "2.0"}')
        v = ren.inspect_artifact(str(f), "code", "pingot")
        assert v.status == "PASSED"

    def test_invalid_json_rejected(self, tmp_path):
        """JSON korup → REJECTED."""
        f = tmp_path / "bad.json"
        f.write_text('{"name": "Dalang-AI", "version":}')
        v = ren.inspect_artifact(str(f), "code", "pingot")
        assert v.status == "REJECTED"


class TestVaultIntegration:

    def test_ren_blocks_bad_artifact_from_bagong(self, tmp_path):
        """Bagong DILARANG menerima file yang ditolak Ren."""
        from gudang_vault import VaultManager, QARejectionError
        vm = VaultManager()
        bad_file = tmp_path / "corrupt.html"
        bad_file.write_text("")  # File kosong

        with pytest.raises(QARejectionError) as exc_info:
            vm.deposit_artifact(
                source_path=str(bad_file),
                category="html_film",
                producer_agent="kresna",
                title="Film Cacat",
            )
        assert "REJECTED" in str(exc_info.value)

    def test_ren_approves_valid_artifact_for_bagong(self, tmp_path):
        """Bagong BOLEH menerima file yang lulus Ren."""
        from gudang_vault import VaultManager
        vm = VaultManager()
        good_file = tmp_path / "valid_film.html"
        good_file.write_text("""<!DOCTYPE html>
<html><body>
<canvas id="stage"></canvas>
<script>
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  const canvas = document.getElementById('stage');
</script>
</body></html>""")
        item = vm.deposit_artifact(
            source_path=str(good_file),
            category="html_film",
            producer_agent="kresna",
            title="Film Valid Lulus QA Ren",
        )
        assert item.id.startswith("VLT-")
        assert item.size_bytes > 0
