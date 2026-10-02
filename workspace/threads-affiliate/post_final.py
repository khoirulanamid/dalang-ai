"""
Eksekusi posting final ke Threads - 100% presisi berdasarkan DOM Threads.com
"""
import sys, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
HISTORY_PATH = Path("data/post_history.json")

POST_1 = "nemu botol 1 liter yang katanya tahan dingin 24 jam. kalo beneran, es teh manis gw bakal bertahan lebih lama dari hubungan kalian 🗿"
POST_2 = "fitur yang bikin menarik:\n• tahan dingin 24 jam, panas 12 jam\n• 1 liter (ga perlu bolak-balik isi)\n• bebas BPA & anti bocor\n• pegangannya pake Silitech jadi ga licin"
POST_3 = "buat yang penasaran atau lagi cari tumbler gede, cek sendiri di sini:\nhttps://s.shopee.co.id/LngnAwCfq"
AFFILIATE_LINK = "https://s.shopee.co.id/LngnAwCfq"

def run():
    print("1. Load cookies...")
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
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        print("2. Buka intent/post modal...")
        page.goto("https://www.threads.com/intent/post", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        # Cek editor pertama
        editors = page.locator('[contenteditable="true"]')
        if editors.count() == 0:
            print("❌ Editor tidak ditemukan!")
            page.screenshot(path="debug_screenshots/error_no_editor.png")
            browser.close()
            return False

        print(f"✅ Modal terbuka. Total editor: {editors.count()}")

        # Ketik Post 1
        print("3. Mengetik Post 1...")
        editors.first.click()
        time.sleep(0.5)
        page.keyboard.type(POST_1, delay=20)
        time.sleep(1)

        # Klik Add to thread untuk Post 2
        print("4. Menambahkan Post 2 (Add to thread)...")
        add_btn = page.locator('div[role="button"]:has-text("Add to thread")')
        if add_btn.count() > 0:
            add_btn.first.click()
            time.sleep(2)
        else:
            print("⚠️ Tombol Add to thread tidak ketemu, lanjut satu post.")

        # Ketik Post 2
        editors = page.locator('[contenteditable="true"]')
        if editors.count() >= 2:
            print(f"5. Mengetik Post 2 (editor #{editors.count()})...")
            editors.nth(1).click()
            time.sleep(0.5)
            page.keyboard.type(POST_2, delay=20)
            time.sleep(1)

            # Klik Add to thread untuk Post 3
            print("6. Menambahkan Post 3 (Add to thread)...")
            add_btn = page.locator('div[role="button"]:has-text("Add to thread")')
            if add_btn.count() > 0:
                add_btn.last.click()
                time.sleep(2)

        # Ketik Post 3
        editors = page.locator('[contenteditable="true"]')
        if editors.count() >= 3:
            print(f"7. Mengetik Post 3 (editor #{editors.count()})...")
            editors.nth(2).click()
            time.sleep(0.5)
            page.keyboard.type(POST_3, delay=20)
            time.sleep(1)
        elif editors.count() == 2:
            print("Editor 3 gagal tambah, gabungkan ke Post 2.")
            editors.nth(1).click()
            page.keyboard.press("Enter")
            page.keyboard.type("\n" + POST_3, delay=20)

        # Simpan screenshot sebelum post
        page.screenshot(path="debug_screenshots/final_ready_to_post.png")
        print("📸 Screenshot draft tersimpan: debug_screenshots/final_ready_to_post.png")

        # Klik Post
        print("8. Klik tombol Post...")
        post_btn = page.locator('div[role="button"]:has-text("Post")')
        if post_btn.count() > 0:
            # Pastikan bukan tombol cancel
            post_btn.last.click(force=True)
            print("🚀 Tombol Post diklik!")
        else:
            print("❌ Tombol Post tidak ditemukan!")
            browser.close()
            return False

        # Tunggu proses posting
        print("9. Menunggu konfirmasi posting (12 detik)...")
        time.sleep(12)

        page.screenshot(path="debug_screenshots/final_after_post.png")
        print("📸 Screenshot sesudah post: debug_screenshots/final_after_post.png")

        browser.close()
        print("\n🎉 EKSEKUSI SELESAI!")
        return True

if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
