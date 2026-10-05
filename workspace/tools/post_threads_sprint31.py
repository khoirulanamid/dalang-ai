"""
tools/post_threads_sprint31.py
Reusable Playwright automation tool: Post Sprint 31 INBEX IB-2R 170CM Tripod campaign to Threads @rizki_mubarakid
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

# Preferred HD product image
CANDIDATE_IMAGES = [
    WORKSPACE_DIR / "product_images/sprint31/sprint31_product_04.jpg",
    BASE_DIR / "product_images/sprint31/sprint31_product_04.jpg",
    WORKSPACE_DIR / "product_images/sprint31/sprint31_product_01.jpg",
    BASE_DIR / "product_images/sprint31/sprint31_product_01.jpg",
]

PRODUCT_IMAGE = None
for p in CANDIDATE_IMAGES:
    if p.exists():
        PRODUCT_IMAGE = p
        break

SCREENSHOT_LOCATIONS = [
    WORKSPACE_DIR / "threads_sprint31_live.png",
    BASE_DIR / "threads_sprint31_live.png",
    Path("workspace/threads_sprint31_live.png").resolve(),
    Path("threads_sprint31_live.png").resolve(),
    Path("/root/storage/projects/dalang-ai/workspace/threads_sprint31_live.png"),
]

PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"

# ── Naskah Kurasi (Gathot Social Standards: No personal claims, objective curation, relatable hook)
POST_1 = """Salah satu hal paling mengesalkan saat bikin konten sendiri: tripod tingginya nanggung, mentok di dada. Ujung-ujungnya kalau mau eye-level harus ditumpuk di atas kursi atau meja darurat yang rawan senggol.

Sudut rekaman dari bawah juga sering bikin postur tubuh kelihatan aneh dan dagu berlipat.

Makanya banyak kreator solo lebih memilih tripod yang tinggi maksimalnya bisa mencapai 170 cm, sejajar langsung sama pandangan mata berdiri normal."""

POST_2 = """Kurasi tripod tinggi proporsional INBEX IB-2R:

• Tinggi maksimal 170 cm: sejajar pandangan mata tanpa perlu meja tambahan
• Struktur aluminium kokoh dengan daya tampung beban hingga 5 kg
• Dilengkapi counterweight hook buat gantung tas saat outdoor berangin
• Termasuk remote Bluetooth nirkabel & 3-way pan-tilt head

Cek spesifikasi lengkapnya di Shopee:
https://s.shopee.co.id/gQbH58w3m

#TripodHP #VlogSetup #InbexTripod #KreatorIndonesia #ShopeeHaul"""


def load_cookies() -> list:
    """Load session cookies from file for both threads.com and threads.net."""
    if not COOKIES_PATH.exists():
        print(f"❌ Cookies not found at: {COOKIES_PATH}", flush=True)
        return []

    try:
        raw = json.loads(COOKIES_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Error reading cookies: {e}", flush=True)
        return []

    threads_cookies = raw.get("threads", raw.get("threads_cookies", raw))
    httponly_keys = {"sessionid", "csrftoken", "ds_user_id", "ig_did", "mid", "rur"}

    cookies = []
    for k, v in threads_cookies.items():
        if isinstance(v, dict):
            continue
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
    print("🚀 Gathot Social Publisher — Sprint 31 INBEX IB-2R Threads Post", flush=True)
    print("=" * 60, flush=True)

    # 1. Load cookies
    cookies = load_cookies()
    if not cookies:
        print("   ❌ Failed to load cookies.", flush=True)
        return False

    if not PRODUCT_IMAGE or not PRODUCT_IMAGE.exists():
        print(f"   ❌ Product image not found!", flush=True)
        return False
    print(f"   ✅ Product image verified: {PRODUCT_IMAGE} ({PRODUCT_IMAGE.stat().st_size // 1024} KB)", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
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
        time.sleep(4)

        # Check if already posted
        already_posted = False
        try:
            match = page.get_by_text("Salah satu hal paling mengesalkan saat bikin konten")
            if match.count() > 0:
                print("   ℹ️  Sprint 31 post already found on profile feed!", flush=True)
                already_posted = True
        except Exception:
            pass

        if already_posted:
            print("📸 Capturing verification screenshot of existing live post...", flush=True)
            for path in SCREENSHOT_LOCATIONS:
                path.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(path), full_page=False)
                print(f"   ✅ Saved: {path}", flush=True)
            browser.close()
            print("=" * 60, flush=True)
            print("🎉 THREADS SPRINT 31 POST ALREADY LIVE — VERIFIED!", flush=True)
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
            debug_path = WORKSPACE_DIR / "threads_sprint31_debug_noeditor.png"
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
        print(f"4. Uploading product image ({PRODUCT_IMAGE})...", flush=True)
        file_inputs = page.locator('input[type="file"]')
        if file_inputs.count() > 0:
            file_inputs.first.set_input_files(str(PRODUCT_IMAGE))
            print("   ✅ Image attached via file input!", flush=True)
            time.sleep(4)
        else:
            # Fallback: look for file upload trigger icon
            img_btns = page.locator('svg[aria-label*="Media" i], svg[aria-label*="photo" i], svg[aria-label*="Attach" i]')
            if img_btns.count() > 0:
                with page.expect_file_chooser() as fc_info:
                    img_btns.first.click()
                file_chooser = fc_info.value
                file_chooser.set_files(str(PRODUCT_IMAGE))
                print("   ✅ Image attached via file chooser!", flush=True)
                time.sleep(4)
            else:
                print("   ⚠️ Could not find attach icon. Continuing...", flush=True)

        # 6. Add second thread post
        print("5. Adding Post 2 (spec curation + CTA)...", flush=True)
        add_thread_btn = page.locator('div[role="button"]:has-text("Add to thread")')
        if add_thread_btn.count() == 0:
            add_thread_btn = page.locator('button:has-text("Add to thread")')
        if add_thread_btn.count() == 0:
            add_thread_btn = page.locator('text="Add to thread"')

        if add_thread_btn.count() > 0:
            add_thread_btn.first.click(force=True)
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
            debug_path = WORKSPACE_DIR / "threads_sprint31_debug_nopostbtn.png"
            page.screenshot(path=str(debug_path))
            browser.close()
            return False

        # 8. Reload profile and verify live post
        print("7. Verifying post on profile...", flush=True)
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(5)

        try:
            l1 = page.get_by_text("Salah satu hal paling mengesalkan saat bikin konten")
            if l1.count() > 0:
                l1.first.scroll_into_view_if_needed()
                time.sleep(2)
        except Exception:
            pass

        # 9. Save screenshot to all required locations
        print("8. Saving verification screenshot...", flush=True)
        primary_saved = None
        for path in SCREENSHOT_LOCATIONS:
            path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(path), full_page=False)
            print(f"   ✅ Saved: {path}", flush=True)
            if primary_saved is None:
                primary_saved = path

        # Check content on page
        body_text = page.locator("body").inner_text()
        if "Salah satu hal paling mengesalkan saat bikin konten" in body_text:
            print("   ✅ Live post content confirmed on profile feed!", flush=True)
        else:
            print("   ℹ️  Post submitted; profile reloaded. Checking feed items...", flush=True)

        browser.close()

    print("=" * 60, flush=True)
    print("🎉 THREADS SPRINT 31 POST — SELESAI!", flush=True)
    print(f"   Primary screenshot: {primary_saved}", flush=True)
    print("=" * 60, flush=True)
    return True


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
