import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"

def load_cookies():
    if not COOKIES_PATH.exists():
        raise FileNotFoundError(f"Cookie file not found at {COOKIES_PATH}")
    raw = json.loads(COOKIES_PATH.read_text())
    cookies = []
    httponly = {"sessionid", "mid", "rur", "ig_did"}
    for k, v in raw.get("threads", {}).items():
        cookies.append({
            "name": k,
            "value": v,
            "domain": ".threads.com",
            "path": "/",
            "secure": True,
            "httpOnly": k in httponly
        })
        cookies.append({
            "name": k,
            "value": v,
            "domain": ".threads.net",
            "path": "/",
            "secure": True,
            "httpOnly": k in httponly
        })
    return cookies

def is_jeans_content(text: str) -> bool:
    keywords = ["celana jeans", "loose-fit", "baggy", "jeans korea", "musuh terbesar", "jeans"]
    return any(kw in text.lower() for kw in keywords)

def execute():
    cookies = load_cookies()
    print("Loaded cookies successfully.")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        context.add_cookies(cookies)
        page = context.new_page()

        print(f"Navigating to {PROFILE_URL}...")
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=45000)
        time.sleep(4)

        page.screenshot(path="before_action.png")

        # Find all post containers
        post_elements = page.locator('div[data-pressable-container="true"]').all()
        print(f"Total post containers found: {len(post_elements)}")

        jeans_posts = []
        for idx, el in enumerate(post_elements):
            try:
                txt = el.inner_text()
                if is_jeans_content(txt):
                    jeans_posts.append((idx, el, txt))
            except Exception as e:
                print(f"Error checking post {idx}: {e}")

        print(f"Found {len(jeans_posts)} jeans posts.")

        if len(jeans_posts) == 1:
            print("Already exactly 1 jeans post remaining! Verifying...")
            browser.close()
            return True

        if len(jeans_posts) == 0:
            print("No jeans posts found at all. Retrying page load...")
            time.sleep(3)
            browser.close()
            return False

        # If more than 1, we delete one duplicate
        print(f"Duplicate jeans posts detected ({len(jeans_posts)}). Deleting the first one...")
        target_idx, target_el, target_txt = jeans_posts[0]
        print(f"Targeting post: {target_txt[:100]}...")

        # Find three dots / menu button within target_el
        menu_button = target_el.locator('div[aria-haspopup="menu"]').first
        if not menu_button.is_visible():
            menu_button = target_el.locator('svg[aria-label="More"], svg[aria-label="Lainnya"]').locator("..").first

        print("Clicking three-dot menu...")
        menu_button.click()
        time.sleep(2)
        page.screenshot(path="menu_opened_check.png")

        # Find Delete item in menu
        print("Looking for Delete menu item...")
        delete_item = page.locator('[role="menu"] div[role="menuitem"]:has-text("Delete"), [role="menu"] div:has-text("Delete"), [role="menu"] span:has-text("Delete"), [role="menu"] div:has-text("Hapus")').first
        print(f"Delete item text: {delete_item.inner_text()}")
        delete_item.click()
        time.sleep(2)
        page.screenshot(path="confirm_dialog_check.png")

        # Find confirm delete button in dialog
        print("Looking for confirmation Delete button...")
        confirm_btn = page.locator('[role="dialog"] button:has-text("Delete"), [role="dialog"] div[role="button"]:has-text("Delete"), [role="dialog"] span:has-text("Delete"), [role="dialog"] button:has-text("Hapus"), [role="dialog"] div[role="button"]:has-text("Hapus")').first
        print(f"Confirm button text: {confirm_btn.inner_text()}")
        confirm_btn.click()
        print("Delete confirmation clicked.")
        time.sleep(5)

        # Refresh and verify
        print("Refreshing profile...")
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=45000)
        time.sleep(4)
        page.screenshot(path="after_action.png")

        final_posts = page.locator('div[data-pressable-container="true"]').all()
        final_jeans = []
        for idx, el in enumerate(final_posts):
            try:
                txt = el.inner_text()
                if is_jeans_content(txt):
                    final_jeans.append((idx, txt))
            except Exception:
                pass

        print(f"Final jeans posts count: {len(final_jeans)}")
        for idx, txt in final_jeans:
            print(f"- Post {idx}: {txt[:100]}")

        browser.close()
        return len(final_jeans) == 1

if __name__ == "__main__":
    ok = execute()
    if ok:
        print("SUCCESS: Exactly 1 jeans post remaining.")
        sys.exit(0)
    else:
        print("FAILURE: Expected 1 jeans post.")
        sys.exit(1)
