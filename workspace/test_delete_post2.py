import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
PROFILE_URL  = "https://www.threads.com/@rizki_mubarakid"

raw = json.loads(COOKIES_PATH.read_text())
cookies = []
httponly = {"sessionid", "mid", "rur", "ig_did"}
for k, v in raw.get("threads", {}).items():
    cookies.append({
        "name": k, "value": v,
        "domain": ".threads.com", "path": "/", "secure": True,
        "httpOnly": k in httponly
    })

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path="/usr/bin/chromium",
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_cookies(cookies)
    page = ctx.new_page()

    print("1. Navigating to profile...")
    page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Post index 2 is the unpinned duplicate jeans post
    post_containers = page.locator('div[data-pressable-container="true"]')
    post_2 = post_containers.nth(2)
    print("Post 2 text preview:", post_2.inner_text()[:100].replace('\n', ' '))

    # Scroll post 2 into view
    post_2.scroll_into_view_if_needed()
    time.sleep(1)

    # Find the menu button inside post 2
    menu_btn = post_2.locator('div[aria-haspopup="menu"]').first
    print("Clicking menu button on Post 2...")
    menu_btn.click()
    time.sleep(2)
    page.screenshot(path="post2_menu_opened.png")

    # Let's inspect all items in the menu
    menu_items = page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('[role="menu"] [role="menuitem"], [role="menu"] div, [role="menu"] span'));
        return items.map(el => ({
            tag: el.tagName,
            role: el.getAttribute('role'),
            text: el.innerText ? el.innerText.trim() : ''
        })).filter(x => x.text.length > 0 && x.text.length < 50);
    }""")
    print("Menu items found:")
    for item in menu_items:
        print(" ", item)

    # Click the "Delete" item in menu
    print("Locating Delete menu item...")
    del_item = page.locator('[role="menu"] [role="menuitem"]:has-text("Delete"), [role="menu"] div:has-text("Delete"), [role="menu"] span:has-text("Delete")').first
    print("Delete item visible:", del_item.is_visible())
    del_item.click()
    time.sleep(2)
    page.screenshot(path="post2_after_click_delete.png")

    # Let's inspect the dialog that appeared
    dialog_elements = page.evaluate("""() => {
        const dialog = document.querySelector('[role="dialog"]') || document.body;
        const all = Array.from(dialog.querySelectorAll('*'));
        return all.map(el => ({
            tag: el.tagName,
            role: el.getAttribute('role'),
            text: el.innerText ? el.innerText.trim() : '',
            classes: el.className
        })).filter(x => x.text.length > 0 && x.text.length < 60);
    }""")
    print("\nElements after clicking delete:")
    for el in dialog_elements[-20:]:
        print(" ", el)

    browser.close()
