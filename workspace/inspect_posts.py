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

    print("Navigating to profile...")
    page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Let's run JS in browser to get all posts and their texts
    posts_data = page.evaluate("""() => {
        const containers = Array.from(document.querySelectorAll('div[data-pressable-container="true"]'));
        return containers.map((c, i) => {
            const text = c.innerText || '';
            const hasMenu = !!c.querySelector('div[aria-haspopup="menu"]');
            return {
                index: i,
                text: text.slice(0, 150),
                fullLength: text.length,
                hasMenu: hasMenu,
                isPinned: text.includes('Pinned')
            };
        });
    }""")

    for p_info in posts_data:
        print(p_info)

    browser.close()
