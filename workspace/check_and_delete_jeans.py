import json
import os
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


def is_jeans(text: str) -> bool:
    return any(kw in text.lower() for kw in JEANS_KEYWORDS)


def main():
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
        page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        # Check posts
        containers = page.locator('div[data-pressable-container="true"]')
        count = containers.count()
        print(f"Total post containers count: {count}")

        jeans_indices = []
        for i in range(count):
            c = containers.nth(i)
            txt = c.inner_text()
            first_line = txt.split("\n")[0] if txt else ""
            second_line = txt.split("\n")[1] if len(txt.split("\n")) > 1 else ""
            print(f"Container {i}: {first_line} | {second_line}")
            if is_jeans(txt):
                jeans_indices.append(i)

        print(f"Jeans posts indices: {jeans_indices}")

        if len(jeans_indices) > 1:
            print(f"Found {len(jeans_indices)} jeans posts. Deleting duplicate (index {jeans_indices[1]})...")
            # Target the duplicate
            dup_container = containers.nth(jeans_indices[1])

            # Find menu button in this container
            menu_btn = dup_container.locator('div[aria-haspopup="menu"]').first
            menu_btn.click()
            time.sleep(2)

            # Click delete option
            delete_option = page.locator('[role="menu"] div[role="menuitem"]:has-text("Delete"), [role="menu"] div:has-text("Delete"), [role="menu"] span:has-text("Delete"), [role="menu"] div:has-text("Hapus")').first
            print("Clicking Delete menu option...")
            delete_option.click()
            time.sleep(2)

            # Confirm delete dialog
            confirm_btn = page.locator('[role="dialog"] button:has-text("Delete"), [role="dialog"] div[role="button"]:has-text("Delete"), [role="dialog"] span:has-text("Delete"), [role="dialog"] button:has-text("Hapus"), [role="dialog"] div[role="button"]:has-text("Hapus")').first
            print("Clicking confirm Delete button...")
            confirm_btn.click()
            time.sleep(5)

            # Reload and check
            print("Reloading page to verify...")
            page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
        elif len(jeans_indices) == 1:
            print("Already exactly 1 jeans post remaining in feed!")
        else:
            print("Warning: No jeans posts found.")

        # Final verification
        final_containers = page.locator('div[data-pressable-container="true"]')
        final_count = final_containers.count()
        remaining_jeans = []
        for i in range(final_count):
            c = final_containers.nth(i)
            txt = c.inner_text()
            if is_jeans(txt):
                remaining_jeans.append((i, txt[:100].replace("\n", " ")))

        page.screenshot(path="/root/storage/projects/dalang-ai/workspace/threads_feed_verified_single_jeans.png")
        print(f"Final remaining jeans posts count: {len(remaining_jeans)}")
        for idx, preview in remaining_jeans:
            print(f" - [{idx}] {preview}")

        browser.close()
        return len(remaining_jeans) == 1


if __name__ == "__main__":
    success = main()
    if success:
        print("SUCCESS: Exactly 1 jeans post remains in feed.")
        sys.exit(0)
    else:
        print("FAILURE: Jeans posts count is not 1.")
        sys.exit(1)
