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

    post = page.locator('div[data-pressable-container="true"]').first

    # Inspect all elements with role="button" or interactive elements in post
    buttons = post.locator('[role="button"]').all()
    print("Buttons in post:", len(buttons))
    for idx, b in enumerate(buttons):
        tag = b.evaluate("el => el.tagName")
        aria = b.get_attribute("aria-label")
        text = b.inner_text().strip()
        html = b.evaluate("el => el.outerHTML")[:150]
        print(f"[{idx}] tag={tag}, aria={aria}, text='{text}', html={html}")

    # Also let's find all svgs in post and their parent roles
    svgs = post.locator('svg').all()
    print("\nSVGs in post:", len(svgs))
    for idx, s in enumerate(svgs):
        svg_title = s.locator('title').inner_text() if s.locator('title').count() > 0 else None
        parent_tag = s.evaluate("el => el.parentElement.tagName")
        parent_role = s.evaluate("el => el.parentElement.getAttribute('role')")
        parent_aria = s.evaluate("el => el.parentElement.getAttribute('aria-label')")
        parent_class = s.evaluate("el => el.parentElement.className")
        print(f"[{idx}] svg_title={svg_title}, parent_tag={parent_tag}, parent_role={parent_role}, parent_aria={parent_aria}, class={parent_class}")

    browser.close()
