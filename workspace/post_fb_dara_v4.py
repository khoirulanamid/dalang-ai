"""
post_fb_dara_v4.py
Publikasi Facebook: Dara One Set Blouse Kulot Rayon
Task T-2404 | Gathot Social Media Agent | Dalang-AI

Fixed: Handle profile selection screen before accessing feed
Screenshot output: workspace/fb_dara_live.png
"""

import json
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COOKIES_PATH = Path.home() / ".fb_poster/cookies/session.json"
IMAGE_PATH = Path("/root/storage/projects/dalang-ai/workspace/product_images/dara_oneset/dara_oneset_1.jpg")
LIVE_SCREENSHOT = Path("/root/storage/projects/dalang-ai/workspace/fb_dara_live.png")

# ── Naskah Facebook ──────────────────────────────────────────────────────────
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
Dari warna netral hingga motif — bisa disesuaikan dengan preferensi dan acara.

✅ Potongan Kulot yang Flowy
Nyaman dipakai seharian, memberikan kesan anggun tanpa harus usaha ekstra.

✅ Harga Terjangkau
Kualitas bahan dan desain yang sepadan dengan harganya.

─────────────────────────────
Cek koleksi lengkap dan pilihan warna di sini:
👉 https://s.shopee.co.id/9pIBNMFHGM

#DaraOneSet #OOTD #FashionMuslim #BajuKantor #OneSet"""


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


def handle_profile_selection(page):
    """Handle the profile selection / cookie consent screen."""
    # Try clicking "Lanjutkan Rizqi Mubarak" or "Lanjutkan" with profile label
    for attempt in range(5):
        try:
            # Specific: Lanjutkan Rizqi Mubarak
            btn = page.locator('[aria-label="Lanjutkan Rizqi Mubarak"]').first
            if btn.is_visible(timeout=2000):
                logger.info("Klik 'Lanjutkan Rizqi Mubarak'...")
                btn.click()
                time.sleep(4)
                return True
        except Exception:
            pass
        
        try:
            # Generic Lanjutkan
            btn = page.locator('div[role="button"]:has-text("Lanjutkan")').first
            if btn.is_visible(timeout=2000):
                txt = btn.text_content() or ""
                logger.info(f"Klik Lanjutkan: {txt.strip()[:50]}")
                btn.click()
                time.sleep(4)
                # Check if we're now on the feed
                if "sk=h_chr" in page.url or page.locator('[aria-label="Beranda"]').count() > 0:
                    return True
        except Exception:
            pass
        
        time.sleep(1)
    
    return False


def wait_for_feed(page):
    """Wait until the feed/home page is loaded."""
    logger.info("Menunggu feed Facebook...")
    
    # Navigate directly to home feed
    page.goto("https://web.facebook.com/?sk=h_chr", wait_until="domcontentloaded", timeout=40000)
    time.sleep(5)
    
    # Handle any remaining consent dialogs
    for _ in range(3):
        try:
            btn = page.locator('[aria-label="Lanjutkan Rizqi Mubarak"]').first
            if btn.is_visible(timeout=2000):
                btn.click()
                time.sleep(4)
                page.goto("https://web.facebook.com/?sk=h_chr", wait_until="domcontentloaded", timeout=40000)
                time.sleep(5)
                break
        except Exception:
            break
    
    logger.info(f"URL feed: {page.url}")
    return page.url


