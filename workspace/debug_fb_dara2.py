"""
debug_fb_dara2.py
Debug: Handle dialog dan cek state setelah dismiss
"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".fb_poster/cookies/session.json"

def load_cookies():
    raw = json.loads(COOKIES_PATH.read_text())
    httponly = {"sb", "datr", "c_user", "xs", "fr"}
    return [
        {"name": k, "value": str(v), "domain": ".facebook.com", "path": "/", "secure": True, "httpOnly": k in httponly}
        for k, v in raw.items()
    ]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    context.add_cookies(load_cookies())
    page = context.new_page()

    print("Navigasi ke Facebook...")
    page.goto("https://web.facebook.com/", wait_until="domcontentloaded", timeout=40000)
    time.sleep(5)

    # Cek semua button
    buttons = page.locator('div[role="button"]').all()
    print(f"Buttons found: {len(buttons)}")
    for btn in buttons:
        try:
            txt = btn.text_content()
            if txt and txt.strip():
                print(f"  Button: {repr(txt.strip()[:80])}")
        except:
            pass

    # Klik "Lanjutkan" jika ada
    for sel in ['div[role="button"]:has-text("Lanjutkan")', 'button:has-text("Lanjutkan")', '[aria-label="Lanjutkan"]']:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                print(f"Klik: {sel}")
                loc.first.click()
                time.sleep(3)
                break
        except:
            pass

    page.screenshot(path="fb_dara_debug2.png")
    print("Screenshot after dismiss: fb_dara_debug2.png")

    # Cek lagi
    url = page.url
    print(f"URL: {url}")
    buttons2 = page.locator('div[role="button"]').all_text_contents()
    print(f"Buttons after dismiss ({len(buttons2)}):")
    for t in buttons2[:20]:
        if t.strip():
            print(f"  - {repr(t.strip()[:80])}")

    # Cek span yang relevan
    all_spans = page.locator('span').all_text_contents()
    print(f"\nSpan yang mengandung kata kunci:")
    for t in all_spans:
        t = t.strip()
        if t and any(kw in t.lower() for kw in ['pikir', 'mind', 'status', 'apa', 'what']):
            print(f"  - {repr(t[:100])}")

    browser.close()
    print("Done.")
