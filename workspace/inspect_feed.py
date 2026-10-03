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
    browser = p.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_cookies(cookies)
    page = ctx.new_page()
    page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Let's inspect all containers of posts
    posts = page.evaluate("""() => {
        // Find all articles or post rows
        // Threads wraps posts in divs with role="article" or data-pressable-container="true"
        const containers = Array.from(document.querySelectorAll('div[data-pressable-container="true"]'));
        return containers.map((c, i) => {
            const hasMenu = !!c.querySelector('div[aria-haspopup="menu"]');
            return {
                idx: i,
                text: c.innerText.replace(/\\n+/g, ' | '),
                hasMenu: hasMenu
            };
        });
    }""")

    for p_info in posts:
        print(f"[{p_info['idx']}] menu={p_info['hasMenu']}: {p_info['text'][:120]}")

    browser.close()
