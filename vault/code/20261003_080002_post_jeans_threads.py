import sys, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
IMAGE_PATH = "/root/storage/projects/dalang-ai/workspace/product_images/celana_jeans_korea_1.jpg"

POST_1 = """Sebagai cowok praktis, musuh terbesar pas nongkrong atau duduk seharian itu bukan kerjaan, tapi celana jeans yang bikin begah & sesak napas di perut bawah 🗿

Ini celana model loose-fit / baggy gaya Korea tapi ada opsi pinggang karetnya. Duduk santai di warkop berjam-jam aman, ga perlu diam-diam lepas kancing celana lagi 👌"""

POST_2 = """Kurasi speknya:
• Model: Loose-fit wide-leg gaya Korea (ga ngetat, ga bikin gerah)
• Bahan: Denim lembut tahan bentuk (ga melar/ga molor)
• Pinggang: Ada varian karet fleksibel & kancing biasa
• Saku: 4 saku dalam aman buat hp/dompet

🔗 Spill etalase produk di Shopee:
https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq"""

def run():
    print("1. Load cookies Threads...")
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
        page.goto("https://www.threads.com/intent/post", wait_until="domcontentloaded", timeout=35000)
        time.sleep(5)

        editors = page.locator('[contenteditable="true"]')
        if editors.count() == 0:
            print("❌ Editor tidak ditemukan!")
            browser.close()
            return False

        print(f"✅ Modal terbuka. Total editor: {editors.count()}")

        print("3. Mengetik Post 1 (Cowok Praktis)...")
        editors.first.click()
        page.keyboard.insert_text(POST_1)
        time.sleep(1)

        # Upload image to Post 1
        print("4. Upload foto produk...")
        file_inputs = page.locator('input[type="file"]')
        if file_inputs.count() > 0:
            file_inputs.first.set_input_files(IMAGE_PATH)
            print("✓ Foto celana jeans berhasil dilampirkan!")
            time.sleep(4)

        # Add to thread -> Post 2
        print("5. Tambah Post 2 (Spek + Link Shopee)...")
        add_btn = page.locator('div[role="button"]:has-text("Add to thread")')
        if add_btn.count() > 0:
            add_btn.first.click()
            time.sleep(1)

        editors = page.locator('[contenteditable="true"]')
        if editors.count() >= 2:
            editors.nth(1).click()
            page.keyboard.insert_text(POST_2)
            time.sleep(1)
        else:
            editors.first.click()
            page.keyboard.press("Enter")
            page.keyboard.insert_text("\n\n" + POST_2)

        # Klik Post
        print("6. Klik tombol Post...")
        post_btn = page.locator('div[role="button"]:has-text("Post")')
        if post_btn.count() > 0:
            post_btn.last.click(force=True)
            print("🚀 Tombol Post diklik!")
        else:
            print("❌ Tombol Post tidak ditemukan!")
            browser.close()
            return False

        print("7. Menunggu konfirmasi posting (12 detik)...")
        time.sleep(12)

        # Cek profil untuk verifikasi postingan live
        page.goto("https://www.threads.com/@rizki_mubarakid", wait_until="networkidle", timeout=35000)
        time.sleep(4)
        screenshot_path = "/root/storage/projects/dalang-ai/workspace/threads_jeans_live.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot profile berhasil disimpan: {screenshot_path}")

        browser.close()
        print("🎉 THREADS POSTING SELESAI DENGAN FOTO!")
        return True

if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
