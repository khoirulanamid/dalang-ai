"""
debug_fb_dara.py
Debug: Screenshot halaman Facebook untuk cek state & selector
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
    time.sleep(6)
    page.screenshot(path="fb_dara_debug_home.png")
    print("Screenshot home saved: fb_dara_debug_home.png")

    # Cek semua teks yang ada di halaman
    texts = page.locator('div[role="button"]').all_text_contents()
    print(f"Semua div[role=button] texts ({len(texts)} items):")
    for t in texts[:30]:
        if t.strip():
            print(f"  - {repr(t.strip()[:80])}")

    # Cek span texts
    span_texts = page.locator('span').all_text_contents()
    print(f"\nSpan texts yang mengandung 'pikir' atau 'mind':")
    for t in span_texts:
        if 'pikir' in t.lower() or 'mind' in t.lower() or 'status' in t.lower():
            print(f"  - {repr(t.strip()[:100])}")

    # Cek apakah login berhasil
    url = page.url
    print(f"\nCurrent URL: {url}")
    title = page.title()
    print(f"Page title: {title}")

    browser.close()
    print("Done.")
