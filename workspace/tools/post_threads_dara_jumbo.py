"""
tools/post_threads_dara_jumbo.py
Reusable Playwright automation tool: Post Dara Jumbo One Set LD 120 campaign to Threads @rizki_mubarakid
- Task ID: T-2503
- Thread split: Post 1 (relatable hook / everyday curvy dilemma) + Post 2 (objective spec curation + affiliate link + hashtags)
- Attaches HD product image (product_images/dara_jumbo/dara_jumbo_1.jpg)
- Saves live screenshot to workspace/threads_dara_jumbo_live.png

Compliant with standards/gathot_social_standards.md:
- No fake personal claims ('aku sudah pakai')
- Objective specs & consensus
- Relatable humor and curiosity gap hook
- Thread split: Post 1 (hook) -> Post 2 (specs + CTA + 4 hashtags)
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── Config ──────────────────────────────────────────────────────────────────
COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
BASE_DIR = Path("/root/storage/projects/dalang-ai/workspace")
PRODUCT_IMAGE = BASE_DIR / "product_images/dara_jumbo/dara_jumbo_1.jpg"
SCREENSHOT_PRIMARY = BASE_DIR / "threads_dara_jumbo_live.png"
SCREENSHOT_SUB = BASE_DIR / "workspace/threads_dara_jumbo_live.png"
PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"

# ── Naskah Kurasi (Angle 1: Anti Sempit & Bebas Begah) ────────────────────────
POST_1 = """Pernah nggak sih beli baju labelnya 'jumbo', tapi pas dipakai duduk rasanya kancing mau meletus dan ketiak ketarik? 🥲

Dilema nyata cewek atau ibu-ibu curvy tuh bukan susah cari model, tapi nemu setelan yang beneran lega tanpa bikin kelihatan kayak karung.

Kuncinya ada di potongan proporsional."""

POST_2 = """Nah, kurasi Dara Set Jumbo ini kasih solusi ukuran riil:

- Lingkar dada (LD) riil 120 cm: leluasa di dada & ketiak, muat BB hingga 85+ kg
- Kulot pinggang full karet (60-120 cm) + lingkar paha 75 cm: anti begah pas duduk
- Bahan Rayon Premium Twill: serat rapat, adem semriwing, dan flowy
- Kancing depan aktif: praktis busui friendly

Harga Rp135.500 per set.
Link belanja Shopee: https://s.shopee.co.id/5AsyAcB5TV

#BajuJumboWanita #OneSetJumbo #RayonAdem #OOTDBigSize"""


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
                "value": v,
                "domain": domain,
                "path": "/",
                "secure": True,
                "httpOnly": k in httponly_keys,
            })
    return cookies


def run() -> bool:
    print("=" * 60)
    print("🚀 Gathot Social Publisher — Dara Jumbo One Set Threads Post")
    print("=" * 60)

    # 1. Load cookies
    print("1. Loading session cookies...")
    try:
        cookies = load_cookies()
        print(f"   ✅ {len(cookies)} cookies loaded (for .threads.com & .threads.net)")
    except FileNotFoundError as e:
        print(f"   ❌ {e}")
        return False

    if not PRODUCT_IMAGE.exists():
        print(f"   ❌ Product image not found at: {PRODUCT_IMAGE}")
        return False
    print(f"   ✅ Product image verified: {PRODUCT_IMAGE} ({PRODUCT_IMAGE.stat().st_size // 1024} KB)")

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
            debug_path = BASE_DIR / "threads_dara_jumbo_debug_noeditor.png"
            page.screenshot(path=str(debug_path))
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
            time.sleep(5)
        else:
            print(f"   ⚠️  File inputs: {file_inputs.count()}, image exists: {PRODUCT_IMAGE.exists()}")

        # 6. Add second thread post
        print("5. Adding Post 2 (spec curation + CTA)...")
        add_btn = page.locator('div[role="button"]:has-text("Add to thread")')
        if add_btn.count() > 0:
            add_btn.first.click()
            time.sleep(2)
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

        # 7. Submit the post
        print("6. Clicking Post button...")
        post_btn = page.locator('div[role="button"]:has-text("Post")')
        if post_btn.count() > 0:
            post_btn.last.click(force=True)
            print("   🚀 Post button clicked!")
            time.sleep(8)
        else:
            print("   ❌ Post button not found!")
            debug_path = BASE_DIR / "threads_dara_jumbo_debug_nopost.png"
            page.screenshot(path=str(debug_path))
            browser.close()
            return False

        # 8. Navigate to profile and capture live screenshot
        print("7. Navigating to @rizki_mubarakid profile for live verification...")
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=40000)
        time.sleep(5)

        # Save primary screenshot
        SCREENSHOT_PRIMARY.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(SCREENSHOT_PRIMARY), full_page=False)
        print(f"   📸 Live screenshot saved: {SCREENSHOT_PRIMARY}")

        # Also save to workspace/threads_dara_jumbo_live.png if subfolder exists
        if SCREENSHOT_SUB.parent.exists():
            page.screenshot(path=str(SCREENSHOT_SUB), full_page=False)
            print(f"   📸 Live screenshot saved to sub-dir: {SCREENSHOT_SUB}")

        # Check if posted content appears
        page_text = page.inner_text("body")
        if "kancing mau meletus" in page_text or "Dara Set Jumbo" in page_text or "LD 120" in page_text:
            print("   ✅ Live post content confirmed on profile feed!")
        else:
            print("   ℹ️  Post submitted; profile reloaded. Checking feed items...")

        browser.close()

    print("=" * 60)
    print("🎉 THREADS DARA JUMBO POST — SELESAI!")
    print(f"   Primary screenshot: {SCREENSHOT_PRIMARY}")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
