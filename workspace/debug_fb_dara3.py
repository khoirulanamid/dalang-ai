"""
debug_fb_dara3.py
Debug: Cek page HTML untuk memahami dialog "Lanjutkan"
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

    # Simpan HTML untuk analisis
    html = page.content()
    with open("fb_dara_debug3.html", "w") as f:
        f.write(html)
    print(f"HTML saved ({len(html)} chars)")

    # Coba klik Lanjutkan (cookie consent)
    lanjutkan = page.locator('div[role="button"]:has-text("Lanjutkan")').first
    if lanjutkan.is_visible():
        print("Klik Lanjutkan (cookie consent)...")
        lanjutkan.click()
        time.sleep(4)

    page.screenshot(path="fb_dara_debug3.png")
    print(f"URL sekarang: {page.url}")

    # Coba navigate ke home feed langsung
    page.goto("https://web.facebook.com/?sk=h_chr", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    page.screenshot(path="fb_dara_debug3b.png")
    print(f"URL feed: {page.url}")

    # Cek semua teks
    all_texts = page.locator('*').all_text_contents()
    for t in all_texts[:50]:
        t = t.strip()
        if t and any(kw in t.lower() for kw in ['pikir', 'mind', 'status', 'apa yang', 'what']):
            print(f"  FOUND: {repr(t[:100])}")

    browser.close()
    print("Done.")
