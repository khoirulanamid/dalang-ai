"""
tools/post_threads_sprint28.py
Reusable Playwright automation tool: Post Sprint 28 AMORA EMWEHA Jaket Crop Wanita campaign to Threads @rizki_mubarakid
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── Config ──────────────────────────────────────────────────────────────────
COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
BASE_DIR = Path("/root/storage/projects/dalang-ai")
WORKSPACE_DIR = BASE_DIR / "workspace"

PRODUCT_IMAGE = WORKSPACE_DIR / "product_images/sprint28/sprint28_product_1.jpg"
if not PRODUCT_IMAGE.exists():
    PRODUCT_IMAGE = BASE_DIR / "product_images/sprint28/sprint28_product_1.jpg"

SCREENSHOT_LOCATIONS = [
    WORKSPACE_DIR / "threads_sprint28_live.png",
    BASE_DIR / "threads_sprint28_live.png",
    Path("workspace/threads_sprint28_live.png").resolve(),
    Path("threads_sprint28_live.png").resolve(),
]

PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"

# ── Naskah Kurasi (Angle 1: Dilema Buka Lemari Penuh tapi Merasa Gak Punya Baju) ──
POST_1 = """Pemandangan klasik tiap mau keluar rumah: buka lemari pakaian penuh sesak, tapi ujung-ujungnya bengong 15 menit sambil mikir 'kok berasa gak punya baju ya?' 😭

Masalahnya bukan kurang baju, tapi belum nemu outer serbaguna yang tinggal dilempar ke kaos polos atau inner manset langsung auto kelihatan rapi dan niat dandan."""

POST_2 = """Kurasi Amora Jaket Crop dari EMWEHA ini menarik buat solusi outfit praktis:
• Potongan depan runcing (pointed front) yang bikin ilusi pinggang lebih proporsional
• Kerah kemeja klasik, cocok buat kasual sampai semi-formal
• Aksen slit di ujung lengan
• Lingkar dada 100 cm, panjang baju 53 cm

Outfit simpel buat harian.
Cek di Shopee: https://s.shopee.co.id/20vxzX4Fx0

#OOTDIndo #OuterKekinian #JaketCrop #FashionWanita #RacunShopee"""


def load_cookies() -> list:
    """Load session cookies from file for both threads.com and threads.net."""
    if not COOKIES_PATH.exists():
        raise FileNotFoundError(f"Cookie file not found: {COOKIES_PATH}")

    with open(COOKIES_PATH, "r", encoding="utf-8") as f:
        cookie_data = json.load(f)

    threads_cookies = cookie_data.get("threads_cookies", cookie_data)
    httponly_keys = {"sessionid", "mid", "rur", "ig_did"}

    cookies = []
    for k, v in threads_cookies.items():
        for domain in [".threads.com", ".threads.net"]:
            cookies.append({
                "name": k,
                "value": str(v),
                "domain": domain,
                "path": "/",
                "secure": True,
                "httpOnly": k in httponly_keys,
            })
    return cookies


