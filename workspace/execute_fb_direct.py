import json
import logging
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COOKIES_PATH = Path.home() / ".fb_poster/cookies/session.json"
CAMPAIGN_JSON_PATH = Path("/root/storage/projects/dalang-ai/workspace/docs/celana_jeans_campaign.json")
IMAGE_PATH = Path("/root/storage/projects/dalang-ai/workspace/product_images/celana_jeans_korea_1.jpg")
LIVE_SCREENSHOT = Path("/root/storage/projects/dalang-ai/workspace/fb_jeans_live.png")

def load_cookies():
    raw = json.loads(COOKIES_PATH.read_text())
    return [
        {"name": k, "value": str(v), "domain": ".facebook.com", "path": "/", "secure": True}
        for k, v in raw.items()
    ]

def get_text():
    with open(CAMPAIGN_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    product_name = data.get("product_name", "Celana Jeans Pria Panjang Gaya Korea")
    specs = data.get("specs", [])
    affiliate_url = data.get("affiliate_url", "https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq")

    specs_str = "\n".join(f"• {s}" for s in specs)

    post_text = (
        f"Sebagai cowok praktis, musuh terbesar pas nongkrong atau duduk seharian "
        f"itu bukan kerjaan, tapi celana jeans yang bikin begah & sesak napas di perut bawah 🫄\n\n"
        f"Ini rekomendasi celana santai: {product_name}.\n"
        f"Model loose-fit / baggy gaya Korea tapi ada opsi pinggang karetnya. "
        f"Duduk santai di warkop berjam-jam aman, ga perlu diam-diam lepas kancing celana lagi 😭\n\n"
        f"Spesifikasi & Keunggulan:\n"
        f"{specs_str}\n\n"
        f"🧵 Detail & Checkout:\n"
        f"🔗 {affiliate_url}\n\n"
        f"#FashionPria #CelanaJeansPria #KoreanStyle #OOTDCowok #ShopeeAffiliate"
    )
    return post_text

def main():
    text = get_text()
    cookies = load_cookies()
    logger.info("Memulai eksekusi posting Facebook...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-notifications"]
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        logger.info("Navigasi ke Facebook...")
        page.goto("https://www.facebook.com/", wait_until="networkidle", timeout=45000)
        time.sleep(3)

        # Trigger dialog buat postingan
        logger.info("Membuka form postingan...")
        selectors = [
            "span:has-text('Apa yang Anda pikirkan')",
            "span:has-text('What\\'s on your mind')",
            "div[role='button']:has-text('Apa yang Anda pikirkan')",
            "div[role='button']:has-text('What\\'s on your mind')",
        ]
        opened = False
        for sel in selectors:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=3000):
                    el.click()
                    opened = True
                    logger.info(f"Trigger sukses dengan: {sel}")
                    break
            except Exception:
                pass

        time.sleep(3)

        # 1. Lampirkan Foto
        logger.info("Mencari input file foto...")
        file_input = page.locator("input[type='file'][accept*='image']").first
        if not file_input.is_visible():
            try:
                photo_btn = page.locator("div[aria-label*='Foto/video'], div[aria-label*='Photo/video']").first
                if photo_btn.is_visible(timeout=2000):
                    photo_btn.click()
                    time.sleep(2)
            except Exception:
                pass
            file_input = page.locator("input[type='file']").first

        file_input.set_input_files(str(IMAGE_PATH))
        logger.info("Foto celana jeans diset.")
        time.sleep(4)

        # 2. Input Naskah Teks ke Editor
        logger.info("Mengetik naskah caption...")
        editor_selectors = [
            "div[role='dialog'] div[role='textbox'][contenteditable='true']",
            "div[role='dialog'] div[aria-label*='Apa yang Anda pikirkan']",
            "div[role='dialog'] div[aria-label*='What\\'s on your mind']",
            "div[role='textbox'][contenteditable='true']"
        ]
        editor = None
        for es in editor_selectors:
            try:
                ed = page.locator(es).first
                if ed.is_visible(timeout=2000):
                    editor = ed
                    logger.info(f"Editor ditemukan: {es}")
                    break
            except Exception:
                pass

        if editor:
            try:
                editor.click(force=True, timeout=5000)
            except Exception:
                editor.focus()
            time.sleep(1)
            page.keyboard.insert_text(text)
            logger.info("Naskah berhasil dimasukkan.")
            time.sleep(2)
        else:
            logger.warning("Editor dialog belum fokus, mencoba klik area dialog...")

        # 3. Klik Tombol Kirim
        logger.info("Mencari tombol Kirim...")
        submit_selectors = [
            "div[role='dialog'] div[aria-label='Kirim'][role='button']",
            "div[role='dialog'] div[aria-label='Post'][role='button']",
            "div[role='dialog'] div[role='button']:has-text('Kirim')",
            "div[role='dialog'] div[role='button']:has-text('Post')",
        ]
        submitted = False
        for ss in submit_selectors:
            try:
                btn = page.locator(ss).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    submitted = True
                    logger.info(f"Tombol kirim diklik: {ss}")
                    break
            except Exception:
                pass

        time.sleep(12)

        # 4. Ambil screenshot live verifikasi
        logger.info("Mengambil screenshot live feed...")
        page.goto("https://www.facebook.com/profile.php", wait_until="networkidle", timeout=35000)
        time.sleep(5)
        page.screenshot(path=str(LIVE_SCREENSHOT))
        logger.info(f"Screenshot live tersimpan di: {LIVE_SCREENSHOT}")
        browser.close()

if __name__ == "__main__":
    main()
