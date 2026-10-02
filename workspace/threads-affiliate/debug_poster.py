"""Debug poster - screenshot tiap tahap untuk cek apa yang terjadi di browser."""
import sys, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
DEBUG_DIR = Path("debug_screenshots")
DEBUG_DIR.mkdir(exist_ok=True)

raw = json.loads(COOKIES_PATH.read_text())
threads_c = raw.get("threads", {})

pw_cookies = []
for name, value in threads_c.items():
    for domain in [".threads.net", ".threads.com", ".instagram.com"]:
        pw_cookies.append({
            "name": name, "value": value, "domain": domain,
            "path": "/", "secure": True, "httpOnly": name in {"sessionid","mid","rur","ig_did"},
        })

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path="/usr/bin/chromium",
        args=["--no-sandbox","--disable-dev-shm-usage"])
    ctx = browser.new_context(viewport={"width":1280,"height":800})
    ctx.add_cookies(pw_cookies)
    page = ctx.new_page()

    print("Step 1: Buka threads.net...")
    page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    page.screenshot(path=str(DEBUG_DIR / "step1_home.png"))
    print(f"  Title: {page.title()}")
    print(f"  URL: {page.url}")

    # Cek apakah sudah login
    content = page.content()
    logged_in = "rizki" in content.lower() or "73692482884" in content or "logout" in content.lower()
    print(f"  Terdeteksi login: {logged_in}")

    print("Step 2: Cek elemen compose/new thread...")
    # Cari tombol buat post
    for sel in ['[aria-label*="new"]', '[aria-label*="thread"]', '[aria-label*="utas"]',
                'div[role="button"]', 'a[href*="new"]']:
        els = page.locator(sel)
        if els.count() > 0:
            print(f"  Found: {sel} -> {els.count()} elemen")

    page.screenshot(path=str(DEBUG_DIR / "step2_buttons.png"))
    browser.close()

print(f"\nScreenshot tersimpan di {DEBUG_DIR.absolute()}")
