"""
Facebook Poster Module
Otomasi posting status ke profil Facebook personal via Playwright
Mendukung cookie session, penanganan dialog pop-up, pengetikan human-like, dan submit.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class FacebookPoster:
    def __init__(
        self,
        cookies_path: Optional[str] = None,
        headless: bool = True,
        timeout_ms: int = 30000,
    ):
        self.cookies_path = Path(cookies_path or Path.home() / ".fb_poster/cookies/session.json")
        self.headless = headless
        self.timeout_ms = timeout_ms

    def _load_cookies(self):
        if not self.cookies_path.exists():
            raise FileNotFoundError(f"Facebook cookie tidak ditemukan di {self.cookies_path}")
        raw = json.loads(self.cookies_path.read_text())
        cookies = []
        httponly = {"xs", "datr", "sb", "fr", "c_user"}
        for k, v in raw.items():
            cookies.append({
                "name": k,
                "value": str(v),
                "domain": ".facebook.com",
                "path": "/",
                "secure": True,
                "httpOnly": k in httponly,
            })
        return cookies

    def post_status(self, text: str) -> dict:
        """Membuat postingan status teks baru di Facebook."""
        cookies = self._load_cookies()

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                executable_path="/usr/bin/chromium",
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            context.add_cookies(cookies)
            page = context.new_page()

            try:
                logger.info("Membuka beranda Facebook...")
                page.goto("https://web.facebook.com/", wait_until="domcontentloaded", timeout=self.timeout_ms)
                time.sleep(5)

                # Tutup popup 'Ingat kata sandi' / dialog jika ada
                for dismiss_sel in [
                    '[aria-label="Tutup"]',
                    '[aria-label="Close"]',
                    'div[role="button"]:has-text("Nanti")',
                    'div[role="button"]:has-text("Batal")',
                ]:
                    try:
                        btn = page.locator(dismiss_sel)
                        if btn.count() > 0 and btn.first.is_visible():
                            btn.first.click()
                            time.sleep(1)
                    except Exception:
                        pass

                # Cari input status "Apa yang Anda pikirkan" / "What's on your mind"
                logger.info("Mencari area compose status...")
                compose_trigger = None
                for sel in [
                    'div[role="button"]:has-text("Apa yang Anda pikirkan")',
                    'div[role="button"]:has-text("What\'s on your mind")',
                    'span:has-text("Apa yang Anda pikirkan")',
                    'div[role="button"]:has-text("Buat postingan")',
                ]:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        compose_trigger = loc.first
                        break

                if not compose_trigger:
                    page.screenshot(path="/tmp/fb_debug/no_trigger.png")
                    return {"success": False, "error": "Kotak buat status tidak ditemukan di feed"}

                compose_trigger.click()
                time.sleep(3)

                # Tunggu editor modal terbuka
                editor = None
                for sel in [
                    'div[role="textbox"][contenteditable="true"]',
                    'div[contenteditable="true"]',
                ]:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.last.is_visible():
                        editor = loc.last
                        break

                if not editor:
                    page.screenshot(path="/tmp/fb_debug/no_editor.png")
                    return {"success": False, "error": "Editor modal Facebook tidak ditemukan"}

                # Ketik teks cepat via insert_text
                editor.click()
                time.sleep(0.5)
                page.keyboard.insert_text(text)
                time.sleep(2)

                time.sleep(3)
                page.screenshot(path="/tmp/fb_debug/fb_draft_ready.png")

                # Klik tombol "Kirim" / "Posting" / "Post"
                post_btn = None
                for sel in [
                    'div[aria-label="Posting"][role="button"]',
                    'div[aria-label="Post"][role="button"]',
                    'div[aria-label="Kirim"][role="button"]',
                    'div[role="button"]:has-text("Posting")',
                    'div[role="button"]:has-text("Kirim")',
                ]:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.last.is_visible():
                        # Pastikan tidak aria-disabled
                        if loc.last.get_attribute("aria-disabled") != "true":
                            post_btn = loc.last
                            break

                if not post_btn:
                    # Fallback koordinat
                    for sel in ['div[role="button"]:has-text("Posting")', 'div[role="button"]:has-text("Kirim")']:
                        loc = page.locator(sel)
                        if loc.count() > 0:
                            post_btn = loc.last
                            break

                if not post_btn:
                    page.screenshot(path="/tmp/fb_debug/no_post_btn.png")
                    return {"success": False, "error": "Tombol Posting/Kirim tidak ditemukan atau nonaktif"}

                box = post_btn.bounding_box()
                if box:
                    cx = box["x"] + box["width"] / 2
                    cy = box["y"] + box["height"] / 2
                    page.mouse.move(cx, cy)
                    time.sleep(0.3)
                    page.mouse.down()
                    time.sleep(0.1)
                    page.mouse.up()
                else:
                    post_btn.click(force=True)

                logger.info("Tombol Posting diklik, menunggu respons...")
                time.sleep(10)
                page.screenshot(path="/tmp/fb_debug/fb_after_post.png")

                browser.close()
                return {
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "text_preview": text[:60] + "..."
                }

            except Exception as e:
                page.screenshot(path="/tmp/fb_debug/fb_exception.png")
                browser.close()
                return {"success": False, "error": str(e)}