def find_and_click_compose(page):
    """Find and click the compose/status box."""
    
    # Debug: list all buttons and aria-labels
    buttons = page.locator('div[role="button"]').all()
    logger.info(f"Buttons on page: {len(buttons)}")
    for i, btn in enumerate(buttons[:30]):
        try:
            txt = (btn.text_content() or "").strip()
            label = btn.get_attribute("aria-label") or ""
            if txt or label:
                logger.info(f"  [{i}] text={repr(txt[:50])} label={repr(label[:50])}")
        except Exception:
            pass
    
    # Try all compose selectors
    compose_selectors = [
        '[aria-label="Lanjutkan Rizqi Mubarak"]',  # profile button (shouldn't be here)
        'div[role="button"]:has-text("Apa yang Anda pikirkan")',
        'span:has-text("Apa yang Anda pikirkan")',
        '[aria-label="Buat postingan"]',
        '[aria-label="Buat Postingan"]',
        '[aria-label="Create post"]',
        '[aria-label="What\'s on your mind"]',
        'div[role="button"]:has-text("What\'s on your mind")',
        '[data-pagelet="FeedComposer"] div[role="button"]',
        'form div[role="button"]',
    ]
    
    for sel in compose_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                logger.info(f"✅ Compose found: {sel}")
                el.click()
                return True
        except Exception:
            pass
    
    # JS approach: find by text content
    result = page.evaluate("""
        () => {
            const keywords = ['pikirkan', 'mind', 'Buat post', 'Create post', 'status'];
            
            // Check all buttons
            const btns = document.querySelectorAll('div[role="button"], button, span[role="button"]');
            for (const btn of btns) {
                const text = (btn.textContent || '').trim();
                const label = btn.getAttribute('aria-label') || '';
                for (const kw of keywords) {
                    if (text.includes(kw) || label.includes(kw)) {
                        btn.click();
                        return 'clicked: ' + text.substring(0, 50) + ' | ' + label;
                    }
                }
            }
            
            // Check all spans
            const spans = document.querySelectorAll('span');
            for (const span of spans) {
                const text = (span.textContent || '').trim();
                for (const kw of keywords) {
                    if (text.includes(kw)) {
                        span.click();
                        return 'span: ' + text.substring(0, 50);
                    }
                }
            }
            
            return null;
        }
    """)
    
    if result:
        logger.info(f"JS compose click: {result}")
        return True
    
    return False


