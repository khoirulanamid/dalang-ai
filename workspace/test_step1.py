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

    # Let's scroll container 2 into view using page.evaluate so it's smooth
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
    page.screenshot(path="step1_menu_open.png")

    # Inspect all menu items currently visible
    items = page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('[role="menu"] *'));
        return els.map(el => ({
            tag: el.tagName,
            role: el.getAttribute('role'),
            text: el.innerText ? el.innerText.trim() : ''
        })).filter(x => x.text.length > 0 && x.text.length < 30);
    }""")
    print("Menu elements found:")
    for it in items:
        print(" ", it)

    browser.close()