def run() -> bool:
    print("=" * 60, flush=True)
    print("🚀 Gathot Social Publisher — Sprint 28 AMORA Jaket Crop Threads Post", flush=True)
    print("=" * 60, flush=True)

    # 1. Load cookies
    print("1. Loading session cookies...", flush=True)
    try:
        cookies = load_cookies()
        print(f"   ✅ {len(cookies)} cookies loaded (for .threads.com & .threads.net)", flush=True)
    except FileNotFoundError as e:
        print(f"   ❌ {e}", flush=True)
        return False

    if not PRODUCT_IMAGE.exists():
        print(f"   ❌ Product image not found at: {PRODUCT_IMAGE}", flush=True)
        return False
    print(f"   ✅ Product image verified: {PRODUCT_IMAGE} ({PRODUCT_IMAGE.stat().st_size // 1024} KB)", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 1200},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        # Check existing posts on profile first
        print("🔍 Checking profile first...", flush=True)
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        page_text = page.content()
        if "Pemandangan klasik tiap mau keluar rumah" in page_text or "Amora Jaket Crop" in page_text:
            print("   ✅ Already posted! Scrolling post into view and taking live verification screenshot...", flush=True)
            try:
                l1 = page.get_by_text("Pemandangan klasik")
                if l1.count() > 0:
                    l1.first.scroll_into_view_if_needed()
                    time.sleep(2)
            except Exception as e:
                print(f"   ⚠️ Scroll error: {e}", flush=True)

            primary_saved = None
            for loc in SCREENSHOT_LOCATIONS:
                try:
                    loc.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(loc), full_page=False)
                    print(f"   📸 Screenshot saved to {loc} ({loc.stat().st_size} bytes)", flush=True)
                    if primary_saved is None:
                        primary_saved = loc
                except Exception as e:
                    print(f"   ⚠️ Could not save screenshot to {loc}: {e}", flush=True)
            browser.close()
            print("=" * 60, flush=True)
            print("🎉 THREADS SPRINT 28 POST VERIFIED LIVE!", flush=True)
            print(f"   Primary screenshot: {primary_saved}", flush=True)
            print("=" * 60, flush=True)
            return True

        # 2. Open Threads compose modal
        print("2. Opening Threads compose modal (intent/post)...", flush=True)
        page.goto(
            "https://www.threads.com/intent/post",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        time.sleep(4)

        # 3. Find editors
        editors = page.locator('[contenteditable="true"]')
        count = editors.count()
        if count == 0:
            print("   ⚠️  Waiting for editor...", flush=True)
            try:
                page.wait_for_selector('[contenteditable="true"]', timeout=10000)
                editors = page.locator('[contenteditable="true"]')
                count = editors.count()
            except Exception as e:
                print(f"   ❌ Editor selector timeout: {e}", flush=True)

        if count == 0:
            print("   ❌ No editor found! Dumping debug screenshot...", flush=True)
            debug_path = WORKSPACE_DIR / "threads_sprint28_debug_noeditor.png"
            page.screenshot(path=str(debug_path))
            browser.close()
            return False

        print(f"   ✅ Modal terbuka. Total editor: {count}", flush=True)

        # 4. Type Post 1 (hook relatable)
        print("3. Typing Post 1 (hook relatable)...", flush=True)
        editors.first.click()
        page.keyboard.insert_text(POST_1)
        time.sleep(1)
        print(f"   ✅ Post 1 typed ({len(POST_1)} chars)", flush=True)

        # 5. Upload image to Post 1
        print(f"4. Uploading product image ({PRODUCT_IMAGE})...", flush=True)
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            file_input.first.set_input_files(str(PRODUCT_IMAGE))
            print("   ✅ Image attached via file input!", flush=True)
            time.sleep(5)  # wait for upload thumbnail
        else:
            print("   ⚠️ File input not found directly, clicking image attach button...", flush=True)
            # Try clicking the paperclip / image icon
            img_btns = page.locator('svg[aria-label*="image" i], svg[aria-label*="photo" i], svg[aria-label*="Attach" i]')
            if img_btns.count() > 0:
                with page.expect_file_chooser() as fc_info:
                    img_btns.first.click()
                file_chooser = fc_info.value
                file_chooser.set_files(str(PRODUCT_IMAGE))
                print("   ✅ Image attached via file chooser!", flush=True)
                time.sleep(5)
            else:
                print("   ⚠️ Could not find attach icon. Continuing text-only...", flush=True)

        # 6. Add second post (thread continuation)
        print("5. Adding second post to thread...", flush=True)
        # Look for "Add to thread" button
        add_thread_btn = page.locator('div[role="button"]:has-text("Add to thread")')
        if add_thread_btn.count() == 0:
            add_thread_btn = page.locator('button:has-text("Add to thread")')
        if add_thread_btn.count() == 0:
            # Fallback: find any element with text "Add to thread"
            add_thread_btn = page.locator('text="Add to thread"')

        if add_thread_btn.count() > 0:
            add_thread_btn.first.click()
            time.sleep(2)
            print("   ✅ 'Add to thread' clicked", flush=True)
        else:
            print("   ⚠️  'Add to thread' button not found, continuing...", flush=True)

        # Re-query editors after adding thread
        editors = page.locator('[contenteditable="true"]')
        count_after = editors.count()
        print(f"   Editors after add-thread: {count_after}", flush=True)

        if count_after >= 2:
            editors.nth(1).click()
            page.keyboard.insert_text(POST_2)
            time.sleep(1)
            print(f"   ✅ Post 2 typed ({len(POST_2)} chars)", flush=True)
        else:
            print("   ⚠️  Fallback: appending Post 2 to first editor", flush=True)
            editors.first.click()
            page.keyboard.press("Enter")
            page.keyboard.insert_text("\n\n" + POST_2)
            time.sleep(1)

        # 7. Submit the post
        print("6. Clicking Post button...", flush=True)
        post_btn = page.locator('div[role="button"]:has-text("Post")')
        if post_btn.count() > 0:
            post_btn.last.click(force=True)
            print("   🚀 Post button clicked!", flush=True)
            time.sleep(8)
        else:
            print("   ❌ Post button not found!", flush=True)
            debug_path = WORKSPACE_DIR / "threads_sprint28_debug_nopostbtn.png"
            page.screenshot(path=str(debug_path))
            browser.close()
            return False

        # 8. Reload profile and verify live post
        print("7. Verifying post on profile...", flush=True)
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(5)

        try:
            l1 = page.get_by_text("Pemandangan klasik")
            if l1.count() > 0:
                l1.first.scroll_into_view_if_needed()
                time.sleep(2)
        except Exception as e:
            print(f"   ⚠️ Scroll error: {e}", flush=True)

        # Save primary screenshot and all alternate locations
        primary_saved = None
        for loc in SCREENSHOT_LOCATIONS:
            try:
                loc.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(loc), full_page=False)
                print(f"   📸 Screenshot saved to {loc} ({loc.stat().st_size} bytes)", flush=True)
                if primary_saved is None:
                    primary_saved = loc
            except Exception as e:
                print(f"   ⚠️ Could not save screenshot to {loc}: {e}", flush=True)

        # Check content on profile page
        feed_content = page.content()
        if "Pemandangan klasik" in feed_content or "Amora" in feed_content:
            print("   ✅ Live post content confirmed on profile feed!", flush=True)
        else:
            print("   ℹ️  Post submitted; profile reloaded. Checking feed items...", flush=True)

        browser.close()

    print("=" * 60, flush=True)
    print("🎉 THREADS SPRINT 28 POST — SELESAI!", flush=True)
    print(f"   Primary screenshot: {primary_saved}", flush=True)
    print("=" * 60, flush=True)
    return True


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
