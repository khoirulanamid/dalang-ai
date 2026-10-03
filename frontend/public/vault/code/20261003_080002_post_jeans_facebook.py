"""
Facebook Photo Post — Celana Jeans Korea (T-1803)
Posting bergambar ke profil Facebook personal Rizqi Mubarak
menggunakan foto celana_jeans_korea_1.jpg dan naskah T-1801.
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

COOKIES_PATH = Path.home() / ".fb_poster/cookies/session.json"
IMAGE_PATH = Path("/root/storage/projects/dalang-ai/workspace/product_images/celana_jeans_korea_1.jpg")
DEBUG_DIR = Path("/tmp/fb_jeans_debug")

# Naskah canonical T-1801 — digabung jadi satu post Facebook (bukan thread)
POST_TEXT = (
    "Sebagai cowok praktis, musuh terbesar pas nongkrong atau duduk seharian "
    "itu bukan kerjaan, tapi celana jeans yang bikin begah & sesak napas di "
    "perut bawah 🗿\n\n"
    "Ini celana model loose-fit / baggy gaya Korea tapi ada opsi pinggang "
    "karetnya. Duduk santai di warkop berjam-jam aman, ga perlu diam-diam "
    "lepas kancing celana lagi 👌\n\n"
    "Kurasi speknya:\n"
    "• Model: Loose-fit wide-leg gaya Korea (ga ngetat, ga bikin gerah)\n"
    "• Bahan: Denim lembut tahan bentuk (ga melar/ga molor)\n"
    "• Pinggang: Ada varian karet fleksibel & kancing biasa\n"
    "• Saku: 4 saku dalam aman buat hp/dompet\n\n"
    "Spill etalase produk di Shopee:\n"
    "https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq"
)


def _load_cookies() -> list[dict]:
    """Baca cookie Facebook dari file session dan format untuk Playwright."""
    if not COOKIES_PATH.exists():
        raise FileNotFoundError(f"Cookie tidak ditemukan: {COOKIES_PATH}")
    raw = json.loads(COOKIES_PATH.read_text())
    httponly_keys = {"xs", "datr", "sb", "fr", "c_user"}
    return [
        {
            "name": k,
            "value": str(v),
            "domain": ".facebook.com",
            "path": "/",
            "secure": True,
            "httpOnly": k in httponly_keys,
        }
        for k, v in raw.items()
    ]


def _dismiss_popups(page) -> None:
    """Tutup dialog/popup yang mungkin muncul sebelum compose box tersedia."""
    for sel in [
        'div[aria-label="Tutup"][role="button"]',
        'div[aria-label="Close"][role="button"]',
        '[data-testid="cookie-policy-manage-dialog-accept-button"]',
    ]:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            loc.first.click()
            time.sleep(1)
            logger.info("Popup ditutup: %s", sel)


def _find_compose_editor(page):
    """Cari editor compose box Facebook yang aktif."""
    candidates = [
        'div[role="textbox"][aria-label*="apa yang"]',
        'div[role="textbox"][aria-label*="Apa yang"]',
        'div[role="textbox"][aria-label*="What"]',
        'div[role="textbox"]',
        '[contenteditable="true"]',
    ]
    for sel in candidates:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            logger.info("Editor ditemukan: %s", sel)
            return loc.first
    return None


def _click_post_button(page) -> bool:
    """Klik tombol Posting/Post/Kirim dengan fallback bertingkat."""
    selectors = [
        'div[aria-label="Posting"][role="button"]',
        'div[aria-label="Post"][role="button"]',
        'div[aria-label="Kirim"][role="button"]',
        'div[role="button"]:has-text("Posting")',
        'div[role="button"]:has-text("Post")',
        'div[role="button"]:has-text("Kirim")',
    ]
    for sel in selectors:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.last.is_visible():
            if loc.last.get_attribute("aria-disabled") == "true":
                continue
            box = loc.last.bounding_box()
            if box:
                cx = box["x"] + box["width"] / 2
                cy = box["y"] + box["height"] / 2
                page.mouse.move(cx, cy)
                time.sleep(0.3)
                page.mouse.down()
                time.sleep(0.1)
                page.mouse.up()
            else:
                loc.last.click(force=True)
            logger.info("Tombol post diklik: %s", sel)
            return True
    return False


def run() -> bool:
    """Eksekusi posting foto celana jeans ke Facebook personal."""
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    if not IMAGE_PATH.exists():
        logger.error("File gambar tidak ditemukan: %s", IMAGE_PATH)
        return False

    cookies = _load_cookies()
    logger.info("Cookie dimuat: %d entri", len(cookies))

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        context.add_cookies(cookies)
        page = context.new_page()

        try:
            logger.info("Membuka Facebook...")
            page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=40000)
            time.sleep(3)
            page.screenshot(path=str(DEBUG_DIR / "01_fb_home.png"))

            _dismiss_popups(page)

            # Klik area "Apa yang Anda pikirkan?" untuk membuka compose modal
            logger.info("Mencari compose trigger...")
            compose_triggers = [
                'div[role="button"]:has-text("Apa yang Anda pikirkan")',
                'div[role="button"]:has-text("What\'s on your mind")',
                '[aria-label*="Apa yang Anda pikirkan"]',
                '[placeholder*="Apa yang Anda pikirkan"]',
                '[data-testid="status-attachment-mentions-input"]',
            ]
            trigger_clicked = False
            for sel in compose_triggers:
                loc = page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.click()
                    trigger_clicked = True
                    logger.info("Compose trigger diklik: %s", sel)
                    time.sleep(2)
                    break

            if not trigger_clicked:
                # Coba langsung buka URL compose foto
                logger.info("Trigger tidak ditemukan, coba URL compose foto...")
                page.goto(
                    "https://www.facebook.com/",
                    wait_until="domcontentloaded",
                    timeout=40000,
                )
                time.sleep(2)

            page.screenshot(path=str(DEBUG_DIR / "02_after_trigger.png"))

            # Cari tombol "Foto/Video" untuk membuka file picker
            logger.info("Mencari tombol Foto/Video...")
            photo_btn_selectors = [
                'div[role="button"]:has-text("Foto/video")',
                'div[role="button"]:has-text("Photo/video")',
                'div[role="button"]:has-text("Foto")',
                '[aria-label*="Foto"]',
                '[aria-label*="Photo"]',
            ]
            photo_btn_clicked = False
            for sel in photo_btn_selectors:
                loc = page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.click()
                    photo_btn_clicked = True
                    logger.info("Tombol foto diklik: %s", sel)
                    time.sleep(2)
                    break

            page.screenshot(path=str(DEBUG_DIR / "03_after_photo_btn.png"))

            # Upload gambar via file input
            logger.info("Mengupload gambar: %s", IMAGE_PATH)
            file_inputs = page.locator('input[type="file"]')
            if file_inputs.count() > 0:
                file_inputs.first.set_input_files(str(IMAGE_PATH))
                logger.info("Gambar berhasil di-set ke file input")
                time.sleep(5)
            else:
                logger.warning("File input tidak ditemukan, lanjut tanpa gambar")

            page.screenshot(path=str(DEBUG_DIR / "04_after_image_upload.png"))

            # Cari editor dan ketik naskah
            logger.info("Mencari editor compose...")
            editor = _find_compose_editor(page)
            if not editor:
                page.screenshot(path=str(DEBUG_DIR / "04b_no_editor.png"))
                logger.error("Editor tidak ditemukan")
                browser.close()
                return False

            editor.click()
            time.sleep(0.5)
            page.keyboard.insert_text(POST_TEXT)
            time.sleep(2)

            page.screenshot(path=str(DEBUG_DIR / "05_draft_ready.png"))
            logger.info("Naskah berhasil diketik")

            # Klik tombol Posting
            logger.info("Mengklik tombol Posting...")
            posted = _click_post_button(page)
            if not posted:
                page.screenshot(path=str(DEBUG_DIR / "05b_no_post_btn.png"))
                logger.error("Tombol Posting tidak ditemukan")
                browser.close()
                return False

            logger.info("Menunggu konfirmasi posting (15 detik)...")
            time.sleep(15)
            page.screenshot(path=str(DEBUG_DIR / "06_after_post.png"))

            # Verifikasi: buka profil dan ambil screenshot
            logger.info("Verifikasi profil Facebook...")
            page.goto(
                "https://www.facebook.com/profile.php?id=100083306003981",
                wait_until="domcontentloaded",
                timeout=40000,
            )
            time.sleep(5)
            screenshot_path = "/root/storage/projects/dalang-ai/workspace/fb_jeans_posted.png"
            page.screenshot(path=screenshot_path)
            logger.info("Screenshot profil tersimpan: %s", screenshot_path)

            browser.close()
            logger.info("POSTING FACEBOOK SELESAI — %s", datetime.now().isoformat())
            return True

        except Exception as exc:
            page.screenshot(path=str(DEBUG_DIR / "error_exception.png"))
            logger.exception("Exception saat posting: %s", exc)
            browser.close()
            return False


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
