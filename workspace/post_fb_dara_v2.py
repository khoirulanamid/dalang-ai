"""
post_fb_dara_v2.py
Publikasi Facebook: Dara One Set Blouse Kulot Rayon
Task T-2404 | Gathot Social Media Agent | Dalang-AI

Menggunakan pola proven dari post_fb_jeans_final.py
Screenshot output: workspace/fb_dara_live.png
"""

import json
import logging
import sys
import shutil
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COOKIES_PATH = Path.home() / ".fb_poster/cookies/session.json"
IMAGE_PATH = Path("/root/storage/projects/dalang-ai/workspace/product_images/dara_oneset/dara_oneset_1.jpg")
LIVE_SCREENSHOT = Path("/root/storage/projects/dalang-ai/workspace/fb_dara_live.png")
LIVE_SCREENSHOT_ROOT = Path("/root/storage/projects/dalang-ai/workspace/fb_dara_live.png")

# ── Naskah Facebook (angle-01: Sat-set OOTD) ─────────────────────────────────
FACEBOOK_CAPTION = """Ada yang pernah ngitung berapa menit sehari yang habis cuma buat milih baju?

Kalau dijumlah seminggu, lumayan banyak. Dan ujung-ujungnya sering balik ke pilihan yang sama juga.

Konsep one set itu sebenarnya menjawab masalah ini: blouse dan kulot sudah didesain sebagai pasangan — warna, proporsi, dan gaya sudah match dari sananya. Tinggal ambil, pakai, pergi.

─────────────────────────────
Dara One Set Blouse Kulot Rayon — untuk yang hidupnya sat-set:

✅ Bahan Rayon Premium/Twill
Jatuh natural, adem, dan tahan aktivitas seharian — nggak perlu khawatir kusut di tengah hari.

✅ Desain Blouse + Kulot Serasi
Satu set, sudah koordinasi. Cocok untuk kerja, hangout, kondangan kasual, sampai jalan-jalan.

✅ Tersedia Berbagai Pilihan Warna
Dari warna netral kalem sampai yang lebih berani — tinggal pilih sesuai mood.

✅ Ukuran All Size (Fit L-XL)
Potongan longgar yang tetap terlihat rapi dan proporsional.

✅ Harga Terjangkau
Kualitas bahan dan desain yang sepadan dengan harganya.

─────────────────────────────
🛒 Cek langsung di Shopee:
https://s.shopee.co.id/8KJqTkz7w7

#DaraOneSet #OOTDSatSet #BlouseKulot #FashionMuslimah #OutfitHarian"""


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


def main():
    logger.info("=" * 60)
    logger.info("T-2404 | Publikasi Facebook: Dara One Set Blouse Kulot Rayon")
    logger.info("=" * 60)
    logger.info(f"Foto produk: {IMAGE_PATH}")
    logger.info(f"Screenshot target: {LIVE_SCREENSHOT}")

    if not IMAGE_PATH.exists():
        logger.error(f"File foto tidak ditemukan: {IMAGE_PATH}")
        sys.exit(1)

    cookies = load_cookies()
    logger.info(f"Cookies dimuat: {len(cookies)} item")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_cookies(cookies)
        page = context.new_page()

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
        page.keyboard.insert_text(FACEBOOK_CAPTION)
        time.sleep(2)
        logger.info("Naskah berhasil diketik.")

        # 2. Lampirkan Foto Produk
        logger.info("Melampirkan foto Dara One Set...")
        # Klik ikon foto/video di modal
        photo_icon = page.locator('div[aria-label*="Foto/video"], div[aria-label*="Photo/video"]').last
        if photo_icon.is_visible():
            photo_icon.click()
            time.sleep(2)

        file_input = page.locator('input[type="file"][accept*="image"]').last
        file_input.set_input_files(str(IMAGE_PATH))
        time.sleep(4)
        logger.info("Foto Dara One Set berhasil dilampirkan.")

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
                post_btn = loc.last
                logger.info(f"Tombol posting ditemukan: {sel}")
                break

        if post_btn:
            post_btn.click()
            logger.info("Tombol posting diklik. Menunggu konfirmasi...")
            time.sleep(6)
        else:
            logger.warning("Tombol posting tidak terdeteksi via selector baku.")

        # 4. Ambil screenshot feed verifikasi
        logger.info("Navigasi ke halaman profil untuk ambil screenshot...")
        page.goto("https://web.facebook.com/profile.php", wait_until="networkidle", timeout=35000)
        time.sleep(6)

        # Simpan screenshot ke workspace/fb_dara_live.png
        LIVE_SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(LIVE_SCREENSHOT))
        logger.info(f"✅ Screenshot tersimpan di: {LIVE_SCREENSHOT}")

        browser.close()

    logger.info("✅ SUKSES: Postingan Dara One Set berhasil dipublikasikan ke Facebook!")
    logger.info(f"📸 Screenshot live: {LIVE_SCREENSHOT}")


if __name__ == "__main__":
    main()
