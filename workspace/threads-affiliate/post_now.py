"""
Script posting langsung ke Threads - Opsi 1 (konten jujur/lucu)
Produk: Tumbler 1 Liter tahan panas dingin
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from threads_poster.poster import ThreadsPoster
from threads_poster.dedup import DedupChecker

COOKIES_PATH = Path.home() / ".threads_poster/cookies/session.json"
HISTORY_PATH = Path("data/post_history.json")

POST_1 = "nemu botol 1 liter yang katanya tahan dingin 24 jam. kalo beneran, es teh manis gw bakal bertahan lebih lama dari hubungan kalian 🗿"

POST_2 = """fitur yang bikin menarik:
• tahan dingin 24 jam, panas 12 jam
• 1 liter (ga perlu bolak-balik isi)
• bebas BPA & anti bocor
• pegangannya pake Silitech jadi ga licin"""

POST_3 = """buat yang penasaran atau lagi cari tumbler gede, cek sendiri di sini:
https://s.shopee.co.id/LngnAwCfq"""

AFFILIATE_LINK = "https://s.shopee.co.id/LngnAwCfq"
PRODUCT = "Tumbler 1 Liter Tahan Panas Dingin"
CATEGORY = "gadget"
HOOK_STYLE = "storytelling"

def main():
    # Cek cookie ada
    if not COOKIES_PATH.exists():
        print(f"ERROR: Cookie tidak ditemukan di {COOKIES_PATH}")
        sys.exit(2)

    # Cek dedup
    dedup = DedupChecker(HISTORY_PATH)
    ok, reason = dedup.check(AFFILIATE_LINK, HOOK_STYLE, POST_1, CATEGORY)
    if not ok:
        print(f"DEDUP REJECTED: {reason}")
        sys.exit(3)

    print("=== KONTEN YANG AKAN DIPOSTING ===")
    print(f"\nPOST 1:\n{POST_1}")
    print(f"\nPOST 2:\n{POST_2}")
    print(f"\nPOST 3:\n{POST_3}")
    print(f"\nLink: {AFFILIATE_LINK}")
    print("\n=== MULAI POSTING ===")

    poster = ThreadsPoster(
        cookies_path=COOKIES_PATH,
        headless=True,
        timeout_ms=45000,
    )

    result = poster.post(
        product=PRODUCT,
        affiliate_link=AFFILIATE_LINK,
        hook_text=POST_1,
        post_2=POST_2,
        post_3=POST_3,
        hook_category=HOOK_STYLE,
        category=CATEGORY,
        username="rizki_mubarok",
    )

    if result.success:
        print(f"\n✅ BERHASIL POSTING!")
        print(f"Post URL: {result.post_url}")
        # Catat ke history
        dedup.record({
            "date": result.timestamp,
            "product": PRODUCT,
            "category": CATEGORY,
            "hook_category": HOOK_STYLE,
            "hook_text": POST_1,
            "affiliate_link": AFFILIATE_LINK,
            "post_url": result.post_url,
        })
        print("History diupdate.")
        sys.exit(0)
    else:
        print(f"\n❌ GAGAL: {result.error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
