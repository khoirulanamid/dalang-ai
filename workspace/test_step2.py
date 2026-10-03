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

    page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Scroll container 2 into view
    page.evaluate("""() => {
        const containers = document.querySelectorAll('div[data-pressable-container="true"]');
        if (containers[2]) {
            containers[2].scrollIntoView({ behavior: 'instant', block: 'center' });
        }
    }""")
    time.sleep(1)

    # Find the menu button in container 2
    post2 = page.locator('div[data-pressable-container="true"]').nth(2)
    menu_btn = post2.locator('div[aria-haspopup="menu"]').first
    print("Clicking menu button on container 2...")
    menu_btn.click()
    time.sleep(1.5)

    # Click Delete
    print("Clicking Delete menu item...")
    delete_item = page.locator('[role="menu"] [role="menuitem"]:has-text("Delete")')
    delete_item.click()
    time.sleep(2)
    page.screenshot(path="after_delete_item_click.png")

    # Inspect all elements currently on the page that could be a confirmation dialog
    dialog_elements = page.evaluate("""() => {
        // Find dialog or modal overlay
        const dialogs = Array.from(document.querySelectorAll('[role="dialog"], [aria-modal="true"], div[data-bloks-name]'));
        const bodyText = document.body.innerText;
        return {
            dialogCount: dialogs.length,
            dialogs: dialogs.map(d => ({
                tag: d.tagName,
                role: d.getAttribute('role'),
                text: d.innerText ? d.innerText.slice(0, 200) : ''
            })),
            bodyHasDelete: bodyText.includes('Delete') || bodyText.includes('Hapus')
        };
    }""")
    print("Dialog elements:", dialog_elements)

    # Also list all buttons on the page right now
    buttons = page.evaluate("""() => {
        const allBtns = Array.from(document.querySelectorAll('button, div[role="button"]'));
        return allBtns.map(b => ({
            tag: b.tagName,
            role: b.getAttribute('role'),
            text: b.innerText ? b.innerText.trim() : '',
            ariaLabel: b.getAttribute('aria-label')
        })).filter(x => x.text || x.ariaLabel);
    }""")
    print("Buttons found:")
    for b in buttons:
        print(" ", b)

    browser.close()
