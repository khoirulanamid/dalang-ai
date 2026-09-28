"""
Browser Automation & Headless App Verification Engine — Dalang-AI
Terinspirasi dari skills/browser-automation di zhaoxuya520/reverse-skill

Digunakan oleh Ren (Wayang Jaksa — QA Lead) dan Lulu (Frontend Architect) untuk:
1. Inspeksi struktur DOM dan sanitasi XSS pada template HTML
2. Verifikasi kesiapan bundle frontend Vite & WebGL Canvas target
3. Skrip otomasi smoke test browser headless (Playwright / Puppeteer contract)
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class BrowserTester:
    """
    Mesin validasi dan otomasi browser headless untuk frontend dan DOM security.
    """

    @staticmethod
    def inspect_html_dom(
        html_content: str,
        required_selectors: Optional[List[str]] = None,
        forbidden_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Memeriksa integritas DOM statis dan resistansi terhadap script unescaped/XSS injection.
        """
        issues = []
        found_elements = []

        # Periksa selektor yang diwajibkan (misal #root, canvas, meta viewport)
        if required_selectors:
            for sel in required_selectors:
                if sel.startswith("#"):
                    # id check
                    elem_id = sel[1:]
                    if f'id="{elem_id}"' in html_content or f"id='{elem_id}'" in html_content:
                        found_elements.append(sel)
                    else:
                        issues.append(f"MISSING: Element dengan ID '{sel}' tidak ditemukan di HTML.")
                elif sel.startswith("."):
                    # class check
                    elem_cls = sel[1:]
                    if elem_cls in html_content:
                        found_elements.append(sel)
                    else:
                        issues.append(f"MISSING: Element dengan class '{sel}' tidak ditemukan di HTML.")
                else:
                    # tag check
                    if f"<{sel}" in html_content:
                        found_elements.append(sel)
                    else:
                        issues.append(f"MISSING: Tag HTML '<{sel}>' tidak ditemukan.")

        # Periksa pola terlarang (XSS atau bad inline script)
        default_forbidden = [
            r"<script[^>]*>\s*alert\(",
            r"onerror\s*=\s*['\"]?[^'\">]+",
            r"javascript:\s*void",
        ]
        active_forbidden = (forbidden_patterns or []) + default_forbidden
        for pattern in active_forbidden:
            if re.search(pattern, html_content, re.IGNORECASE):
                issues.append(f"SECURITY HAZARD: Ditemukan pola script berbahaya/XSS: {pattern}")

        return {
            "valid": len(issues) == 0,
            "found_elements": found_elements,
            "issues": issues,
        }

    @staticmethod
    def verify_vite_build_bundle(dist_dir: str) -> Dict[str, Any]:
        """
        Memverifikasi bahwa output build Vite/React valid dan siap disajikan.
        """
        p = Path(dist_dir).resolve()
        index_html = p / "index.html"
        assets_dir = p / "assets"

        if not index_html.exists():
            return {"ready": False, "error": "dist/index.html tidak ditemukan."}

        content = index_html.read_text(encoding="utf-8")
        has_root = 'id="root"' in content or "id='root'" in content
        has_js_bundle = any(assets_dir.glob("*.js")) if assets_dir.exists() else False
        has_css_bundle = any(assets_dir.glob("*.css")) if assets_dir.exists() else False

        return {
            "ready": has_root and has_js_bundle,
            "index_html_present": True,
            "root_mount_present": has_root,
            "js_bundle_present": has_js_bundle,
            "css_bundle_present": has_css_bundle,
            "size_bytes": len(content),
        }

    @staticmethod
    def generate_playwright_smoke_script(target_url: str = "http://localhost:5173") -> str:
        """
        Membuat template skrip Playwright headless E2E smoke test untuk Ren.
        """
        return f"""# Headless E2E Smoke Test Contract — Ren (Dalang-AI QA)
import asyncio
from playwright.async_api import async_playwright

async def run_smoke_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        response = await page.goto("{target_url}", timeout=15000)
        assert response.status == 200, f"Expected 200, got {{response.status}}"
        
        # Verify root mount and Canvas existence
        await page.wait_for_selector("#root", timeout=5000)
        canvas = await page.query_selector("canvas")
        assert canvas is not None, "WebGL Canvas not mounted"
        print("✅ Smoke Test Succeeded: Frontend and WebGL Canvas active.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
"""
