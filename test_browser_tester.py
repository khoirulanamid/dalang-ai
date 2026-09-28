"""
Test Suite untuk Browser Automation & Headless App Verification Engine
"""

import pytest
import tempfile
from pathlib import Path
from browser_tester import BrowserTester


class TestBrowserTester:
    def test_inspect_clean_html_dom(self):
        clean_html = """<!DOCTYPE html>
        <html>
          <head><title>Dalang-AI</title></head>
          <body>
            <div id="root"></div>
            <canvas id="three-canvas"></canvas>
          </body>
        </html>"""
        res = BrowserTester.inspect_html_dom(clean_html, required_selectors=["#root", "canvas"])
        assert res["valid"] is True
        assert "#root" in res["found_elements"]
        assert "canvas" in res["found_elements"]
        assert len(res["issues"]) == 0

    def test_inspect_xss_hazard_dom(self):
        malicious_html = """<div><img src="x" onerror="alert('xss')" /></div>"""
        res = BrowserTester.inspect_html_dom(malicious_html)
        assert res["valid"] is False
        assert any("SECURITY HAZARD" in issue for issue in res["issues"])

    def test_verify_real_vite_build_bundle(self):
        dist_path = "/root/storage/projects/dalang-ai/frontend/dist"
        res = BrowserTester.verify_vite_build_bundle(dist_path)
        assert res["ready"] is True
        assert res["index_html_present"] is True
        assert res["root_mount_present"] is True
        assert res["js_bundle_present"] is True

    def test_generate_playwright_smoke_script(self):
        script = BrowserTester.generate_playwright_smoke_script("http://127.0.0.1:5173")
        assert "async_playwright" in script
        assert "http://127.0.0.1:5173" in script
        assert "#root" in script
