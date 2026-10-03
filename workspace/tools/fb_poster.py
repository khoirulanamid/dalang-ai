"""
tools/fb_poster.py
Reusable Facebook Personal Profile Poster via Playwright
Dalang-AI | Gathot Social Media Agent
"""

import json
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COOKIES_PATH = Path.home() / ".fb_poster/cookies/session.json"


def load_cookies():
    raw = json.loads(COOKIES_PATH.read_text())
    return [
        {"name": k, "value": str(v), "domain": ".facebook.com", "path": "/", "secure": True}
        for k, v in raw.items()
    ]


def post_to_facebook(
    caption: str,
    image_path: str | Path | None = None,
    screenshot_path: str | Path = "fb_live.png",
    headless: bool = True,
) -> bool:
    """
    Post a status update (with optional image) to Facebook personal profile.

    Args:
        caption: The full text caption to post.
        image_path: Optional path to image file to attach.
        screenshot_path: Where to save the live verification screenshot.
        headless: Run browser headless (default True).

    Returns:
        True if post succeeded, False otherwise.
    """
    cookies = load_cookies()
    screenshot_path = Path(screenshot_path)
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-notifications"],
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        try:
            # ── Step 1: Navigate to Facebook home ──────────────────────────────
            logger.info("Navigasi ke Facebook home...")
            page.goto("https://www.facebook.com/", wait_until="networkidle", timeout=40000)
            time.sleep(3)

            # ── Step 2: Open "What's on your mind?" composer ───────────────────
            logger.info("Membuka form postingan...")
            composer_selectors = [
                "span:has-text('Apa yang Anda pikirkan')",
                "span:has-text('What\\'s on your mind')",
                "div[role='button']:has-text('Apa yang Anda pikirkan')",
                "div[role='button']:has-text('What\\'s on your mind')",
            ]
            opened = False
            for sel in composer_selectors:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=4000):
                        el.click()
                        time.sleep(2)
                        opened = True
                        logger.info(f"Composer dibuka via: {sel}")
                        break
                except Exception:
                    continue

            if not opened:
                logger.warning("Composer tidak ditemukan via selector standar, mencoba fallback...")
                page.screenshot(path="fb_composer_debug.png")
                # Fallback: click on the text area directly
                try:
                    page.locator("div[role='textbox']").first.click(timeout=5000)
                    opened = True
                except Exception:
                    logger.error("Gagal membuka composer Facebook.")
                    browser.close()
                    return False

            time.sleep(2)

            # ── Step 3: Attach image (if provided) ────────────────────────────
            if image_path:
                image_path = Path(image_path)
                logger.info(f"Melampirkan foto: {image_path.name}")

                # Try to click Photo/Video button first
                photo_btn_selectors = [
                    "div[aria-label*='Foto/video']",
                    "div[aria-label*='Photo/video']",
                    "div[aria-label*='Photo']",
                    "span:has-text('Foto/video')",
                    "span:has-text('Photo/video')",
                ]
                for pb_sel in photo_btn_selectors:
                    try:
                        pb = page.locator(pb_sel).first
                        if pb.is_visible(timeout=3000):
                            pb.click()
                            time.sleep(2)
                            logger.info(f"Tombol foto diklik via: {pb_sel}")
                            break
                    except Exception:
                        continue

                # Set file input
                file_input = page.locator("input[type='file']").first
                file_input.set_input_files(str(image_path))
                logger.info("File foto berhasil diset.")
                time.sleep(5)

            # ── Step 4: Type caption ───────────────────────────────────────────
            logger.info("Mengetik caption...")
            editor_selectors = [
                "div[role='dialog'] div[role='textbox'][contenteditable='true']",
                "div[role='dialog'] div[aria-label*='Apa yang Anda pikirkan']",
                "div[role='dialog'] div[aria-label*='What\\'s on your mind']",
                "div[role='textbox'][contenteditable='true']",
            ]
            editor = None
            for es in editor_selectors:
                try:
                    ed = page.locator(es).first
                    if ed.is_visible(timeout=4000):
                        editor = ed
                        logger.info(f"Editor ditemukan via: {es}")
                        break
                except Exception:
                    continue

            if editor is None:
                logger.error("Editor teks tidak ditemukan.")
                page.screenshot(path="fb_editor_debug.png")
                browser.close()
                return False

            editor.click()
            time.sleep(1)
            editor.fill(caption)
            time.sleep(2)
            logger.info("Caption berhasil diketik.")

            # ── Step 5: Submit post ────────────────────────────────────────────
            logger.info("Mengirim postingan...")
            post_btn_selectors = [
                "div[aria-label='Posting']",
                "div[aria-label='Post']",
                "button[aria-label='Posting']",
                "button[aria-label='Post']",
                "div[role='button']:has-text('Posting')",
                "div[role='button']:has-text('Post')",
            ]
            posted = False
            for ps in post_btn_selectors:
                try:
                    btn = page.locator(ps).first
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        posted = True
                        logger.info(f"Tombol post diklik via: {ps}")
                        break
                except Exception:
                    continue

            if not posted:
                logger.error("Tombol Posting tidak ditemukan.")
                page.screenshot(path="fb_post_btn_debug.png")
                browser.close()
                return False

            # ── Step 6: Wait for post to publish ──────────────────────────────
            logger.info("Menunggu postingan terbit...")
            time.sleep(12)

            # ── Step 7: Screenshot live profile ───────────────────────────────
            logger.info("Mengambil screenshot live feed...")
            page.goto("https://www.facebook.com/profile.php", wait_until="networkidle", timeout=35000)
            time.sleep(5)
            page.screenshot(path=str(screenshot_path))
            logger.info(f"✅ Screenshot live tersimpan: {screenshot_path}")

            browser.close()
            return True

        except Exception as e:
            logger.error(f"Error saat posting: {e}")
            try:
                page.screenshot(path="fb_error_debug.png")
            except Exception:
                pass
            browser.close()
            return False


if __name__ == "__main__":
    # Quick test / standalone usage
    import sys
    caption = sys.argv[1] if len(sys.argv) > 1 else "Test post dari Gathot tools/fb_poster.py"
    image = sys.argv[2] if len(sys.argv) > 2 else None
    screenshot = sys.argv[3] if len(sys.argv) > 3 else "fb_test_live.png"
    result = post_to_facebook(caption, image, screenshot)
    print("SUCCESS" if result else "FAILED")
