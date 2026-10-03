"""
Task T-2302:
Buka browser Playwright ke Facebook personal Rizqi Mubarak, input naskah kurasi celana jeans
dari docs/celana_jeans_campaign.json, lampirkan foto workspace/product_images/celana_jeans_korea_1.jpg,
submit posting, dan simpan screenshot live di workspace/fb_jeans_live.png
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COOKIES_PATH = Path.home() / ".fb_poster/cookies/session.json"
CAMPAIGN_JSON_PATH = Path("docs/celana_jeans_campaign.json")
IMAGE_PATH = Path("/root/storage/projects/dalang-ai/workspace/product_images/celana_jeans_korea_1.jpg")
if not IMAGE_PATH.exists():
    IMAGE_PATH = Path("product_images/celana_jeans_korea_1.jpg")

DEBUG_DIR = Path("/tmp/fb_t2302_debug")
DEBUG_DIR.mkdir(parents=True, exist_ok=True)


def load_cookies() -> list[dict]:
    if not COOKIES_PATH.exists():
        raise FileNotFoundError(f"Cookies not found at {COOKIES_PATH}")
    raw = json.loads(COOKIES_PATH.read_text())
    return [
        {
            "name": k,
            "value": str(v),
            "domain": ".facebook.com",
            "path": "/",
            "secure": True,
        }
        for k, v in raw.items()
    ]


def build_post_text() -> str:
    with open(CAMPAIGN_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    product_name = data.get("product_name", "Celana Jeans Pria Panjang Gaya Korea")
    specs = data.get("specs", [])
    affiliate_url = data.get("affiliate_url", "")

    specs_str = "\n".join(f"• {s}" for s in specs)

    # Naskah kurasi yang menarik dan natural untuk Facebook personal
    post_text = (
        f"Sebagai cowok praktis, musuh terbesar pas nongkrong atau duduk seharian "
        f"itu bukan kerjaan, tapi celana jeans yang bikin begah & sesak napas di perut bawah 🗿\n\n"
        f"Ini rekomendasi kurasi: {product_name}.\n"
        f"Model loose-fit / baggy gaya Korea tapi ada opsi pinggang karetnya. "
        f"Duduk santai di warkop berjam-jam aman, ga perlu diam-diam lepas kancing celana lagi 👌\n\n"
        f"Kurasi speknya:\n"
        f"{specs_str}\n\n"
        f"Spill etalase produk di Shopee:\n"
        f"{affiliate_url}"
    )
    return post_text


def run():
    post_text = build_post_text()
    logger.info("Post text prepared:\n%s", post_text)

    cookies = load_cookies()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-notifications",
                "--lang=id-ID",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="id-ID",
        )
        context.add_cookies(cookies)
        page = context.new_page()

        try:
            logger.info("Membuka profil Facebook personal Rizqi Mubarak...")
            page.goto(
                "https://www.facebook.com/profile.php?id=100083306003981",
                wait_until="domcontentloaded",
                timeout=45000,
            )
            time.sleep(5)
            page.screenshot(path=str(DEBUG_DIR / "01_profile.png"))

            # Cari tombol pembuka komposer postingan
            logger.info("Mencari komposer postingan...")
            composer_triggers = [
                'div[role="button"]:has-text("Apa yang Anda pikirkan")',
                'div[role="button"]:has-text("What\'s on your mind")',
                'span:has-text("Apa yang Anda pikirkan")',
                'span:has-text("What\'s on your mind")',
                'div[role="button"]:has-text("Foto/video")',
                'span:has-text("Foto/video")',
            ]

            clicked_composer = False
            for sel in composer_triggers:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=3000):
                        logger.info("Trigger komposer ditemukan: %s", sel)
                        el.click()
                        clicked_composer = True
                        break
                except Exception:
                    continue

            if not clicked_composer:
                # Coba buka feed home jika di profil tidak langsung tampak
                logger.info("Mencoba buka beranda facebook.com...")
                page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=45000)
                time.sleep(5)
                for sel in composer_triggers:
                    try:
                        el = page.locator(sel).first
                        if el.is_visible(timeout=3000):
                            logger.info("Trigger komposer di beranda ditemukan: %s", sel)
                            el.click()
                            clicked_composer = True
                            break
                    except Exception:
                        continue

            time.sleep(3)
            page.screenshot(path=str(DEBUG_DIR / "02_composer_opened.png"))

            # Upload gambar
            logger.info("Mengunggah foto: %s", IMAGE_PATH.resolve())
            file_input = page.locator('input[type="file"]')
            # Jika file_input belum ada di DOM dialog, klik icon Foto/video di dialog
            if file_input.count() == 0:
                logger.info("Input file belum muncul, mencoba klik tombol Foto/video di dialog...")
                photo_btn = page.locator('div[aria-label="Foto/video"], div[aria-label="Photo/video"]').first
                if photo_btn.is_visible(timeout=3000):
                    photo_btn.click()
                    time.sleep(2)

            file_inputs = page.locator('input[type="file"][accept*="image"]')
            if file_inputs.count() > 0:
                file_inputs.first.set_input_files(str(IMAGE_PATH.resolve()))
                logger.info("Foto berhasil diset ke file input")
            else:
                # fallback all file inputs
                all_inputs = page.locator('input[type="file"]')
                if all_inputs.count() > 0:
                    all_inputs.first.set_input_files(str(IMAGE_PATH.resolve()))
                    logger.info("Foto diset ke input[type=file]")
                else:
                    logger.warning("Tidak menemukan input[type=file]!")

            time.sleep(3)
            page.screenshot(path=str(DEBUG_DIR / "03_photo_attached.png"))

            # Input teks ke editor
            logger.info("Mencari area input teks...")
            editor = None
            editor_selectors = [
                'div[role="textbox"][contenteditable="true"]',
                'div[aria-label*="Apa yang Anda pikirkan"]',
                'div[aria-label*="What\'s on your mind"]',
                'div[aria-label*="Buat postingan"]',
                'div[aria-label*="Create a post"]',
            ]
            for sel in editor_selectors:
                try:
                    loc = page.locator(sel).first
                    if loc.is_visible(timeout=3000):
                        editor = loc
                        logger.info("Editor ditemukan dengan selector: %s", sel)
                        break
                except Exception:
                    continue

            if not editor:
                logger.error("Editor tidak ditemukan!")
                page.screenshot(path=str(DEBUG_DIR / "error_no_editor.png"))
                browser.close()
                return False

            editor.click()
            time.sleep(0.5)
            page.keyboard.insert_text(post_text)
            time.sleep(2)
            page.screenshot(path=str(DEBUG_DIR / "04_text_entered.png"))

            # Submit posting
            logger.info("Mencari tombol Kirim / Posting...")
            post_button_selectors = [
                'div[aria-label="Posting"][role="button"]',
                'div[aria-label="Post"][role="button"]',
                'div[aria-label="Kirim"][role="button"]',
                'button:has-text("Posting")',
                'button:has-text("Post")',
                'div[role="button"]:has-text("Posting")',
                'div[role="button"]:has-text("Post")',
            ]

            posted = False
            for sel in post_button_selectors:
                try:
                    candidates = page.locator(sel)
                    for i in range(candidates.count()):
                        btn = candidates.nth(i)
                        aria_disabled = btn.get_attribute("aria-disabled")
                        if btn.is_visible() and aria_disabled != "true":
                            logger.info("Tombol posting ditemukan: %s (nth %d)", sel, i)
                            btn.click()
                            posted = True
                            break
                    if posted:
                        break
                except Exception:
                    continue

            if not posted:
                logger.error("Gagal menemukan tombol posting aktif!")
                page.screenshot(path=str(DEBUG_DIR / "error_no_post_btn.png"))
                browser.close()
                return False

            logger.info("Menunggu posting selesai diproses (15 detik)...")
            time.sleep(15)
            page.screenshot(path=str(DEBUG_DIR / "05_after_click_post.png"))

            # Verifikasi di profil Facebook personal Rizqi Mubarak
            logger.info("Membuka profil untuk live screenshot...")
            page.goto(
                "https://www.facebook.com/profile.php?id=100083306003981",
                wait_until="domcontentloaded",
                timeout=45000,
            )
            time.sleep(6)

            # Scroll sedikit agar postingan terbaru terlihat jelas
            page.evaluate("window.scrollBy(0, 400)")
            time.sleep(2)

            # Simpan screenshot live di workspace/fb_jeans_live.png
            # Catatan: simpan di kedua kemungkinan lokasi agar pasti ditemukan
            out_path1 = Path("/root/storage/projects/dalang-ai/workspace/fb_jeans_live.png")
            out_path2 = Path("/root/storage/projects/dalang-ai/workspace/workspace/fb_jeans_live.png")
            out_path2.parent.mkdir(parents=True, exist_ok=True)

            page.screenshot(path=str(out_path1), full_page=False)
            page.screenshot(path=str(out_path2), full_page=False)
            logger.info("Screenshot tersimpan di %s dan %s", out_path1, out_path2)

            browser.close()
            logger.info("T-2302 SUCCESS!")
            return True

        except Exception as e:
            logger.exception("Terjadi kesalahan: %s", e)
            page.screenshot(path=str(DEBUG_DIR / "fatal_error.png"))
            browser.close()
            return False


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
