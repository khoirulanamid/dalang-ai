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

    # Let's inspect posts on the page
    posts = page.locator('div[data-pressable-container="true"]').all()
    print(f"Total post containers found: {len(posts)}")

    jeans_posts = []
    for idx, post in enumerate(posts):
        text = post.inner_text()
        print(f"Post {idx} preview: {text[:80]!r}")
        if any(w in text.lower() for w in ["celana jeans", "loose-fit", "baggy", "jeans"]):
            jeans_posts.append((idx, post, text))

    print(f"Total jeans posts found: {len(jeans_posts)}")

    if len(jeans_posts) <= 1:
        print(f"Jeans posts count is already {len(jeans_posts)}. No duplicate to delete or already deleted.")
    else:
        # We need to delete one duplicate jeans post so only 1 remains!
        target_idx, target_post, target_text = jeans_posts[0]
        print(f"Targeting jeans post {target_idx} for deletion...")

        # Find menu button (aria-haspopup="menu" or three dots)
        menu_btn = target_post.locator('div[aria-haspopup="menu"], div[role="button"][aria-label*="More"], svg[aria-label*="More"]').first
        if not menu_btn.is_visible():
            # Scroll into view
            target_post.scroll_into_view_if_needed()
            time.sleep(1)

        menu_btn = target_post.locator('div[aria-haspopup="menu"]').first
        print("Clicking menu button...")
        menu_btn.click()
        time.sleep(2)
        page.screenshot(path="after_click_menu.png")

        # In menu, find Delete option
        # Let's see all text items in any popup/menu
        menu_items = page.locator('div[role="menu"] [role="menuitem"], div[role="menu"] span, div[role="dialog"] span').all()
        print("Menu items text:")
        for item in menu_items:
            t = item.inner_text().strip()
            if t:
                print(f"  - {t}")

        # Find and click Delete
        del_btn = page.locator('div[role="menuitem"]:has-text("Delete"), div[role="menu"] div:has-text("Delete"), span:has-text("Delete")').first
        print("Clicking Delete option...")
        del_btn.click()
        time.sleep(2)
        page.screenshot(path="after_click_delete.png")

        # Now check what dialog or prompt appeared
        # Look for confirmation dialog
        print("Checking for confirmation dialog...")
        # Inspect all buttons or dialog elements on page
        dialog_elements = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button, div[role="button"], div[role="dialog"] *')).map(el => ({
                tag: el.tagName,
                role: el.getAttribute('role'),
                text: el.innerText ? el.innerText.trim() : '',
                ariaLabel: el.getAttribute('aria-label')
            })).filter(x => x.text.length > 0 && x.text.length < 50);
        }""")
        print("Interactive elements on screen:")
        for el in dialog_elements[-15:]:
            print(" ", el)

        # Look specifically for confirm "Delete" in the confirmation dialog
        # Usually confirmation dialog has two buttons: "Cancel" and "Delete"
        # Or red "Delete" button
        confirm_btn = page.locator('div[role="dialog"] div[role="button"]:has-text("Delete"), div[role="dialog"] button:has-text("Delete"), div[role="dialog"] span:has-text("Delete")').first
        if confirm_btn.count() > 0 and confirm_btn.is_visible():
            print("Found confirm delete button, clicking...")
            confirm_btn.click()
        else:
            # Maybe the dialog role is different or general button
            # Let's search for any visible Delete button not inside a role=menu
            alt_confirm = page.locator(':not([role="menu"]) > div[role="button"]:has-text("Delete"), button:has-text("Delete")')
            print(f"Alternative confirm buttons count: {alt_confirm.count()}")
            for i in range(alt_confirm.count()):
                btn = alt_confirm.nth(i)
                if btn.is_visible():
                    print(f"Clicking confirm button {i}: {btn.inner_text()}")
                    btn.click()
                    break

        time.sleep(3)
        page.screenshot(path="after_confirm_delete.png")

        # Reload profile and check remaining jeans posts
        print("Reloading profile to verify...")
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        page.screenshot(path="profile_after_deletion.png")

        final_posts = page.locator('div[data-pressable-container="true"]').all()
        final_jeans = []
        for idx, post in enumerate(final_posts):
            text = post.inner_text()
            if any(w in text.lower() for w in ["celana jeans", "loose-fit", "baggy", "jeans"]):
                final_jeans.append((idx, text))

        print(f"Remaining jeans posts count: {len(final_jeans)}")
        for idx, text in final_jeans:
            print(f"  Post {idx}: {text[:80]!r}")

    browser.close()
