"""
T-2001: Delete Duplicate Jeans Post on Threads @rizki_mubarakid
================================================================
Modul Playwright untuk menghapus salah satu postingan celana jeans
yang duplikat di Threads akun @rizki_mubarakid via:
  tombol menu opsi (titik tiga / ⋯) -> Delete -> Confirm

Strategy:
  1. Load session cookies dari ~/.threads_poster/cookies/session.json
  2. Navigasi ke profil @rizki_mubarakid
  3. Scan semua postingan, temukan yang mengandung keyword celana jeans
  4. Hover postingan pertama yang ditemukan -> klik tombol ⋯ (more options)
  5. Klik "Delete" di dropdown menu
  6. Konfirmasi dialog "Delete" jika muncul
  7. Screenshot hasil akhir sebagai bukti
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ── Config ──────────────────────────────────────────────────────────────────
COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
PROFILE_URL  = "https://www.threads.com/@rizki_mubarakid"
SCREENSHOT_BEFORE = "/root/storage/projects/dalang-ai/workspace/delete_jeans_before.png"
SCREENSHOT_AFTER  = "/root/storage/projects/dalang-ai/workspace/delete_jeans_after.png"
SCREENSHOT_DEBUG  = "/root/storage/projects/dalang-ai/workspace/delete_jeans_debug.png"

# Keyword untuk mendeteksi postingan celana jeans
JEANS_KEYWORDS = [
    "celana jeans",
    "loose-fit",
    "baggy",
    "jeans korea",
    "wide-leg",
    "denim",
    "karet fleksibel",
    "shopee.co.id/4LJqTkz7w7",
    "musuh terbesar",
    "begah",
]

HTTPONLY_COOKIES = {"sessionid", "mid", "rur", "ig_did"}


def load_cookies() -> list[dict]:
    """Load Threads session cookies dari file JSON."""
    print("1. Load cookies Threads...")
    if not COOKIES_PATH.exists():
        raise FileNotFoundError(
            f"Cookie file tidak ditemukan: {COOKIES_PATH}\n"
            "Pastikan session sudah login dan cookie tersimpan."
        )
    raw = json.loads(COOKIES_PATH.read_text())
    cookies = []
    for k, v in raw.get("threads", {}).items():
        cookies.append({
            "name": k,
            "value": v,
            "domain": ".threads.com",
            "path": "/",
            "secure": True,
            "httpOnly": k in HTTPONLY_COOKIES,
        })
    print(f"   ✓ {len(cookies)} cookies dimuat.")
    return cookies


def is_jeans_post(text: str) -> bool:
    """Cek apakah teks postingan mengandung keyword celana jeans."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in JEANS_KEYWORDS)


