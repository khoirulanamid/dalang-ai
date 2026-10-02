"""
Instagram Feed Poster via Playwright
- Login via session cookie
- Buka modal Create (+)
- Upload gambar
- Isi caption
- Submit post
"""
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class InstagramPoster:
    def __init__(
        self,
        cookies_path: Optional[str] = None,
        headless: bool = True,
        timeout_ms: int = 30000,
    ):
        self.cookies_path = Path(cookies_path or Path.home() / ".ig_poster/cookies/session.json")
        self.headless = headless
        self.timeout_ms = timeout_ms

    def _load_cookies(self):
        if not self.cookies_path.exists():
            raise FileNotFoundError(f"Cookie Instagram tidak ditemukan: {self.cookies_path}")
        raw = json.loads(self.cookies_path.read_text())
        httponly = {"sessionid", "mid", "rur", "ig_did", "datr", "ds_user_id"}
        cookies = []
        for k, v in raw.items():
            cookies.append({
                "name": k, "value": str(v),
                "domain": ".instagram.com", "path": "/",
                "secure": True, "httpOnly": k in httponly,
            })
        return cookies

    def post_feed(self, image_path: str, caption: str) -> dict:
        """Upload foto ke feed Instagram dengan caption."""
        image_path = Path(image_path)
        if not image_path.exists():
            return {"success": False, "error": f"Gambar tidak ditemukan: {image_path}"}

        cookies = self._load_cookies()

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                executable_path="/usr/bin/chromium",
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            context.add_cookies(cookies)
            page = context.new_page()

            debug_dir = Path("/tmp/ig_debug")
            debug_dir.mkdir(exist_ok=True)

            try:
                logger.info("Membuka Instagram...")
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=self.timeout_ms)
                time.sleep(5)

                # Dismiss semua popup yang muncul (loop sampai bersih)
                for attempt in range(5):
                    dismissed = False
                    for sel in [
                        'button:has-text("Not Now")',
                        'button:has-text("Nanti")',
                        'div[role="button"]:has-text("Not Now")',
                        'div[role="button"]:has-text("Nanti")',
                        '[aria-label="Close"]',
                        '[aria-label="Tutup"]',
                    ]:
                        try:
                            btn = page.locator(sel)
                            if btn.count() > 0 and btn.first.is_visible():
                                btn.first.click()
                                time.sleep(1.5)
                                dismissed = True
                                logger.info(f"Popup dismissed [{attempt+1}] via: {sel}")
                                break
                        except Exception:
                            pass
                    if not dismissed:
                        break
                    time.sleep(1)

                page.screenshot(path=str(debug_dir / "ig_01_home.png"))

                # Klik tombol Create (+) di sidebar
                logger.info("Klik tombol Create...")
                create_clicked = False
                for sel in [
                    'svg[aria-label="New post"]',
                    '[aria-label="New post"]',
                    'span:has-text("Create")',
                    'div[role="button"]:has-text("Create")',
                ]:
                    try:
                        loc = page.locator(sel)
                        if loc.count() > 0:
                            el = loc.first
                            el.click(force=True)
                            create_clicked = True
                            logger.info(f"Create diklik via: {sel}")
                            break
                    except Exception:
                        pass

                if not create_clicked:
                    # Fallback koordinat pasti tombol New post di sidebar
                    logger.info("Fallback: mouse click pada koordinat ikon New post (36, 480)...")
                    page.mouse.click(36, 480)
                    create_clicked = True

                if not create_clicked:
                    page.screenshot(path=str(debug_dir / "ig_fail_create.png"))
                    browser.close()
                    return {"success": False, "error": "Tombol Create tidak ditemukan"}

                time.sleep(3)
                page.screenshot(path=str(debug_dir / "ig_02_after_create.png"))

                # Dismiss popup yang mungkin muncul lagi setelah klik Create
                for attempt in range(3):
                    dismissed = False
                    for sel in [
                        'button:has-text("Not Now")',
                        'button:has-text("Nanti")',
                        'div[role="button"]:has-text("Not Now")',
                        'div[role="button"]:has-text("Nanti")',
                        '[aria-label="Close"]',
                    ]:
                        try:
                            btn = page.locator(sel)
                            if btn.count() > 0 and btn.first.is_visible():
                                btn.first.click()
                                time.sleep(1.5)
                                dismissed = True
                                logger.info(f"Popup post-create dismissed via: {sel}")
                                break
                        except Exception:
                            pass
                    if not dismissed:
                        break

                # Klik Create sekali lagi jika modal upload belum muncul
                if page.locator('input[type="file"]').count() == 0:
                    logger.info("Modal belum muncul, re-klik tombol Create (36, 480)...")
                    page.mouse.click(36, 480)
                    time.sleep(3)

                # Tunggu dialog upload muncul: cari input file atau tombol "Select from computer"
                logger.info("Menunggu dialog upload...")
                file_input = None

                # Intercept file input yang muncul
                for _ in range(10):
                    inputs = page.locator('input[type="file"]')
                    if inputs.count() > 0:
                        file_input = inputs.first
                        break

                    # Coba klik "Select from computer" jika ada
                    for sel in [
                        'button:has-text("Select from computer")',
                        'button:has-text("Pilih dari komputer")',
                        'div[role="button"]:has-text("Select from computer")',
                        'div[role="button"]:has-text("Pilih dari komputer")',
                    ]:
                        loc = page.locator(sel)
                        if loc.count() > 0 and loc.first.is_visible():
                            loc.first.click()
                            time.sleep(1)
                            break

                    time.sleep(1.5)

                if not file_input:
                    page.screenshot(path=str(debug_dir / "ig_fail_upload.png"))
                    browser.close()
                    return {"success": False, "error": "Input file upload tidak ditemukan"}

                # Upload gambar
                logger.info(f"Upload gambar: {image_path}")
                file_input.set_input_files(str(image_path))
                time.sleep(5)
                page.screenshot(path=str(debug_dir / "ig_03_image_uploaded.png"))

                # Dismiss popup notifikasi yang muncul setelah upload
                for sel in [
                    'button:has-text("Not Now")',
                    'button:has-text("Nanti")',
                    'div[role="button"]:has-text("Not Now")',
                    'div[role="button"]:has-text("Nanti")',
                    '[aria-label="Close"]',
                ]:
                    try:
                        btn = page.locator(sel)
                        if btn.count() > 0 and btn.first.is_visible():
                            btn.first.click()
                            logger.info(f"Popup dismissed via: {sel}")
                            time.sleep(1)
                            break
                    except Exception:
                        pass

                # Klik Next / Lanjutkan TIGA kali (Crop → Edit/Filter → Caption)
                logger.info("Navigasi step: Crop -> Edit -> Caption...")
                for step in range(3):
                    for wait_t in range(8):
                        next_clicked = False
                        for sel in [
                            'div[role="button"]:has-text("Next")',
                            'div[role="button"]:has-text("Lanjutkan")',
                            'button:has-text("Next")',
                            'button:has-text("Lanjutkan")',
                        ]:
                            try:
                                loc = page.locator(sel)
                                if loc.count() > 0 and loc.last.is_visible():
                                    loc.last.click(force=True)
                                    next_clicked = True
                                    logger.info(f"  Step {step+1}: klik Next via {sel}")
                                    time.sleep(3)
                                    break
                            except Exception:
                                pass
                        if next_clicked:
                            break
                        time.sleep(1)
                    page.screenshot(path=str(debug_dir / f"ig_0{4+step}_step_{step+1}.png"))

                # Isi caption
                logger.info("Mengisi caption...")
                caption_box = None
                for sel in [
                    'div[aria-label="Write a caption..."][contenteditable="true"]',
                    'div[aria-label="Tulis caption..."][contenteditable="true"]',
                    'textarea[aria-label="Write a caption..."]',
                    'div[contenteditable="true"][role="textbox"]',
                    'div[contenteditable="true"]',
                ]:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.last.is_visible():
                        caption_box = loc.last
                        break

                if not caption_box:
                    page.screenshot(path=str(debug_dir / "ig_fail_caption.png"))
                    browser.close()
                    return {"success": False, "error": "Caption box tidak ditemukan"}

                caption_box.click()
                time.sleep(0.5)
                page.keyboard.type(caption, delay=15)
                time.sleep(2)
                page.screenshot(path=str(debug_dir / "ig_07_caption_filled.png"))

                # Dismiss tooltip atau popover tag jika ada sebelum share
                page.keyboard.press("Escape")
                time.sleep(1)

                # Submit / Share / Bagikan
                logger.info("Klik Share / Bagikan...")
                share_btn = None
                # Tombol Share ada di header modal kanan atas — pakai .first bukan .last
                for sel in [
                    'div[role="button"]:has-text("Share")',
                    'div[role="button"]:has-text("Bagikan")',
                    'button:has-text("Share")',
                    'button:has-text("Bagikan")',
                ]:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        if loc.first.get_attribute("aria-disabled") != "true":
                            share_btn = loc.first
                            break

                if not share_btn:
                    page.screenshot(path=str(debug_dir / "ig_fail_share.png"))
                    browser.close()
                    return {"success": False, "error": "Tombol Share/Bagikan tidak ditemukan"}

                # Klik via mouse coordinate (lebih reliable untuk React event)
                box = share_btn.bounding_box()
                if box:
                    cx = box["x"] + box["width"] / 2
                    cy = box["y"] + box["height"] / 2
                    page.mouse.move(cx, cy)
                    time.sleep(0.3)
                    page.mouse.down()
                    time.sleep(0.1)
                    page.mouse.up()
                    logger.info(f"Share diklik di koordinat ({cx:.0f}, {cy:.0f})")
                else:
                    # Fallback koordinat tetap: tombol Share di header modal kanan atas
                    logger.info("Fallback koordinat Share (1064, 109)...")
                    page.mouse.move(1064, 109)
                    time.sleep(0.3)
                    page.mouse.down()
                    time.sleep(0.1)
                    page.mouse.up()

                logger.info("Menunggu konfirmasi posting (maks 30 detik)...")
                posted = False
                for _ in range(30):
                    time.sleep(1)
                    if page.locator(':has-text("Post shared"), :has-text("Your post has been shared")').count() > 0:
                        posted = True
                        logger.info("✅ Konfirmasi 'Post shared' diterima!")
                        break
                page.screenshot(path=str(debug_dir / "ig_08_after_share.png"))

                browser.close()
                return {
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "caption_preview": caption[:60] + "...",
                    "image": str(image_path),
                }

            except Exception as e:
                page.screenshot(path=str(debug_dir / "ig_exception.png"))
                browser.close()
                return {"success": False, "error": str(e)}
