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
    httponly = {"sb", "datr", "c_user", "xs", "fr"}
    return [
        {
            "name": k,
            "value": str(v),
            "domain": ".facebook.com",
            "path": "/",
            "secure": True,
            "httpOnly": k in httponly
        }
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
    logger.info("Membuka browser Playwright untuk Facebook...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 850},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        logger.info("Navigasi ke web.facebook.com...")
        page.goto("https://web.facebook.com/", wait_until="domcontentloaded", timeout=40000)
        time.sleep(5)

        # Tutup modal pengganggu
        for dismiss_sel in ['[aria-label="Tutup"]', '[aria-label="Close"]', 'div[role="button"]:has-text("Nanti")']:
            try:
                btn = page.locator(dismiss_sel)
                if btn.count() > 0 and btn.first.is_visible():
                    btn.first.click()
                    time.sleep(1)
            except Exception:
                pass

        # Klik kotak buat status
        logger.info("Mencari tombol compose status...")
        compose = page.locator('div[role="button"]:has-text("Apa yang Anda pikirkan"), span:has-text("Apa yang Anda pikirkan")').first
        compose.click()
        time.sleep(3)

        # 1. Ketik naskah terlebih dahulu
        logger.info("Mengetik naskah caption...")
        editor = page.locator('div[role="textbox"][contenteditable="true"]').last
        editor.click()
        time.sleep(1)
        page.keyboard.insert_text(text)
        time.sleep(2)
        logger.info("Naskah berhasil diketik.")

        # 2. Lampirkan Foto Produk
        logger.info("Melampirkan foto celana jeans...")
        # Klik ikon foto/video di modal
        photo_icon = page.locator('div[aria-label*="Foto/video"], div[aria-label*="Photo/video"]').last
        if photo_icon.is_visible():
            photo_icon.click()
            time.sleep(2)

        file_input = page.locator('input[type="file"][accept*="image"]').last
        file_input.set_input_files(str(IMAGE_PATH))
        time.sleep(4)
        logger.info("Foto celana jeans berhasil dilampirkan.")

        # 3. Klik Kirim / Posting
        logger.info("Mencari tombol Kirim/Posting...")
        post_btn = None
        for sel in [
            'div[aria-label="Posting"][role="button"]',
            'div[aria-label="Post"][role="button"]',
            'div[aria-label="Kirim"][role="button"]',
            'div[role="button"]:has-text("Posting")',
            'div[role="button"]:has-text("Kirim")'
        ]:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.last.is_visible():
                if loc.last.get_attribute("aria-disabled") != "true":
                    post_btn = loc.last
                    break

        if post_btn:
            logger.info("Mengklik tombol Posting...")
            post_btn.click()
            time.sleep(12)
        else:
            logger.warning("Tombol posting tidak terdeteksi via selector baku.")

        # 4. Ambil screenshot feed verifikasi
        logger.info("Navigasi ke halaman profil untuk ambil screenshot...")
        page.goto("https://web.facebook.com/profile.php", wait_until="networkidle", timeout=35000)
        time.sleep(6)
        page.screenshot(path=str(LIVE_SCREENSHOT))
        logger.info(f"Screenshot tersimpan di: {LIVE_SCREENSHOT}")
        browser.close()

if __name__ == "__main__":
    main()
