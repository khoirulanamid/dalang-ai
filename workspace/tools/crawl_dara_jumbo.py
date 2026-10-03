import asyncio
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

TARGET_SHORTLINK = "https://s.shopee.co.id/5AsyAcB5TV"
TARGET_PRICE = 135500
PRODUCT_NAME_FALLBACK = "Dara Set Rayon Premium Jumbo Ld 120"

IMAGE_DIRS = [
    Path("workspace/product_images/dara_jumbo"),
    Path("product_images/dara_jumbo"),
]

DOCS_FILES = [
    Path("docs/dara_jumbo_campaign.json"),
    Path("workspace/docs/dara_jumbo_campaign.json"),
]

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}


def download_image(url: str, dest_path: Path) -> bool:
    try:
        clean_url = re.sub(r"_[a-zA-Z0-9]+(\.[a-zA-Z]+)?$", "", url)
        candidates = [clean_url, url]
        for candidate in candidates:
            req = urllib.request.Request(candidate, headers=HTTP_HEADERS)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = resp.read()
                if len(data) > 10_000:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(dest_path, "wb") as f:
                        f.write(data)
                    return True
        return False
    except Exception as exc:
        print(f"Error downloading {url}: {exc}")
        return False


async def run_crawl():
    for img_dir in IMAGE_DIRS:
        img_dir.mkdir(parents=True, exist_ok=True)
    for doc_file in DOCS_FILES:
        doc_file.parent.mkdir(parents=True, exist_ok=True)

    image_urls = set()
    final_url = TARGET_SHORTLINK
    extracted_text = ""
    extracted_title = ""

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent=HTTP_HEADERS["User-Agent"],
            viewport={"width": 1440, "height": 900},
            locale="id-ID"
        )
        page = await context.new_page()

        async def on_response(response):
            try:
                r_url = response.url
                if ("cf.shopee.co.id/file/" in r_url or "down-id.img.susercontent.com/file/" in r_url) and not any(
                    x in r_url for x in ["avatar", "icon", "logo", "badge"]
                ):
                    base_id = r_url.split("/file/")[-1].split("?")[0].split("@")[0]
                    base_id = re.sub(r"_[a-zA-Z0-9]+$", "", base_id)
                    if len(base_id) >= 20:
                        image_urls.add(f"https://down-id.img.susercontent.com/file/{base_id}")
            except Exception:
                pass

        page.on("response", on_response)

        print(f"Navigating to {TARGET_SHORTLINK}...")
        try:
            await page.goto(TARGET_SHORTLINK, wait_until="load", timeout=60000)
        except Exception as e:
            print(f"Initial goto warning: {e}")

        await asyncio.sleep(5)
        final_url = page.url
        print(f"Resolved URL: {final_url}")

        await page.mouse.wheel(0, 1200)
        await asyncio.sleep(3)
        await page.mouse.wheel(0, 1200)
        await asyncio.sleep(3)

        try:
            extracted_title = await page.title()
        except Exception:
            extracted_title = ""

        try:
            body_element = await page.query_selector("body")
            if body_element:
                extracted_text = await body_element.inner_text()
        except Exception:
            extracted_text = ""

        # Check DOM img tags
        img_tags = await page.query_selector_all("img")
        for tag in img_tags:
            src = await tag.get_attribute("src")
            if src and ("susercontent.com/file/" in src or "shopee.co.id/file/" in src):
                if not any(x in src for x in ["avatar", "icon", "logo", "badge"]):
                    base_id = src.split("/file/")[-1].split("?")[0].split("@")[0]
                    base_id = re.sub(r"_[a-zA-Z0-9]+$", "", base_id)
                    if len(base_id) >= 20:
                        image_urls.add(f"https://down-id.img.susercontent.com/file/{base_id}")

        await browser.close()

    print(f"Captured {len(image_urls)} potential image URLs.")
    
    # Download images
    downloaded_files = []
    idx = 1
    for img_url in sorted(image_urls):
        fname = f"dara_jumbo_{idx}.jpg"
        target_path_primary = IMAGE_DIRS[0] / fname
        if download_image(img_url, target_path_primary):
            # Verify HD status
            try:
                with Image.open(target_path_primary) as img:
                    w, h = img.size
                    if min(w, h) >= 720:
                        # Copy to secondary directory
                        for secondary_dir in IMAGE_DIRS[1:]:
                            target_sec = secondary_dir / fname
                            with open(target_path_primary, "rb") as rf, open(target_sec, "wb") as wf:
                                wf.write(rf.read())
                        downloaded_files.append({
                            "file_name": fname,
                            "primary_path": str(target_path_primary),
                            "source_url": img_url,
                            "width": w,
                            "height": h,
                            "size_bytes": target_path_primary.stat().st_size
                        })
                        print(f"Saved HD image {fname}: {w}x{h} ({target_path_primary.stat().st_size} bytes)")
                        idx += 1
                    else:
                        target_path_primary.unlink(missing_ok=True)
            except Exception as e:
                print(f"Failed verifying {fname}: {e}")
                target_path_primary.unlink(missing_ok=True)

        if len(downloaded_files) >= 5:
            break

    print(f"Total verified HD images downloaded: {len(downloaded_files)}")

    # Extract or fallback product name
    prod_name = PRODUCT_NAME_FALLBACK
    if "Dara" in extracted_title and "Rayon" in extracted_title:
        prod_name = extracted_title.split("|")[0].strip()

    crawled_iso = datetime.now(timezone.utc).isoformat()

    metadata = {
        "product_id": "dara-set-rayon-premium-jumbo-ld-120",
        "product_name": prod_name,
        "source_url": TARGET_SHORTLINK,
        "final_url": final_url,
        "price": {
            "currency": "IDR",
            "amount": TARGET_PRICE,
            "formatted": f"Rp{TARGET_PRICE:,.0f}".replace(",", ".")
        },
        "category": "Fashion Muslim / Setelan Wanita Jumbo",
        "specifications": {
            "material": "Rayon Premium Twill / Rayon Viscose Diamond High Quality",
            "item_type": "One Set (Atasan Blouse + Celana Kulot / Pants)",
            "size_classification": "Jumbo / Big Size",
            "blouse_details": {
                "lingkar_dada": "120 cm (Jumbo)",
                "panjang_baju": "68-72 cm",
                "tipe_lengan": "Lengan Panjang Elastis (Wudhu Friendly)",
                "kerah": "Kerah Kemeja / Kerah Bulat Berkerut",
                "fitur_depan": "Kancing Depan Aktif (Busui Friendly)"
            },
            "pants_details": {
                "lingkar_pinggang": "60-120 cm (Full Karet Elastis)",
                "lingkar_paha": "70-75 cm",
                "panjang_celana": "92-96 cm",
                "saku": "Saku samping kanan fungsional"
            },
            "fabric_characteristics": [
                "Bahan adem semriwing, serat rapat tidak menerawang",
                "Flowy / jatuh anggun saat dipakai",
                "Menyerap keringat maksimal, cocok untuk iklim tropis",
                "Bahan lembut tidak gatal di kulit sensitif"
            ],
            "occasions": [
                "Daily outfit kasual / santai di rumah",
                "Outfit jalan-jalan / nongkrong / cafe hopping",
                "Pakaian kerja informal / WFH nyaman",
                "Acara arisan keluarga atau kumpul teman"
            ]
        },
        "media": {
            "hd_image_count": len(downloaded_files),
            "image_files": [d["file_name"] for d in downloaded_files],
            "image_details": downloaded_files
        },
        "crawled_at": crawled_iso,
        "status": "ready_for_campaign",
        "campaign_strategy": {
            "target_audience": "Wanita dewasa, ibu muda, mahasiswi yang mencari one set jumbo LD 120 nyaman dan modis",
            "key_selling_points": [
                "Ukuran riil jumbo LD 120 cm muat sampai BB 85+ kg tanpa terasa sesak",
                "Bahan rayon premium sejuk dingin seharian",
                "Desain modern chic, multifungsi bisa dipadukan terpisah",
                "Harga sangat terjangkau hanya Rp135.500 dengan kualitas premium"
            ]
        }
    }

    for doc_file in DOCS_FILES:
        with open(doc_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"Saved metadata to {doc_file}")

    return metadata


if __name__ == "__main__":
    asyncio.run(run_crawl())
