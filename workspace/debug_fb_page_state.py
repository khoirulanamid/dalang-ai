"""
debug_fb_page_state.py
Debug: Understand current FB page state and find compose button
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

    print("Step 1: Navigate to FB...")
    page.goto("https://web.facebook.com/", wait_until="domcontentloaded", timeout=40000)
    time.sleep(4)
    print(f"URL: {page.url}")
    
    # Check all buttons
    buttons = page.locator('div[role="button"]').all()
    print(f"Buttons: {len(buttons)}")
    for i, btn in enumerate(buttons[:30]):
        try:
            txt = btn.text_content()
            label = btn.get_attribute("aria-label")
            print(f"  [{i}] text={repr((txt or '').strip()[:60])} label={repr(label)}")
        except:
            pass
    
    # Click all "Lanjutkan" buttons to dismiss consent
    for i in range(3):
        try:
            btn = page.locator('div[role="button"]:has-text("Lanjutkan")').first
            if btn.is_visible(timeout=2000):
                print(f"Clicking Lanjutkan #{i+1}...")
                btn.click()
                time.sleep(3)
        except:
            break
    
    print(f"\nURL after consent: {page.url}")
    page.screenshot(path="fb_state_after_consent.png")
    
    # Check buttons again
    buttons = page.locator('div[role="button"]').all()
    print(f"\nButtons after consent: {len(buttons)}")
    for i, btn in enumerate(buttons[:30]):
        try:
            txt = btn.text_content()
            label = btn.get_attribute("aria-label")
            if txt and txt.strip():
                print(f"  [{i}] text={repr(txt.strip()[:60])} label={repr(label)}")
        except:
            pass
    
    # Check page title and key elements
    print(f"\nPage title: {page.title()}")
    
    # Check if logged in
    logged_in = page.locator('[aria-label="Beranda"]').count() > 0 or page.locator('[aria-label="Home"]').count() > 0
    print(f"Logged in (home icon): {logged_in}")
    
    # Check for feed composer
    composer = page.locator('[data-pagelet="FeedComposer"]').count()
    print(f"FeedComposer pagelet: {composer}")
    
    # Check all aria-labels
    all_labeled = page.locator('[aria-label]').all()
    print(f"\nAll aria-labeled elements: {len(all_labeled)}")
    for el in all_labeled[:40]:
        try:
            label = el.get_attribute("aria-label")
            role = el.get_attribute("role")
            if label:
                print(f"  role={role} label={repr(label[:60])}")
        except:
            pass
    
    browser.close()
    print("\nDone.")
