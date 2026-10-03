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

    # Let's inspect the menu item element for Delete
    delete_elements = page.evaluate("""() => {
        const results = [];
        const all = document.querySelectorAll('*');
        for (const el of all) {
            if (el.innerText === 'Delete') {
                results.push({
                    tagName: el.tagName,
                    role: el.getAttribute('role'),
                    className: el.className,
                    parentTagName: el.parentElement ? el.parentElement.tagName : null,
                    parentRole: el.parentElement ? el.parentElement.getAttribute('role') : null,
                    outerHTML: el.outerHTML.slice(0, 150)
                });
            }
        }
        return results;
    }""")
    print("Delete elements:", json.dumps(delete_elements, indent=2))

    browser.close()
