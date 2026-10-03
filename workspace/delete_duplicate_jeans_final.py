"""
Execution script for T-2301:
Buka browser Playwright ke akun Threads @rizki_mubarakid, buka menu titik tiga
pada salah satu status celana jeans yang duplikat, lalu klik tombol Delete dan
konfirmasi hapus sehingga di feed hanya tersisa 1 postingan celana jeans.
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
PROFILE_URL = "https://www.threads.com/@rizki_mubarakid"
SCREENSHOT_BEFORE = "/root/storage/projects/dalang-ai/workspace/delete_jeans_before.png"
SCREENSHOT_AFTER = "/root/storage/projects/dalang-ai/workspace/delete_jeans_after.png"

JEANS_KEYWORDS = ["celana jeans", "loose-fit", "baggy", "jeans korea", "begah", "shopee.co.id/4ljqtkz7w7", "musuh terbesar"]


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
    return cookies


def is_jeans_content(text: str) -> bool:
    return any(kw in text.lower() for kw in JEANS_KEYWORDS)


def run_deletion():
    cookies = load_cookies()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        print(f"1. Navigasi ke profil Threads: {PROFILE_URL}")
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

        jeans_indices = [p["index"] for p in posts_data if is_jeans_content(p["text"])]
        print(f"Postingan jeans terdeteksi pada indeks: {jeans_indices} (Total: {len(jeans_indices)})")

        page.screenshot(path=SCREENSHOT_BEFORE)
        print(f"Screenshot before tersimpan: {SCREENSHOT_BEFORE}")

        if len(jeans_indices) > 1:
            target_index = jeans_indices[1]
            print(f"\n2. Menargetkan postingan jeans duplikat pada index container: {target_index}")
            container = page.locator('div[data-pressable-container="true"]').nth(target_index)
            container.scroll_into_view_if_needed()
            time.sleep(1)

            print("3. Membuka menu opsi (titik tiga)...")
            menu_btn = container.locator('svg[aria-label="More options"], svg[aria-label="Lainnya"], svg[aria-label="More"]').locator("xpath=ancestor::div[@role='button']").first
            menu_btn.click()
            time.sleep(1.5)

            print("4. Mengklik opsi 'Delete' pada menu dropdown...")
            delete_option = page.locator('[role="menu"] div[role="menuitem"]:has-text("Delete"), [role="menu"] div:has-text("Delete"), [role="menu"] div:has-text("Hapus")').first
            delete_option.click()
            time.sleep(1.5)

            print("5. Menunggu dialog konfirmasi dan mengklik tombol konfirmasi 'Delete'...")
            dialog = page.locator('[role="dialog"]')
            dialog.wait_for(state="visible", timeout=10000)
            confirm_btn = dialog.locator('div[role="button"]:has-text("Delete"), button:has-text("Delete"), button:has-text("Hapus"), div[role="button"]:has-text("Hapus")').first
            print(f"   Tombol konfirmasi ditemukan: '{confirm_btn.inner_text()}'")
            confirm_btn.click()
            time.sleep(5)
        else:
            print("Postingan jeans duplikat sudah tidak ada atau sudah terhapus sebelumnya.")

        print("6. Reload profil untuk verifikasi jumlah postingan jeans...")
        page.goto(PROFILE_URL, wait_until="networkidle", timeout=35000)
        time.sleep(3)
        page.evaluate("() => { const s = document.getElementById('barcelona-splash-screen'); if (s) s.remove(); }")

        page.screenshot(path=SCREENSHOT_AFTER)
        print(f"Screenshot after tersimpan: {SCREENSHOT_AFTER}")

        final_posts = page.evaluate("""() => {
            const containers = document.querySelectorAll('div[data-pressable-container="true"]');
            return Array.from(containers).map((c, i) => ({
                index: i,
                text: c.innerText
            }));
        }""")

        remaining_jeans = [p for p in final_posts if is_jeans_content(p["text"])]
        print(f"\nPostingan jeans yang tersisa: {len(remaining_jeans)}")
        for jp in remaining_jeans:
            cleaned = jp["text"][:100].replace("\n", " ")
            print(f"  Container {jp['index']}: {cleaned}")

        browser.close()

        if len(remaining_jeans) == 1:
            print("\n✅ SUKSES: Hanya tersisa 1 postingan celana jeans di feed Threads!")
            return True
        else:
            print(f"\n⚠️ Perhatian: Jumlah jeans post tersisa: {len(remaining_jeans)}")
            return len(remaining_jeans) == 1


if __name__ == "__main__":
    success = run_deletion()
    sys.exit(0 if success else 1)
