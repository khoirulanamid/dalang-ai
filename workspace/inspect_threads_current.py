import json
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"

def main():
    raw = json.loads(COOKIES_PATH.read_text())
    cookies = []
    httponly = {"sessionid", "mid", "rur", "ig_did"}
    for k, v in raw.get("threads", {}).items():
        cookies.append({
            "name": k,
            "value": v,
            "domain": ".threads.com",
            "path": "/",
            "secure": True,
            "httpOnly": k in httponly
        })
        cookies.append({
            "name": k,
            "value": v,
            "domain": ".threads.net",
            "path": "/",
            "secure": True,
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
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=35000)
        page.wait_for_timeout(3000)

        posts = page.locator('div[data-pressable-container="true"]').all()
        print(f"Total posts: {len(posts)}")
        for i, post in enumerate(posts):
            print(f"--- POST {i} ---")
            print(post.inner_text())

        page.screenshot(path="threads_current_state.png")
        browser.close()

if __name__ == "__main__":
    main()
