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
    page.goto(PROFILE_URL, wait_until="networkidle", timeout=40000)
    time.sleep(3)

    # Let's inspect the first post
    posts = page.locator('div[data-pressable-container="true"]')
    print(f"Posts count: {posts.count()}")
    for i in range(min(4, posts.count())):
        post = posts.nth(i)
        print(f"\n--- Post {i} ---")
        text = post.inner_text()
        print("Text snippet:", text[:100].replace('\n', ' '))
        
        # Look for buttons or svgs or aria-label
        elements = post.locator('[aria-label]').all()
        labels = [el.get_attribute('aria-label') for el in elements]
        print("aria-labels in post:", labels)

        # Look for svgs
        svgs = post.locator('svg').all()
        print(f"Number of svgs: {len(svgs)}")
        for s in svgs:
            print("svg parent tag:", s.evaluate("el => el.parentElement.tagName"), "parent role:", s.evaluate("el => el.parentElement.getAttribute('role')"), "aria-label:", s.get_attribute("aria-label"))

    browser.close()
