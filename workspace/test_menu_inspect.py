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

    # Dismiss splash screen if any
    page.evaluate("() => { const s = document.getElementById('barcelona-splash-screen'); if (s) s.remove(); }")

    # Find jeans post
    posts = page.locator('div[data-pressable-container="true"]').all()
    print(f"Posts found: {len(posts)}")
    target_post = None
    for p_el in posts:
        txt = p_el.inner_text()
        # Find unpinned jeans post
        if "celana jeans" in txt.lower() and "pinned" not in txt.lower():
            target_post = p_el
            print("Found unpinned jeans post:", txt[:80])
            break

    if not target_post:
        target_post = posts[0]

    menu_btn = target_post.locator('div[aria-haspopup="menu"]').first
    menu_btn.click()
    time.sleep(1.5)

    items = page.evaluate("""() => {
        const menu = document.querySelector('[role="menu"]');
        if (!menu) return { error: "No menu found" };
        const all = Array.from(menu.querySelectorAll('*'));
        return all.map(el => ({
            tag: el.tagName,
            role: el.getAttribute('role'),
            text: el.innerText ? el.innerText.trim() : '',
            classes: el.className
        })).filter(x => x.text === 'Delete' || x.text === 'Hapus');
    }""")
    print("Delete matching elements in menu:", json.dumps(items, indent=2))

    browser.close()