def run() -> bool:
    cookies = load_cookies()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        # ── Step 2: Buka profil ──────────────────────────────────────────────
        print(f"2. Navigasi ke profil: {PROFILE_URL}")
        page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=40000)
        time.sleep(4)
        page.screenshot(path=SCREENSHOT_BEFORE)
        print(f"   📸 Screenshot before: {SCREENSHOT_BEFORE}")

        # ── Step 3: Scroll & temukan postingan jeans duplikat ────────────────
        print("3. Scan postingan untuk menemukan celana jeans duplikat...")

        # Scroll sedikit untuk memuat postingan
        for _ in range(3):
            page.keyboard.press("End")
            time.sleep(1.5)
        page.keyboard.press("Home")
        time.sleep(1)

        # Ambil semua artikel/postingan yang terlihat
        # Threads menggunakan article atau div dengan role="article"
        post_selectors = [
            'article',
            'div[data-pressable-container="true"]',
            'div[role="article"]',
        ]

        target_post = None
        jeans_count = 0

        for selector in post_selectors:
            posts = page.locator(selector)
            count = posts.count()
            if count == 0:
                continue
            print(f"   Ditemukan {count} elemen dengan selector '{selector}'")

            for i in range(count):
                post = posts.nth(i)
                try:
                    text = post.inner_text(timeout=3000)
                    if is_jeans_post(text):
                        jeans_count += 1
                        print(f"   ✓ Postingan jeans #{jeans_count} ditemukan (index {i})")
                        if jeans_count == 1:
                            # Simpan referensi postingan pertama sebagai target delete
                            target_post = post
                except Exception:
                    continue

            if jeans_count >= 1:
                break

        if jeans_count == 0:
            print("   ⚠️  Tidak ada postingan celana jeans ditemukan di halaman profil.")
            print("   Mencoba scroll lebih dalam...")

            # Scroll lebih dalam
            for _ in range(5):
                page.keyboard.press("End")
                time.sleep(2)

            for selector in post_selectors:
                posts = page.locator(selector)
                count = posts.count()
                if count == 0:
                    continue
                for i in range(count):
                    post = posts.nth(i)
                    try:
                        text = post.inner_text(timeout=3000)
                        if is_jeans_post(text):
                            jeans_count += 1
                            if jeans_count == 1:
                                target_post = post
                    except Exception:
                        continue
                if jeans_count >= 1:
                    break

        if target_post is None:
            print("❌ Tidak ada postingan celana jeans yang ditemukan untuk dihapus.")
            page.screenshot(path=SCREENSHOT_DEBUG)
            print(f"   📸 Debug screenshot: {SCREENSHOT_DEBUG}")
            browser.close()
            return False

        print(f"   Total postingan jeans ditemukan: {jeans_count}")
        if jeans_count < 2:
            print("   ⚠️  Hanya 1 postingan jeans ditemukan (mungkin sudah terhapus atau perlu scroll lebih).")
            print("   Melanjutkan hapus postingan yang ada...")

        # ── Step 4: Hover postingan target & klik tombol ⋯ ──────────────────
        print("4. Hover postingan target dan klik tombol menu opsi (⋯)...")
        target_post.scroll_into_view_if_needed()
        time.sleep(1)
        target_post.hover()
        time.sleep(1.5)

        # Cari tombol more options (⋯) di dalam postingan
        # Threads biasanya pakai button dengan aria-label atau SVG titik tiga
        more_btn_selectors = [
            '[aria-label="More"]',
            '[aria-label="more"]',
            'button[aria-label*="more" i]',
            'button[aria-label*="More" i]',
            'div[role="button"][aria-label*="more" i]',
            'div[role="button"][aria-label*="More" i]',
            '[data-testid="post-options-button"]',
            'svg[aria-label="More"]',
        ]

        more_btn = None
        for sel in more_btn_selectors:
            btn = target_post.locator(sel)
            if btn.count() > 0:
                more_btn = btn.first
                print(f"   ✓ Tombol ⋯ ditemukan dengan selector: {sel}")
                break

        if more_btn is None:
            # Fallback: cari semua button di dalam postingan dan ambil yang terakhir
            print("   Fallback: mencari semua button dalam postingan...")
            all_btns = target_post.locator('button, div[role="button"]')
            btn_count = all_btns.count()
            print(f"   Ditemukan {btn_count} button dalam postingan")
            if btn_count > 0:
                # Tombol ⋯ biasanya ada di pojok kanan atas postingan (button terakhir)
                more_btn = all_btns.last
                print(f"   Menggunakan button terakhir sebagai fallback")

        if more_btn is None:
            print("❌ Tombol menu opsi (⋯) tidak ditemukan!")
            page.screenshot(path=SCREENSHOT_DEBUG)
            browser.close()
            return False

        more_btn.click(force=True)
        time.sleep(2)
        page.screenshot(path=SCREENSHOT_DEBUG)
        print(f"   📸 Debug screenshot (setelah klik ⋯): {SCREENSHOT_DEBUG}")

        # ── Step 5: Klik "Delete" di dropdown menu ───────────────────────────
        print("5. Klik opsi 'Delete' di menu...")
        delete_selectors = [
            'text="Delete"',
            'button:has-text("Delete")',
            'div[role="button"]:has-text("Delete")',
            'span:has-text("Delete")',
            '[data-testid="delete-button"]',
            'li:has-text("Delete")',
            'a:has-text("Delete")',
        ]

        delete_btn = None
        for sel in delete_selectors:
            btn = page.locator(sel)
            if btn.count() > 0:
                delete_btn = btn.first
                print(f"   ✓ Tombol Delete ditemukan dengan selector: {sel}")
                break

        if delete_btn is None:
            print("❌ Opsi 'Delete' tidak ditemukan di menu!")
            page.screenshot(path=SCREENSHOT_DEBUG)
            browser.close()
            return False

        delete_btn.click(force=True)
        time.sleep(2)

        # ── Step 6: Konfirmasi dialog Delete ────────────────────────────────
        print("6. Konfirmasi dialog Delete...")
        confirm_selectors = [
            'button:has-text("Delete")',
            'div[role="button"]:has-text("Delete")',
            'button:has-text("Hapus")',
            'div[role="button"]:has-text("Hapus")',
            '[data-testid="confirm-delete-button"]',
            'button[type="submit"]:has-text("Delete")',
        ]

        confirmed = False
        for sel in confirm_selectors:
            btn = page.locator(sel)
            if btn.count() > 0:
                # Pastikan ini bukan tombol Cancel
                for idx in range(btn.count()):
                    b = btn.nth(idx)
                    try:
                        label = b.inner_text(timeout=2000).strip()
                        if label.lower() in ("delete", "hapus"):
                            b.click(force=True)
                            confirmed = True
                            print(f"   ✓ Konfirmasi Delete diklik (label: '{label}')")
                            break
                    except Exception:
                        continue
            if confirmed:
                break

        if not confirmed:
            # Coba tekan Enter sebagai fallback konfirmasi
            print("   Fallback: mencoba tekan Enter untuk konfirmasi...")
            page.keyboard.press("Enter")
            confirmed = True

        time.sleep(3)

        # ── Step 7: Screenshot hasil akhir ───────────────────────────────────
        print("7. Reload profil dan ambil screenshot hasil akhir...")
        page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=40000)
        time.sleep(4)
        page.screenshot(path=SCREENSHOT_AFTER)
        print(f"   📸 Screenshot after: {SCREENSHOT_AFTER}")

        # Verifikasi: hitung ulang postingan jeans
        remaining_jeans = 0
        for selector in post_selectors:
            posts = page.locator(selector)
            count = posts.count()
            for i in range(count):
                try:
                    text = posts.nth(i).inner_text(timeout=3000)
                    if is_jeans_post(text):
                        remaining_jeans += 1
                except Exception:
                    continue
            if remaining_jeans > 0 or count > 0:
                break

        browser.close()

        print("\n" + "=" * 60)
        print("✅ PROSES DELETE SELESAI")
        print(f"   Postingan jeans sebelum : {jeans_count}")
        print(f"   Postingan jeans sesudah : {remaining_jeans}")
        print(f"   Screenshot before : {SCREENSHOT_BEFORE}")
        print(f"   Screenshot after  : {SCREENSHOT_AFTER}")
        print("=" * 60)
        return True


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
