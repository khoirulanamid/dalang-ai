"""
post_fb_dara.py
Publikasi Facebook: Dara One Set Blouse Kulot Rayon
Task T-2404 | Gathot Social Media Agent | Dalang-AI

Naskah: angle-01 (Sat-set OOTD) — Post 1 (hook relatable) + Post 2 (spec curation + CTA)
Foto: product_images/dara_oneset/dara_oneset_1.jpg (HD 268K)
Output screenshot: workspace/fb_dara_live.png & fb_dara_live.png
"""

import sys
import shutil
import logging
from pathlib import Path

# Add root / tools to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from tools.fb_poster import post_to_facebook

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Konfigurasi Path ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
IMAGE_PATH = BASE_DIR / "product_images/dara_oneset/dara_oneset_1.jpg"

# Main screenshot in cwd (workspace/fb_dara_live.png from project root)
LIVE_SCREENSHOT = BASE_DIR / "fb_dara_live.png"
# Secondary screenshot in workspace/fb_dara_live.png if subfolder exists
LIVE_SCREENSHOT_SUB = BASE_DIR / "workspace/fb_dara_live.png"

# ── Naskah Facebook (angle-01: Sat-set OOTD) ─────────────────────────────────
# Thread Split Format:
# Post 1 = Hook relatable (bingung milih baju)
# Post 2 = Spec curation + CTA affiliate
FACEBOOK_CAPTION = """Ada yang pernah ngitung berapa menit sehari yang habis cuma buat milih baju?

Kalau dijumlah seminggu, lumayan banyak. Dan ujung-ujungnya sering balik ke pilihan yang sama juga.

Konsep one set itu sebenarnya menjawab masalah ini: blouse dan kulot sudah didesain sebagai pasangan — warna, proporsi, dan gaya sudah match dari sananya. Tinggal ambil, pakai, pergi.

─────────────────────────────
Dara One Set Blouse Kulot Rayon — untuk yang hidupnya sat-set:

✅ Bahan Rayon Premium/Twill
Jatuh natural, adem, dan tahan aktivitas seharian — nggak perlu khawatir kusut di tengah hari

✅ Blouse Lengan Panjang Berkancing
Coverage lengkap, tetap stylish untuk berbagai kesempatan

✅ Kulot Full Karet Pinggang
Fleksibel untuk semua ukuran, nyaman dari pagi sampai malam

✅ Desain Serba Guna
Casual, hangout, kerja, atau formal ringan — satu set bisa handle semuanya

💰 Harga: Rp124.500 / set

👉 Order di Shopee: https://s.shopee.co.id/3qNaOVRWrP

#SatSetOOTD #OneSetWanita #FashionEfisien"""


def main():
    logger.info("=" * 60)
    logger.info("T-2404 | Publikasi Facebook: Dara One Set")
    logger.info("=" * 60)
    logger.info(f"Foto produk: {IMAGE_PATH}")
    logger.info(f"Screenshot target: {LIVE_SCREENSHOT}")

    if not IMAGE_PATH.exists():
        logger.error(f"File foto tidak ditemukan: {IMAGE_PATH}")
        sys.exit(1)

    logger.info("Memulai proses posting ke Facebook...")
    success = post_to_facebook(
        caption=FACEBOOK_CAPTION,
        image_path=IMAGE_PATH,
        screenshot_path=LIVE_SCREENSHOT,
        headless=True,
    )

    if success:
        # Copy also to workspace/fb_dara_live.png if needed
        LIVE_SCREENSHOT_SUB.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(LIVE_SCREENSHOT, LIVE_SCREENSHOT_SUB)
        logger.info(f"✅ Screenshot live disalin ke: {LIVE_SCREENSHOT_SUB}")
        logger.info("✅ SUKSES: Postingan Dara One Set berhasil dipublikasikan ke Facebook!")
        logger.info(f"📸 Screenshot live utama: {LIVE_SCREENSHOT}")
        sys.exit(0)
    else:
        logger.error("❌ GAGAL: Postingan tidak berhasil dipublikasikan.")
        sys.exit(1)


if __name__ == "__main__":
    main()
