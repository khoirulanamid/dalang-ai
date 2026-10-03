"""
tools/post_threads_dara.py
Reusable Playwright automation tool: Post Dara One Set campaign to Threads @rizki_mubarakid
- Thread split: Post 1 (hook relatable) + Post 2 (spec curation + CTA)
- Attaches HD product image (dara_oneset_1.jpg)
- Saves live screenshot to workspace/threads_dara_live.png

Pattern: Proven from post_jeans_threads.py (successful prior posts)
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── Config ──────────────────────────────────────────────────────────────────
COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
SCREENSHOT_OUT = Path("/root/storage/projects/dalang-ai/workspace/threads_dara_live.png")
PRODUCT_IMAGE = Path("/root/storage/projects/dalang-ai/workspace/product_images/dara_oneset/dara_oneset_1.jpg")
PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"

# ── Naskah: Sat-set OOTD angle (paling viral & relatable) ───────────────────
POST_1 = """Pagi-pagi buka lemari, bengong 10 menit, akhirnya pakai yang kemarin juga. 😅

Bukan males — tapi milih baju itu butuh energi yang harusnya bisa dipakai buat hal lain.

One set itu solusinya: blouse + kulot udah didesain sebagai pasangan. Warna match, proporsi pas, tinggal ambil dan pergi."""

POST_2 = """Dara One Set: satu keputusan, outfit selesai.

🧵 Rayon Premium/Twill
→ Bahan yang jatuh dan nggak kusut gampang — cocok langsung pakai tanpa setrika darurat

📐 Blouse: LD 110–120 cm, panjang 65–70 cm, lengan panjang berkancing
📐 Kulot: pinggang karet 60–110 cm, panjang 95–100 cm
→ Sat-set, nggak perlu mikir size

🎯 Cocok untuk: hangout, arisan, kerja, jalan-jalan — satu set handle semua

💰 Rp124.500 / set
🛒 Shopee → https://s.shopee.co.id/3qNaOVRWrP

#SatSetOOTD #OneSetWanita #FashionEfisien"""


def load_cookies() -> list:
    """Load session cookies from file."""
    if not COOKIES_PATH.exists():
        raise FileNotFoundError(f"Cookie file not found: {COOKIES_PATH}")
    raw = json.loads(COOKIES_PATH.read_text())
    httponly_keys = {"sessionid", "csrftoken", "ds_user_id", "ig_did", "mid"}
    cookies = []
    for k, v in raw.get("threads", {}).items():
        cookies.append({
            "name": k,
            "value": v,
            "domain": ".threads.com",
            "path": "/",
            "secure": True,
            "httpOnly": k in httponly_keys,
        })
    return cookies


def run() -> bool:
    print("=" * 60)
    print("🚀 Gathot Social Publisher — Dara One Set Threads Post")
    print("=" * 60)

    # 1. Load cookies
    print("1. Loading session cookies...")
    try:
        cookies = load_cookies()
        print(f"   ✅ {len(cookies)} cookies loaded")
    except FileNotFoundError as e:
        print(f"   ❌ {e}")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
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

        # 2. Open Threads compose modal
        print("2. Opening Threads compose modal (intent/post)...")
        page.goto(
            "https://www.threads.com/intent/post",
            wait_until="domcontentloaded",
            timeout=40000,
        )
        time.sleep(5)

        # 3. Find editors
        editors = page.locator('[contenteditable="true"]')
        count = editors.count()
        print(f"   Found {count} contenteditable editor(s)")

        if count == 0:
            print("   ❌ No editor found — saving debug screenshot")
            page.screenshot(path="/root/storage/projects/dalang-ai/threads_dara_debug_noeditor.png")
            browser.close()
            return False

        print(f"   ✅ Modal terbuka. Total editor: {count}")

        # 4. Type Post 1 (hook relatable)
        print("3. Typing Post 1 (hook relatable)...")
        editors.first.click()
        page.keyboard.insert_text(POST_1)
        time.sleep(1)
        print(f"   ✅ Post 1 typed ({len(POST_1)} chars)")

        # 5. Attach HD product image
        print("4. Attaching HD product image...")
        file_inputs = page.locator('input[type="file"]')
        if file_inputs.count() > 0 and PRODUCT_IMAGE.exists():
            file_inputs.first.set_input_files(str(PRODUCT_IMAGE))
            print(f"   ✅ Image attached: {PRODUCT_IMAGE.name}")
            time.sleep(4)
        else:
            print(f"   ⚠️  File inputs: {file_inputs.count()}, image exists: {PRODUCT_IMAGE.exists()}")

        page.screenshot(path="/root/storage/projects/dalang-ai/threads_dara_debug_post1.png")

        # 6. Add second thread post
        print("5. Adding Post 2 (spec curation + CTA)...")
        add_btn = page.locator('div[role="button"]:has-text("Add to thread")')
        if add_btn.count() > 0:
            add_btn.first.click()
            time.sleep(1)
            print("   ✅ 'Add to thread' clicked")
        else:
            print("   ⚠️  'Add to thread' button not found, continuing...")

        # Re-query editors after adding thread
        editors = page.locator('[contenteditable="true"]')
        count_after = editors.count()
        print(f"   Editors after add-thread: {count_after}")

        if count_after >= 2:
            editors.nth(1).click()
            page.keyboard.insert_text(POST_2)
            time.sleep(1)
            print(f"   ✅ Post 2 typed ({len(POST_2)} chars)")
        else:
            # Fallback: append to first editor
            print("   ⚠️  Fallback: appending Post 2 to first editor")
            editors.first.click()
            page.keyboard.press("Enter")
            page.keyboard.insert_text("\n\n" + POST_2)
            time.sleep(1)

        page.screenshot(path="/root/storage/projects/dalang-ai/threads_dara_debug_post2.png")

        # 7. Submit the post
        print("6. Clicking Post button...")
        post_btn = page.locator('div[role="button"]:has-text("Post")')
        if post_btn.count() > 0:
            post_btn.last.click(force=True)
            print("   🚀 Post button clicked!")
            time.sleep(6)
        else:
            print("   ❌ Post button not found!")
            page.screenshot(path="/root/storage/projects/dalang-ai/threads_dara_debug_nopost.png")
            browser.close()
            return False

        page.screenshot(path="/root/storage/projects/dalang-ai/threads_dara_debug_submitted.png")

        # 8. Navigate to profile and capture live screenshot
        print("7. Navigating to @rizki_mubarakid profile for live verification...")
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=40000)
        time.sleep(4)

        SCREENSHOT_OUT.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(SCREENSHOT_OUT), full_page=False)
        print(f"   📸 Live screenshot saved: {SCREENSHOT_OUT}")

        browser.close()

    print("=" * 60)
    print("🎉 THREADS DARA ONE SET POST — SELESAI!")
    print(f"   Screenshot: {SCREENSHOT_OUT}")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
