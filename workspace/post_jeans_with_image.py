import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIE_PATH = os.path.expanduser("~/.threads_poster/cookies/session.json")
IMAGE_PATH = "/root/storage/projects/dalang-ai/workspace/product_images/celana_jeans_korea_1.jpg"

post1_text = (
    "Sebagai cowok praktis, musuh terbesar pas nongkrong atau duduk seharian itu bukan kerjaan, "
    "tapi celana jeans yang bikin sesak napas di perut bawah 🗿\n\n"
    "Ini model loose-fit gaya Korea tapi ada opsi pinggang karetnya. "
    "Duduk santai di warkop berjam-jam aman, ga perlu diam-diam lepas kancing celana lagi 👌"
)

post2_text = (
    "Kurasi speknya:\n"
    "• Model: Loose-fit / wide-leg gaya Korea (ga ngetat, ga bikin gerah)\n"
    "• Bahan: Denim lembut tahan bentuk (ga melar/ga molor)\n"
    "• Pinggang: Ada varian karet fleksibel & kancing biasa\n"
    "• Saku: 4 saku dalam aman buat hp/dompet\n\n"
    "Spill etalasenya di Shopee: https://s.shopee.co.id/4LJqTkz7w7?exp_info=tt_6ZwLZ7Mq"
)

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    context = browser.new_context(
        storage_state=COOKIE_PATH,
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    print("[1] Buka Threads compose...")
    page.goto("https://www.threads.com/intent/post", wait_until="networkidle")
    time.sleep(2)

    # Input text 1
    composer = page.locator('div[contenteditable="true"]').first
    composer.click()
    composer.fill(post1_text)
    time.sleep(1)

    # Attach image
    print("[2] Lampirkan foto produk...")
    file_input = page.locator('input[type="file"]').first
    if file_input.count() > 0:
        file_input.set_input_files(IMAGE_PATH)
        print("✓ Image file attached via file input")
        time.sleep(4)

    # Klik tombol Kirim / Post
    print("[3] Submit postingan...")
    post_btn = page.locator('div[role="button"]:has-text("Kirim"), div[role="button"]:has-text("Post")').last
    post_btn.click()
    time.sleep(5)

    # Ambil screenshot verifikasi
    screenshot_path = "/root/storage/projects/dalang-ai/workspace/threads_jeans_posted.png"
    page.goto("https://www.threads.net/@rizki_mubarakid", wait_until="networkidle")
    time.sleep(3)
    page.screenshot(path=screenshot_path)
    print(f"✓ Screenshot profil tersimpan: {screenshot_path}")

    browser.close()
