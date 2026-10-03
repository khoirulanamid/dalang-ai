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

    print("Found menu button:", menu_btn.count())
    menu_btn.click()
    time.sleep(2)

    page.screenshot(path="/root/storage/projects/dalang-ai/workspace/menu_opened.png")

    menu_options = page.evaluate("""() => {
        const results = [];
        const elements = document.querySelectorAll('[role="menu"] *, [role="dialog"] *');
        elements.forEach(el => {
            const text = el.innerText ? el.innerText.trim() : '';
            if (text && text.length < 50 && !results.includes(text)) {
                results.push(text);
            }
        });
        return results;
    }""")

    print("Menu options found:")
    for opt in menu_options:
        print("  ->", opt)

    browser.close()
