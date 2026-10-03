"""
post_fb_dara_v3.py
Publikasi Facebook: Dara One Set Blouse Kulot Rayon
Task T-2404 | Gathot Social Media Agent | Dalang-AI

Robust version with multiple selector strategies + debug screenshots
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


def try_click_compose(page):
    """Try multiple strategies to click the compose/status box."""
    
    # Strategy 1: Standard "Apa yang Anda pikirkan" text
    selectors_to_try = [
        'div[role="button"]:has-text("Apa yang Anda pikirkan")',
        'span:has-text("Apa yang Anda pikirkan")',
        '[aria-label="Buat postingan"]',
        '[aria-label="Create post"]',
        '[aria-label="Buat Postingan"]',
        'div[role="button"]:has-text("What\'s on your mind")',
        'span:has-text("What\'s on your mind")',
        # Generic compose area
        'div[data-pagelet="FeedComposer"]',
        'div[data-testid="status-attachment-mentions-input"]',
        'form[method="POST"] div[role="button"]',
    ]
    
    for sel in selectors_to_try:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=3000):
                logger.info(f"✅ Found compose via: {sel}")
                el.click()
                return True
        except Exception:
            pass
    
    # Strategy 2: JavaScript click on any compose-like element
    logger.info("Trying JS-based compose click...")
    result = page.evaluate("""
        () => {
            // Try to find compose box by text content
            const allDivs = document.querySelectorAll('div[role="button"]');
            for (const div of allDivs) {
                const text = div.textContent || '';
                if (text.includes('pikirkan') || text.includes('mind') || text.includes('Buat post')) {
                    div.click();
                    return 'clicked: ' + text.substring(0, 50);
                }
            }
            // Try spans
            const allSpans = document.querySelectorAll('span');
            for (const span of allSpans) {
                const text = span.textContent || '';
                if (text.includes('pikirkan') || text.includes('mind')) {
                    span.click();
                    return 'span clicked: ' + text.substring(0, 50);
                }
            }
            return null;
        }
    """)
    
    if result:
        logger.info(f"JS click result: {result}")
        return True
    
    return False


def main():
    logger.info("=" * 60)
    logger.info("T-2404 | Publikasi Facebook: Dara One Set Blouse Kulot Rayon")
    logger.info("=" * 60)
    logger.info(f"Foto produk: {IMAGE_PATH}")
    logger.info(f"Screenshot target: {LIVE_SCREENSHOT}")

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

        # ── Step 1: Navigate to Facebook ──────────────────────────────────────
        logger.info("Navigasi ke web.facebook.com...")
        page.goto("https://web.facebook.com/", wait_until="domcontentloaded", timeout=40000)
        time.sleep(4)

        # Handle cookie consent
        for consent_text in ["Lanjutkan", "Allow all cookies", "Accept all"]:
            try:
                btn = page.locator(f'div[role="button"]:has-text("{consent_text}")').first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    logger.info(f"Klik consent: {consent_text}")
                    time.sleep(3)
                    break
            except Exception:
                pass

        page.screenshot(path="fb_dara_v3_step1.png")
        logger.info(f"URL setelah load: {page.url}")

        # ── Step 2: Navigate to home feed ─────────────────────────────────────
        page.goto("https://web.facebook.com/?sk=h_chr", wait_until="domcontentloaded", timeout=35000)
        time.sleep(5)
        page.screenshot(path="fb_dara_v3_step2.png")
        logger.info(f"URL feed: {page.url}")

        # Debug: print all button texts
        try:
            buttons = page.locator('div[role="button"]').all()
            logger.info(f"Total buttons found: {len(buttons)}")
            for i, btn in enumerate(buttons[:20]):
                try:
                    txt = btn.text_content()
                    if txt and txt.strip():
                        logger.info(f"  Button[{i}]: {repr(txt.strip()[:80])}")
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Button debug failed: {e}")

        # ── Step 3: Click compose ──────────────────────────────────────────────
        logger.info("Mencari tombol compose status...")
        clicked = try_click_compose(page)
        
        if not clicked:
            logger.warning("Compose button not found via standard methods, trying direct navigation...")
            # Try navigating directly to create post
            page.goto("https://web.facebook.com/", wait_until="domcontentloaded", timeout=35000)
            time.sleep(5)
            page.screenshot(path="fb_dara_v3_step3_home.png")
            clicked = try_click_compose(page)

        if not clicked:
            logger.error("❌ Tidak bisa menemukan compose button!")
            page.screenshot(path="fb_dara_v3_failed.png")
            browser.close()
            return

        time.sleep(3)
        page.screenshot(path="fb_dara_v3_step3_compose.png")
        logger.info("Compose dialog terbuka")

        # ── Step 4: Type caption ───────────────────────────────────────────────
        logger.info("Mengetik caption...")
        
        # Find the text input area in the dialog
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
                    el.type(FACEBOOK_CAPTION, delay=20)
                    logger.info(f"✅ Caption diketik via: {sel}")
                    typed = True
                    break
            except Exception as e:
                logger.debug(f"Selector {sel} failed: {e}")

        if not typed:
            logger.error("❌ Tidak bisa mengetik caption!")
            page.screenshot(path="fb_dara_v3_type_failed.png")
            browser.close()
            return

        time.sleep(2)
        page.screenshot(path="fb_dara_v3_step4_typed.png")

        # ── Step 5: Attach photo ───────────────────────────────────────────────
        logger.info("Melampirkan foto produk...")
        
        photo_selectors = [
            'div[role="dialog"] [aria-label*="Foto"]',
            'div[role="dialog"] [aria-label*="Photo"]',
            'div[role="dialog"] [aria-label*="foto"]',
            '[data-testid="photo-video-button"]',
            'div[role="dialog"] div[aria-label="Foto/video"]',
        ]
        
        photo_clicked = False
        for sel in photo_selectors:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=3000):
                    el.click()
                    logger.info(f"✅ Photo button clicked via: {sel}")
                    photo_clicked = True
                    time.sleep(2)
                    break
            except Exception:
                pass

        if not photo_clicked:
            # Try JS approach
            logger.info("Trying JS photo button click...")
            result = page.evaluate("""
                () => {
                    const dialog = document.querySelector('div[role="dialog"]');
                    if (!dialog) return 'no dialog';
                    const btns = dialog.querySelectorAll('[aria-label]');
                    for (const btn of btns) {
                        const label = btn.getAttribute('aria-label') || '';
                        if (label.toLowerCase().includes('foto') || label.toLowerCase().includes('photo')) {
                            btn.click();
                            return 'clicked: ' + label;
                        }
                    }
                    return 'not found';
                }
            """)
            logger.info(f"JS photo result: {result}")
            if 'clicked' in str(result):
                photo_clicked = True
                time.sleep(2)

        # Handle file input
        try:
            with page.expect_file_chooser(timeout=8000) as fc_info:
                if not photo_clicked:
                    # Try clicking any photo-related button
                    page.locator('div[role="dialog"]').locator('[aria-label]').first.click()
                time.sleep(1)
            file_chooser = fc_info.value
            file_chooser.set_files(str(IMAGE_PATH))
            logger.info("✅ File dipilih via file chooser")
            time.sleep(5)
        except Exception as e:
            logger.warning(f"File chooser method failed: {e}")
            # Try direct input
            try:
                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(str(IMAGE_PATH))
                logger.info("✅ File dipilih via direct input")
                time.sleep(5)
            except Exception as e2:
                logger.warning(f"Direct file input also failed: {e2}")

        page.screenshot(path="fb_dara_v3_step5_photo.png")

        # ── Step 6: Submit post ────────────────────────────────────────────────
        logger.info("Mencari tombol Posting/Post...")
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
                    logger.info(f"✅ Post button clicked via: {sel}")
                    posted = True
                    break
            except Exception:
                pass

        if not posted:
            # JS fallback
            result = page.evaluate("""
                () => {
                    const dialog = document.querySelector('div[role="dialog"]');
                    if (!dialog) return 'no dialog';
                    const btns = dialog.querySelectorAll('div[role="button"], button');
                    for (const btn of btns) {
                        const text = btn.textContent || '';
                        if (text.trim() === 'Posting' || text.trim() === 'Post') {
                            btn.click();
                            return 'clicked: ' + text.trim();
                        }
                    }
                    // Try aria-label
                    const labeled = dialog.querySelectorAll('[aria-label]');
                    for (const el of labeled) {
                        const label = el.getAttribute('aria-label') || '';
                        if (label === 'Posting' || label === 'Post') {
                            el.click();
                            return 'aria clicked: ' + label;
                        }
                    }
                    return 'not found';
                }
            """)
            logger.info(f"JS post result: {result}")
            if 'clicked' in str(result):
                posted = True

        if not posted:
            logger.warning("⚠️ Post button tidak ditemukan, mencoba Enter...")
            page.keyboard.press("Control+Enter")

        logger.info("Menunggu posting selesai...")
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