def main():
    logger.info("=" * 60)
    logger.info("T-2404 | Publikasi Facebook: Dara One Set Blouse Kulot Rayon")
    logger.info("=" * 60)

    if not IMAGE_PATH.exists():
        logger.error(f"Image not found: {IMAGE_PATH}")
        return

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

        # ── Step 1: Navigate & handle profile selection ────────────────────────
        logger.info("Navigasi ke web.facebook.com...")
        page.goto("https://web.facebook.com/", wait_until="domcontentloaded", timeout=40000)
        time.sleep(4)
        page.screenshot(path="fb_dara_v4_s1.png")
        logger.info(f"URL: {page.url}")

        # Handle profile selection screen
        handle_profile_selection(page)
        page.screenshot(path="fb_dara_v4_s2.png")
        logger.info(f"URL after profile select: {page.url}")

        # ── Step 2: Navigate to feed ───────────────────────────────────────────
        wait_for_feed(page)
        page.screenshot(path="fb_dara_v4_s3_feed.png")

        # ── Step 3: Find compose button ────────────────────────────────────────
        logger.info("Mencari compose button...")
        clicked = find_and_click_compose(page)

        if not clicked:
            logger.warning("Compose not found on feed, trying home page...")
            page.goto("https://web.facebook.com/", wait_until="domcontentloaded", timeout=35000)
            time.sleep(5)
            handle_profile_selection(page)
            time.sleep(3)
            page.screenshot(path="fb_dara_v4_s3b.png")
            clicked = find_and_click_compose(page)

        if not clicked:
            logger.error("❌ Compose button tidak ditemukan!")
            page.screenshot(path="fb_dara_v4_failed.png")
            # Save page HTML for analysis
            html = page.content()
            with open("fb_dara_v4_debug.html", "w") as f:
                f.write(html)
            logger.info("HTML saved to fb_dara_v4_debug.html")
            browser.close()
            return

        time.sleep(3)
        page.screenshot(path="fb_dara_v4_s4_compose.png")
        logger.info("Compose dialog terbuka")

        # ── Step 4: Type caption ───────────────────────────────────────────────
        logger.info("Mengetik caption...")
        text_selectors = [
            'div[role="dialog"] div[contenteditable="true"]',
            'div[contenteditable="true"][data-lexical-editor="true"]',
            'div[contenteditable="true"]',
            'div[role="textbox"]',
        ]

        typed = False
        for sel in text_selectors:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=4000):
                    el.click()
                    time.sleep(1)
                    el.type(FACEBOOK_CAPTION, delay=15)
                    logger.info(f"✅ Caption diketik via: {sel}")
                    typed = True
                    break
            except Exception as e:
                logger.debug(f"Selector {sel} failed: {e}")

        if not typed:
            logger.error("❌ Tidak bisa mengetik caption!")
            page.screenshot(path="fb_dara_v4_type_failed.png")
            browser.close()
            return

        time.sleep(2)
        page.screenshot(path="fb_dara_v4_s5_typed.png")

        # ── Step 5: Attach photo ───────────────────────────────────────────────
        logger.info("Melampirkan foto produk...")
        
        photo_clicked = False
        photo_selectors = [
            'div[role="dialog"] [aria-label*="Foto"]',
            'div[role="dialog"] [aria-label*="foto"]',
            'div[role="dialog"] [aria-label*="Photo"]',
            'div[role="dialog"] [aria-label*="photo"]',
            '[data-testid="photo-video-button"]',
            'div[role="dialog"] div[aria-label="Foto/video"]',
            'div[role="dialog"] div[aria-label="Photo/Video"]',
        ]

        for sel in photo_selectors:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=2000):
                    el.click()
                    logger.info(f"✅ Photo button: {sel}")
                    photo_clicked = True
                    time.sleep(2)
                    break
            except Exception:
                pass

        if not photo_clicked:
            # JS approach
            result = page.evaluate("""
                () => {
                    const dialog = document.querySelector('div[role="dialog"]') || document;
                    const els = dialog.querySelectorAll('[aria-label]');
                    for (const el of els) {
                        const label = (el.getAttribute('aria-label') || '').toLowerCase();
                        if (label.includes('foto') || label.includes('photo') || label.includes('gambar') || label.includes('image')) {
                            el.click();
                            return 'clicked: ' + label;
                        }
                    }
                    return null;
                }
            """)
            if result:
                logger.info(f"JS photo: {result}")
                photo_clicked = True
                time.sleep(2)

        # Handle file chooser
        try:
            with page.expect_file_chooser(timeout=8000) as fc_info:
                if not photo_clicked:
                    # Try clicking any button in dialog
                    page.locator('div[role="dialog"] div[role="button"]').nth(1).click()
                time.sleep(0.5)
            file_chooser = fc_info.value
            file_chooser.set_files(str(IMAGE_PATH))
            logger.info("✅ File dipilih via file chooser")
            time.sleep(5)
        except Exception as e:
            logger.warning(f"File chooser failed: {e}")
            try:
                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(str(IMAGE_PATH))
                logger.info("✅ File dipilih via direct input")
                time.sleep(5)
            except Exception as e2:
                logger.warning(f"Direct file input failed: {e2}")

        page.screenshot(path="fb_dara_v4_s6_photo.png")

        # ── Step 6: Submit post ────────────────────────────────────────────────
        logger.info("Mencari tombol Posting...")
        time.sleep(2)

        post_selectors = [
            'div[role="dialog"] div[aria-label="Posting"]',
            'div[role="dialog"] div[aria-label="Post"]',
            'div[role="dialog"] div[role="button"]:has-text("Posting")',
            'div[role="dialog"] div[role="button"]:has-text("Post")',
            'div[role="dialog"] button:has-text("Posting")',
            'div[role="dialog"] button:has-text("Post")',
        ]

        posted = False
        for sel in post_selectors:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=3000):
                    el.click()
                    logger.info(f"✅ Post button: {sel}")
                    posted = True
                    break
            except Exception:
                pass

        if not posted:
            result = page.evaluate("""
                () => {
                    const dialog = document.querySelector('div[role="dialog"]') || document;
                    const btns = dialog.querySelectorAll('div[role="button"], button');
                    for (const btn of btns) {
                        const text = (btn.textContent || '').trim();
                        const label = btn.getAttribute('aria-label') || '';
                        if (text === 'Posting' || text === 'Post' || label === 'Posting' || label === 'Post') {
                            btn.click();
                            return 'clicked: ' + text + ' | ' + label;
                        }
                    }
                    return null;
                }
            """)
            if result:
                logger.info(f"JS post: {result}")
                posted = True

        if not posted:
            logger.warning("⚠️ Post button tidak ditemukan, mencoba Enter...")
            page.keyboard.press("Control+Enter")

        logger.info("Menunggu posting selesai (15 detik)...")
        time.sleep(15)

        # ── Step 7: Screenshot live feed ──────────────────────────────────────
        logger.info("Navigasi ke profil untuk screenshot live...")
        page.goto("https://web.facebook.com/profile.php", wait_until="domcontentloaded", timeout=35000)
        time.sleep(6)

        LIVE_SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(LIVE_SCREENSHOT))
        logger.info(f"✅ Screenshot tersimpan di: {LIVE_SCREENSHOT}")

        browser.close()

    logger.info("=" * 60)
    logger.info("✅ SELESAI: T-2404 Publikasi Facebook Dara One Set")
    logger.info(f"📸 Screenshot live: {LIVE_SCREENSHOT}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
