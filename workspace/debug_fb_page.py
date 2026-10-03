"""
debug_fb_page.py — Snapshot halaman FB untuk debug selector
"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".fb_poster/cookies/session.json"

def load_cookies():
    raw = json.loads(COOKIES_PATH.read_text())
    return [
        {"name": k, "value": str(v), "domain": ".facebook.com", "path": "/", "secure": True}
        for k, v in raw.items()
    ]

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path="/usr/bin/chromium",
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-notifications"],
    )
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    ctx.add_cookies(load_cookies())
    page = ctx.new_page()

    print("Navigasi ke Facebook...")
    page.goto("https://www.facebook.com/", wait_until="networkidle", timeout=40000)
    time.sleep(4)

    page.screenshot(path="fb_debug_home.png")
    print("Screenshot disimpan: fb_debug_home.png")

    # Cari semua elemen yang mungkin jadi composer
    for sel in [
        "div[role='button']",
        "div[role='textbox']",
        "span",
    ]:
        els = page.locator(sel).all()
        print(f"\n{sel}: {len(els)} elemen")
        for el in els[:5]:
            try:
                txt = el.inner_text()[:80].strip()
                if txt:
                    print(f"  → '{txt}'")
            except Exception:
                pass

    # Dump HTML snippet
    html = page.content()
    with open("fb_debug_home.html", "w") as f:
        f.write(html[:50000])
    print("\nHTML disimpan: fb_debug_home.html (50KB)")

    browser.close()
