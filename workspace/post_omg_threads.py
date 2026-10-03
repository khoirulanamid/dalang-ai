import sys, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"

POST_1 = """Cewek ngabisin 20 menit cuma buat milih nude base ombre 🥲💄

Cowok ngeliatnya "ini kan warnanya sama kayak yang di rumah". Padahal ada nude peach, nude mauve, sama warm nude. Beda sedikit undertone, hasil akhir riasan bibir langsung berubah drastis."""

POST_2 = """Secara teknis, ini alasan kenapa seri OMG Matte Kiss Lip Cream banyak dipilih untuk base ombre:

• Formula dasar: Quick-dry matte yang cepat nge-set, gak geser pas ditimpa lip tint/lip cream gelap di tengah.
• Proteksi kelembapan: Dilengkapi Jojoba Oil dan Vitamin E biar bibir gak pecah atau ketarik seharian.
• Daya tutup: Konsentrasi pigmen padat, langsung nutup garis gelap pinggiran bibir dalam satu usapan tipis.
• Legalitas: Terdaftar resmi BPOM dan Halal MUI (aman bumil/busui), harga belasan ribu."""

POST_3 = """Rumus kombinasi ombre paling favorit:
• Base luar: Shade 13 (Latte) atau Shade 14 (Cappuccino)
• Inner center: Shade 12 (Scarlet) buat merah cerah, atau Shade 15 (Espresso) buat kesan deep berry

🔗 Katalog swatch lengkap & ketersediaan stok resmi:
https://s.shopee.co.id/7ptiWpCm06?exp_info=tt_6ZwLZ7Mq

Di meja rias lo sekarang, udah ada berapa botol lip cream nude yang menurut orang lain warnanya 'kembar'? 🗿"""

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

        print("3. Mengetik Post 1 (Hook Cewek Dilema)...")
        editors.first.click()
        page.keyboard.insert_text(POST_1)
        time.sleep(1)

        # Add to thread -> Post 2
        print("4. Tambah Post 2 (Kurasi Spek + Link)...")
        add_btn = page.locator('div[role="button"]:has-text("Add to thread")')
        if add_btn.count() > 0:
            add_btn.first.click()
            time.sleep(1)

        # Gabungkan Post 2 dan Post 3 agar ringkas dan pasti lolos 2 thread
        FULL_POST_2 = POST_2 + "\n\n" + POST_3
        editors = page.locator('[contenteditable="true"]')
        if editors.count() >= 2:
            editors.nth(1).click()
            page.keyboard.insert_text(FULL_POST_2)
            time.sleep(1)
        else:
            editors.first.click()
            page.keyboard.press("Enter")
            page.keyboard.insert_text("\n\n" + FULL_POST_2)

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
        time.sleep(3)
        page.screenshot(path="/root/storage/projects/dalang-ai/workspace/threads_omg_live.png")
        print("📸 Screenshot profile berhasil disimpan: workspace/threads_omg_live.png")

        browser.close()
        print("🎉 THREADS POSTING SELESAI!")
        return True

if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
