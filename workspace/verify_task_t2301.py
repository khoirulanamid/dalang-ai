"""
Verification script for T-2301:
Memverifikasi bahwa di feed Threads @rizki_mubarakid hanya tersisa tepat 1 postingan celana jeans
setelah proses delete postingan duplikat dieksekusi.
"""

import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"
JEANS_KEYWORDS = [
    "celana jeans",
    "loose-fit",
    "baggy",
    "jeans korea",
    "begah",
    "shopee.co.id/4ljqtkz7w7",
    "musuh terbesar",
]


def load_cookies():
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
            "httpOnly": k in httponly,
        })
        cookies.append({
            "name": k,
            "value": v,
            "domain": ".threads.net",
            "path": "/",
            "secure": True,
            "httpOnly": k in httponly,
        })
    return cookies


def verify_single_jeans_post() -> bool:
    cookies = load_cookies()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        print(f"Navigating to {PROFILE_URL}...")
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=35000)
        time.sleep(3)
        page.evaluate("() => { const s = document.getElementById('barcelona-splash-screen'); if (s) s.remove(); }")

        posts_data = page.evaluate("""() => {
            const containers = document.querySelectorAll('div[data-pressable-container="true"]');
            return Array.from(containers).map((c, i) => ({
                index: i,
                text: c.innerText
            }));
        }""")

        print(f"Total post containers found: {len(posts_data)}")

        jeans_posts = []
        for post in posts_data:
            txt = post["text"]
            if any(kw in txt.lower() for kw in JEANS_KEYWORDS):
                cleaned = txt[:100].replace("\n", " ")
                jeans_posts.append((post["index"], cleaned))

        print(f"Total jeans posts found: {len(jeans_posts)}")
        for idx, preview in jeans_posts:
            print(f"  Jeans post [{idx}]: {preview}")

        screenshot_path = "/root/storage/projects/dalang-ai/workspace/verify_final_threads_feed.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()
        return len(jeans_posts) == 1


if __name__ == "__main__":
    success = verify_single_jeans_post()
    if success:
        print("\n✅ VERIFIKASI BERHASIL: Tepat 1 postingan celana jeans tersisa di feed Threads!")
        sys.exit(0)
    else:
        print("\n❌ VERIFIKASI GAGAL: Jumlah postingan celana jeans bukan 1.")
        sys.exit(1)
