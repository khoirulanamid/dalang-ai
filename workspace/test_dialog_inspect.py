import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"

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
    page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
    time.sleep(3)
    page.evaluate("() => { const s = document.getElementById('barcelona-splash-screen'); if (s) s.remove(); }")

    # Find unpinned jeans post
    posts = page.locator('div[data-pressable-container="true"]').all()
    target_post = None
    for p_el in posts:
        txt = p_el.inner_text()
        if "celana jeans" in txt.lower() and "pinned" not in txt.lower():
            target_post = p_el
            print("Found post to delete:", txt[:60].replace("\n", " "))
            break

    if not target_post:
        target_post = posts[0]

    menu_btn = target_post.locator('div[aria-haspopup="menu"]').first
    menu_btn.click()
    time.sleep(1.5)

    delete_item = page.get_by_role("menuitem", name="Delete")
    print("Delete item count:", delete_item.count())
    delete_item.click()
    time.sleep(2)

    page.screenshot(path="after_delete_click_dialog.png")

    dialog_buttons = page.evaluate("""() => {
        const dialog = document.querySelector('[role="dialog"]');
        if (!dialog) return { error: "No dialog found", allDialogs: document.querySelectorAll('[role]').length };
        const buttons = Array.from(dialog.querySelectorAll('button, div[role="button"], span'));
        return {
            dialogText: dialog.innerText,
            buttons: buttons.map(b => ({
                tag: b.tagName,
                role: b.getAttribute('role'),
                text: b.innerText ? b.innerText.trim() : '',
                ariaLabel: b.getAttribute('aria-label')
            })).filter(x => x.text.length > 0 && x.text.length < 50)
        };
    }""")
    print("Dialog buttons:", json.dumps(dialog_buttons, indent=2))

    browser.close()
