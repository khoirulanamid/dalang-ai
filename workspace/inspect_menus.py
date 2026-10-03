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

    info = page.evaluate("""() => {
        const buttons = Array.from(document.querySelectorAll('div[aria-haspopup="menu"]'));
        return buttons.map((b, i) => {
            let cur = b;
            let text = '';
            for (let d = 0; d < 10; d++) {
                if (!cur.parentElement) break;
                cur = cur.parentElement;
                if (cur.innerText && cur.innerText.includes('celana jeans')) {
                    text = cur.innerText;
                    break;
                }
            }
            const rect = b.getBoundingClientRect();
            return {
                index: i,
                x: rect.x,
                y: rect.y,
                visible: rect.width > 0 && rect.height > 0,
                hasJeansText: text.length > 0,
                isPinned: text.includes('Pinned'),
                textSnippet: text.slice(0, 80)
            };
        });
    }""")

    for item in info:
        print(item)

    browser.close()
