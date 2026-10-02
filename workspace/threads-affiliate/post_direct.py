"""
Poster langsung ke Threads - berdasarkan UI nyata hasil debug screenshot.
- Tombol new thread: sidebar kiri "New thread" atau floating button "+"
- Editor: [contenteditable="true"] atau [data-lexical-editor="true"]
- Submit: tombol "Post" atau "Kirim"
"""
import sys, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
HISTORY_PATH = Path("data/post_history.json")

POST_1 = "nemu botol 1 liter yang katanya tahan dingin 24 jam. kalo beneran, es teh manis gw bakal bertahan lebih lama dari hubungan kalian 🗿"
POST_2 = "fitur yang bikin menarik:\n• tahan dingin 24 jam, panas 12 jam\n• 1 liter (ga perlu bolak-balik isi)\n• bebas BPA & anti bocor\n• pegangannya pake Silitech jadi ga licin"
POST_3 = "buat yang penasaran atau lagi cari tumbler gede, cek sendiri di sini:\nhttps://s.shopee.co.id/LngnAwCfq"
AFFILIATE_LINK = "https://s.shopee.co.id/LngnAwCfq"

def type_slow(page, text):
    """Ketik teks dengan delay human-like."""
    for ch in text:
        page.keyboard.type(ch)
        time.sleep(0.03)

def build_cookies():
    raw = json.loads(COOKIES_PATH.read_text())
    threads_c = raw.get("threads", {})
    ig_c = raw.get("instagram", {})
    cookies = []
    httponly = {"sessionid","mid","rur","ig_did"}
    for name, value in threads_c.items():
        for domain in [".threads.net", ".threads.com"]:
            cookies.append({"name": name, "value": value, "domain": domain,
                            "path": "/", "secure": True, "httpOnly": name in httponly})
    for name, value in ig_c.items():
        cookies.append({"name": name, "value": value, "domain": ".instagram.com",
                        "path": "/", "secure": True, "httpOnly": name in httponly})
    return cookies

def main():
    print("Membangun cookie...")
    cookies = build_cookies()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox","--disable-dev-shm-usage","--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        print("Membuka Threads...")
        page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        print(f"  URL: {page.url} | Title: {page.title()}")

        # Klik "New thread" di sidebar
        print("Klik New thread...")
        clicked = False
        for sel in [
            'a[href*="/new"]',
            '[aria-label*="New thread"]',
            '[aria-label*="Utas baru"]',
            'div[role="button"]:has-text("New thread")',
            'a:has-text("New thread")',
        ]:
            els = page.locator(sel)
            if els.count() > 0:
                els.first.click()
                clicked = True
                print(f"  Klik via: {sel}")
                break

        if not clicked:
            # Fallback: floating button (+) di kanan bawah
            btns = page.locator('div[role="button"]')
            btns.last.click()
            clicked = True
            print("  Klik via floating button")

        time.sleep(4)

        # Tunggu editor muncul
        print("Tunggu editor...")
        editor = None
        for _ in range(8):
            for sel in ['[contenteditable="true"]', '[data-lexical-editor="true"]', 'div[role="textbox"]']:
                els = page.locator(sel)
                if els.count() > 0:
                    editor = els.first
                    print(f"  Editor ditemukan: {sel}")
                    break
            if editor:
                break
            time.sleep(2)

        if not editor:
            page.screenshot(path="debug_screenshots/fail_no_editor.png")
            print("ERROR: Editor tidak ditemukan")
            sys.exit(1)

        # Ketik Post 1
        print("Ketik Post 1...")
        editor.click()
        time.sleep(1)
        type_slow(page, POST_1)
        time.sleep(2)

        # Tambah Post 2 - klik "Add to thread" atau tombol +
        print("Tambah Post 2...")
        add_clicked = False
        for sel in [
            '[aria-label*="Add to thread"]',
            '[aria-label*="Tambah"]',
            'div[role="button"]:has-text("Add to thread")',
            'button:has-text("Add to thread")',
        ]:
            els = page.locator(sel)
            if els.count() > 0:
                els.first.click()
                add_clicked = True
                print(f"  Add to thread via: {sel}")
                break

        time.sleep(3)

        # Editor Post 2
        editors = page.locator('[contenteditable="true"]')
        if editors.count() >= 2:
            editors.nth(1).click()
        else:
            print("  Hanya 1 editor, ketik di editor yang ada")
            editor.click()
        time.sleep(1)
        type_slow(page, POST_2)
        time.sleep(2)

        # Tambah Post 3
        if add_clicked:
            print("Tambah Post 3...")
            for sel in [
                '[aria-label*="Add to thread"]',
                '[aria-label*="Tambah"]',
                'div[role="button"]:has-text("Add to thread")',
            ]:
                els = page.locator(sel)
                if els.count() > 0:
                    els.last.click()
                    print(f"  Add to thread via: {sel}")
                    break
            time.sleep(3)

        # Editor Post 3
        editors = page.locator('[contenteditable="true"]')
        n = editors.count()
        print(f"  Total editor: {n}")
        if n >= 3:
            editors.nth(2).click()
        elif n >= 2:
            editors.nth(1).click()
        else:
            editor.click()
        time.sleep(1)
        type_slow(page, POST_3)
        time.sleep(2)

        page.screenshot(path="debug_screenshots/before_submit.png")
        print("Screenshot before_submit.png disimpan")

        # Submit
        print("Klik Post/Kirim...")
        submitted = False
        for sel in [
            'div[role="button"]:has-text("Post")',
            'div[role="button"]:has-text("Kirim")',
            'button:has-text("Post")',
            'button:has-text("Kirim")',
            '[aria-label="Post"]',
            '[aria-label="Kirim"]',
        ]:
            els = page.locator(sel)
            if els.count() > 0:
                els.last.click(force=True)
                submitted = True
                print(f"  Submit via: {sel}")
                break

        if not submitted:
            page.screenshot(path="debug_screenshots/fail_no_submit.png")
            print("ERROR: Tombol Post/Kirim tidak ditemukan")
            sys.exit(1)

        time.sleep(8)
        page.screenshot(path="debug_screenshots/after_submit.png")
        print("Screenshot after_submit.png disimpan")
        print(f"URL setelah submit: {page.url}")
        print("\n✅ SELESAI - cek screenshot after_submit.png")
        browser.close()

    # Catat history
    history_path = HISTORY_PATH
    history_path.parent.mkdir(exist_ok=True)
    if history_path.exists():
        data = json.loads(history_path.read_text())
        posts = data.get("posts", [])
    else:
        posts = []

    posts.append({
        "date": datetime.now().isoformat(),
        "product": "Tumbler 1 Liter Tahan Panas Dingin",
        "category": "gadget",
        "hook_category": "storytelling",
        "hook_text": POST_1,
        "affiliate_link": AFFILIATE_LINK,
        "post_url": "",
    })
    history_path.write_text(json.dumps({"posts": posts[-100:]}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
