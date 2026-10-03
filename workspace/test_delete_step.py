import sys, json, time
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
    browser = p.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_cookies(cookies)
    page = ctx.new_page()
    page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    post = page.locator('div[data-pressable-container="true"]').first
    menu_btn = post.locator('div[aria-haspopup="menu"]').first
    menu_btn.click()
    time.sleep(1.5)

    # Click Delete
    # Notice: In the menu, there is a text 'Delete'
    del_item = page.locator('div[role="menu"] div:has-text("Delete"), div[role="menuitem"]:has-text("Delete"), span:has-text("Delete")').first
    print("Delete item found:", del_item.count())
    del_item.click()
    time.sleep(2)

    page.screenshot(path="/root/storage/projects/dalang-ai/workspace/delete_confirm_dialog.png")

    dialog_info = page.evaluate("""() => {
        const dialog = document.querySelector('[role="dialog"]');
        if (!dialog) return { found: false };
        const buttons = Array.from(dialog.querySelectorAll('button, div[role="button"], span')).map(b => b.innerText ? b.innerText.trim() : '').filter(Boolean);
        return {
            found: true,
            text: dialog.innerText,
            buttons: [...new Set(buttons)]
        };
    }""")
    print("Dialog info:", dialog_info)

    browser.close()
