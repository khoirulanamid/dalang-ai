#!/usr/bin/env python3
"""
tools/shopee_media_extractor.py

Modul resmi tim Dalang-AI untuk ekstraksi gambar produk HD dan metadata dari link Shopee (Shortlink / Longlink).
Dibangun agar tim tidak perlu menulis script crawler berulang-ulang dari nol.
Efisiensi: 1 round-trip eksekusi, selesai dalam hitungan detik.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

def clean_cdn_url(raw_url: str) -> str:
    """Bersihkan thumbnail modifier Shopee agar mendapat resolusi HD asli."""
    clean = raw_url.split("?")[0]
    clean = re.sub(r"_[a-z0-9]+$", "", clean)
    return clean

def extract_shopee_product(url: str, output_dir: str, max_images: int = 5) -> dict:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    result = {
        "source_url": url,
        "final_url": None,
        "title": None,
        "images": [],
        "success": False,
        "error": None
    }
    
    captured_cdn_images = set()

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
        ctx.add_cookies([
            {"name": "shopee_locale", "value": "id", "domain": ".shopee.co.id", "path": "/"}
        ])

        def handle_request(req):
            u = req.url
            if "susercontent.com/file/" in u:
                cleaned = clean_cdn_url(u)
                captured_cdn_images.add(cleaned)

        page = ctx.new_page()
        page.on("request", handle_request)

        try:
            # 1. Navigasi awal
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            time.sleep(5)
            
            # Jika terlempar ke URL mobile __mobile__=1, bersihkan ke URL desktop
            cur_url = page.url
            clean_desk_url = cur_url.replace("&__mobile__=1", "").replace("?__mobile__=1", "")
            if clean_desk_url != cur_url:
                page.goto(clean_desk_url, wait_until="networkidle", timeout=35000)
                time.sleep(4)

            result["final_url"] = page.url
            result["title"] = page.title()

            # Ambil juga semua gambar dari tag img di DOM
            dom_imgs = page.eval_on_selector_all("img", "imgs => imgs.map(i => i.src)")
            for src in dom_imgs:
                if "susercontent.com/file/" in src:
                    captured_cdn_images.add(clean_cdn_url(src))

            # 2. Filter & Download gambar HD
            downloaded = []
            idx = 1
            for img_url in list(captured_cdn_images):
                if idx > max_images:
                    break
                target_file = out_path / f"product_image_{idx}.jpg"
                try:
                    req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=12) as resp, open(target_file, "wb") as f:
                        data = resp.read()
                        # Hanya simpan gambar nyata (>10KB, hindari icon tracking)
                        if len(data) > 10240:
                            f.write(data)
                            downloaded.append({
                                "index": idx,
                                "file_path": str(target_file),
                                "url": img_url,
                                "bytes": len(data)
                            })
                            idx += 1
                except Exception as e:
                    pass

            result["images"] = downloaded
            result["success"] = len(downloaded) > 0
            if not result["success"]:
                result["error"] = "Tidak ada gambar HD yang berhasil diunduh (>10KB)"

        except Exception as e:
            result["error"] = str(e)
        finally:
            browser.close()

    return result

def main():
    parser = argparse.ArgumentParser(description="Dalang-AI Shopee Media Extractor Tool")
    parser.add_argument("url", help="URL produk atau shortlink Shopee")
    parser.add_argument("--out", "-o", default="workspace/product_images", help="Direktori penyimpanan gambar")
    parser.add_argument("--max", "-m", type=int, default=5, help="Jumlah maksimal gambar yang diunduh")
    
    args = parser.parse_args()
    res = extract_shopee_product(args.url, args.out, args.max)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["success"] else 1)

if __name__ == "__main__":
    main()
