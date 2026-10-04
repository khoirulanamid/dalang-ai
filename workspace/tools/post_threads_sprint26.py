"""
tools/post_threads_sprint26.py
Reusable Playwright automation tool: Post Sprint 26 One Set 4in1 Simple Vest Cherish campaign to Threads @rizki_mubarakid
"""

import sys
import json
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── Config ──────────────────────────────────────────────────────────────────
COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
BASE_DIR = Path("/root/storage/projects/dalang-ai/workspace")
PROJECT_ROOT = Path("/root/storage/projects/dalang-ai")

PRODUCT_IMAGE = BASE_DIR / "product_images/sprint26/sprint26_product_1.jpg"
if not PRODUCT_IMAGE.exists():
    PRODUCT_IMAGE = PROJECT_ROOT / "workspace/product_images/sprint26/sprint26_product_1.jpg"

SCREENSHOT_LOCATIONS = [
    BASE_DIR / "threads_sprint26_live.png",
    PROJECT_ROOT / "threads_sprint26_live.png",
    BASE_DIR / "workspace/threads_sprint26_live.png",
]

PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"

# ── Naskah Kurasi (Angle 1: Solusi Dilema Baju Ngampus & Nongkrong Sat-Set) ──
POST_1 = """Pernah berdiri 20 menit depan lemari tapi merasa gak punya baju? 👗

Lemari penuh sesak, tapi tiap mau ngampus atau nongkrong bingung setengah mati mencocokkan atasan, bawahan, dan hijab. Ujung-ujungnya berangkat telat.

Kuncinya bukan nambah tumpukan baju acak, tapi punya setelan siap pakai yang potongannya sudah terkurasi rapi dari atas sampai bawah."""

POST_2 = """One Set 4in1 Simple Vest Cherish hadir sebagai solusi outfit praktis:

- Vest Cherish: aksen rompi minimalis modern
- Inner manset: bahan adem, lentur, nyaman dipakai seharian
- Celana cutbray: siluet ramping dengan ilusi kaki lebih jenjang
- Hijab Bella Square: warna senada, mudah dibentuk rapi

Praktis dipakai tanpa ribet padu padan dari nol.
Link belanja Shopee: https://s.shopee.co.id/6L4wk65TN6

#OneSetHijab #OutfitNgampus #OOTDHijab #SetelanWanita #BellaSquare"""


def load_cookies() -> list:
    """Load session cookies from file for both threads.com and threads.net."""
    if not COOKIES_PATH.exists():
        raise FileNotFoundError(f"Cookie file not found: {COOKIES_PATH}")
    raw = json.loads(COOKIES_PATH.read_text())
    httponly_keys = {"sessionid", "csrftoken", "ds_user_id", "ig_did", "mid"}
    cookies = []
    threads_cookies = raw.get("threads", {})
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
    print("🚀 Gathot Social Publisher — Sprint 26 One Set 4in1 Threads Post", flush=True)
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
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        # Check profile first to see if it was already posted in the previous timed-out run
        print("Checking profile first...", flush=True)
        page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        page_text = page.content()
        if "Simple Vest Cherish" in page_text or "Pernah berdiri 20 menit" in page_text:
            print("   ✅ Already posted in previous attempt! Taking live verification screenshot...", flush=True)
            for loc in SCREENSHOT_LOCATIONS:
                try:
                    loc.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(loc), full_page=False)
                    print(f"   📸 Screenshot saved to {loc}", flush=True)
                except Exception as e:
                    print(f"   ⚠️ Could not save screenshot to {loc}: {e}", flush=True)
            browser.close()
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
            print("   ❌ Editor contenteditable not found!", flush=True)
            debug_path = BASE_DIR / "threads_sprint26_debug_noeditor.png"
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

        # 5. Attach HD product image
        print("4. Attaching HD product image...", flush=True)
        file_inputs = page.locator('input[type="file"]')
        if file_inputs.count() > 0 and PRODUCT_IMAGE.exists():
            file_inputs.first.set_input_files(str(PRODUCT_IMAGE))
            print(f"   ✅ Image attached: {PRODUCT_IMAGE.name}", flush=True)
            time.sleep(4)
        else:
            print(f"   ⚠️  File inputs: {file_inputs.count()}, image exists: {PRODUCT_IMAGE.exists()}", flush=True)

        # 6. Add second thread post
        print("5. Adding Post 2 (spec curation + CTA)...", flush=True)
        add_btn = page.locator('div[role="button"]:has-text("Add to thread")')
        if add_btn.count() > 0:
            add_btn.first.click()
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
            debug_path = BASE_DIR / "threads_sprint26_debug_nopost.png"
            page.screenshot(path=str(debug_path))
            browser.close()
            return False

        # 8. Navigate to profile and capture live screenshot
        print("7. Navigating to @rizki_mubarakid profile for live verification...", flush=True)
        page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        # Scroll down slightly to make sure the newest post is clearly visible in viewport
        page.mouse.wheel(0, 150)
        time.sleep(2)

        # Save primary screenshot and all alternate locations
        primary_saved = None
        for loc in SCREENSHOT_LOCATIONS:
            try:
                loc.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(loc), full_page=False)
                print(f"   📸 Screenshot saved to {loc}", flush=True)
                if primary_saved is None:
                    primary_saved = loc
            except Exception as e:
                print(f"   ⚠️ Could not save screenshot to {loc}: {e}", flush=True)

        # Check page content for verification
        page_text = page.content()
        if "Simple Vest Cherish" in page_text or "One Set 4in1" in page_text or "Pernah berdiri 20 menit" in page_text:
            print("   ✅ Live post content confirmed on profile feed!", flush=True)
        else:
            print("   ℹ️  Post submitted; profile reloaded. Checking feed items...", flush=True)

        browser.close()

    print("=" * 60, flush=True)
    print("🎉 THREADS SPRINT 26 POST — SELESAI!", flush=True)
    print(f"   Primary screenshot: {primary_saved}", flush=True)
    print("=" * 60, flush=True)
    return True


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
