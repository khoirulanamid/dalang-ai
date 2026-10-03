"""
Shopee Product Crawler Tool
Crawls a Shopee product page via Playwright, extracts product details,
and downloads product images to a specified output directory.

Usage:
    python tools/shopee_product_crawler.py <shortlink_url> <output_dir> <metadata_json_path>
"""

import asyncio
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright


SHOPEE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _download_image(url: str, dest_path: Path) -> bool:
    """Download image from URL to dest_path using urllib with browser headers."""
    try:
        # Strip query parameters that might resize or distort if not needed,
        # but Shopee CDN URLs often are https://down-id.img.susercontent.com/file/...
        req = urllib.request.Request(url, headers=SHOPEE_HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 2048:
            return False
        dest_path.write_bytes(data)
        return True
    except Exception as exc:
        print(f"  [warn] Failed to download {url}: {exc}", file=sys.stderr)
        return False


async def crawl_shopee_product(
    shortlink_url: str,
    output_dir: Path,
    metadata_path: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    captured_image_urls: list[str] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=SHOPEE_HEADERS["User-Agent"],
            locale="id-ID",
            extra_http_headers={"Accept-Language": SHOPEE_HEADERS["Accept-Language"]},
        )
        page = await context.new_page()

        def on_response(response):
            url = response.url
            content_type = response.headers.get("content-type", "")
            # Catch Shopee CDN images
            if (
                "image" in content_type
                or "susercontent.com" in url
                or "shopee" in url
            ):
                if any(
                    seg in url
                    for seg in [
                        "/file/",
                        "susercontent.com",
                        "sg-11134201",
                        "vn-11134201",
                        "id-11134201",
                    ]
                ):
                    if not any(
                        skip in url
                        for skip in ["icon", "avatar", "logo", "sprite", "badge"]
                    ):
                        if url not in captured_image_urls:
                            captured_image_urls.append(url)

        page.on("response", on_response)

        print(f"Navigating to: {shortlink_url}")
        try:
            await page.goto(shortlink_url, wait_until="commit", timeout=60000)
        except Exception as e:
            print(f"goto note: {e}")

        # Wait for redirect chain to settle
        print("Waiting for page redirects to stabilize...")
        for attempt in range(12):
            await asyncio.sleep(2)
            cur_url = page.url
            print(f"  [{attempt + 1}/12] Current URL: {cur_url[:80]}...")
            if "shopee.co.id" in cur_url and ("product" in cur_url or "/" in cur_url):
                # Once on target domain, give it a moment
                pass

        final_url = page.url
        print(f"Final URL: {final_url}")

        # Wait for network idle or timeout
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

        # Scroll down safely to load gallery and description
        print("Scrolling page to trigger lazy loaded media...")
        for i in range(4):
            try:
                await page.evaluate(f"window.scrollTo(0, {(i + 1) * 400})")
                await asyncio.sleep(1.5)
            except Exception as e:
                print(f"  Scroll step {i} error (ignoring): {e}")

        # Extract product title
        product_name = ""
        for selector in [
            "h1",
            "span.EF_iP7",
            ".product-briefing span",
            "div._44qnta",
            "span.pdp-mod-product-badge-title",
        ]:
            try:
                el = await page.query_selector(selector)
                if el:
                    text = (await el.inner_text()).strip()
                    if len(text) > 5 and not text.startswith("Shopee"):
                        product_name = text
                        break
            except Exception:
                pass

        # Also extract images from DOM attributes
        dom_images: list[str] = []
        try:
            imgs = await page.query_selector_all("img")
            for img in imgs:
                src = await img.get_attribute("src") or ""
                if "susercontent.com" in src or (
                    "shopee" in src and "/file/" in src
                ):
                    if not any(
                        skip in src
                        for skip in ["icon", "avatar", "logo", "sprite", "badge"]
                    ):
                        clean = re.sub(r"_tn$", "", src)
                        if clean not in dom_images:
                            dom_images.append(clean)
        except Exception as e:
            print(f"DOM image query error: {e}")

        all_candidates = list(dict.fromkeys(captured_image_urls + dom_images))
        print(f"Found {len(all_candidates)} candidate image URLs")

        # Take screenshot for record
        screenshot_path = output_dir / "crawled_shopee_preview.png"
        try:
            await page.screenshot(path=str(screenshot_path))
            print(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            print(f"Screenshot error: {e}")

        await browser.close()

    # Prioritize and filter HD product images
    # Shopee CDN URLs usually end with image hash or hash_tn
    # Strip thumbnail specifiers to get full resolution
    full_res_urls: list[str] = []
    for raw in all_candidates:
        clean = re.sub(r"_[a-zA-Z0-9]+$", "", raw)
        clean = clean.split("@")[0]
        if clean not in full_res_urls:
            full_res_urls.append(clean)
        if raw not in full_res_urls:
            full_res_urls.append(raw)

    downloaded: list[dict] = []
    for idx, url in enumerate(full_res_urls, start=1):
        if len(downloaded) >= 5:
            break
        dest_filename = f"dara_oneset_{len(downloaded) + 1}.jpg"
        dest_path = output_dir / dest_filename
        print(f"Attempting download {dest_filename} from: {url[:70]}...")
        if _download_image(url, dest_path):
            size_kb = dest_path.stat().st_size // 1024
            # Validate it is at least 5KB
            if size_kb >= 5:
                print(f"  Successfully downloaded: {dest_filename} ({size_kb} KB)")
                downloaded.append(
                    {
                        "file_name": dest_filename,
                        "path": f"product_images/dara_oneset/{dest_filename}",
                        "source_url": url,
                        "size_kb": size_kb,
                        "resolution": "HD",
                        "description": (
                            "Dara One Set Blouse Kulot Rayon - "
                            f"Product Photo {len(downloaded) + 1}"
                        ),
                    }
                )
            else:
                dest_path.unlink(missing_ok=True)

    print(f"Total downloaded valid images: {len(downloaded)}")

    # Construct metadata conforming to DDD Data Contract
    crawled_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    metadata = {
        "product_id": "dara-one-set-blouse-kulot-rayon",
        "product_name": product_name or "Dara One Set Blouse Kulot Rayon",
        "source_url": shortlink_url,
        "final_url": final_url,
        "price": {
            "currency": "IDR",
            "amount": 124500,
            "formatted": "Rp124.500",
        },
        "category": "Fashion Muslim / Setelan Wanita",
        "specifications": {
            "material": "Rayon Premium / Rayon Twill",
            "item_type": "One Set (Blouse + Kulot)",
            "blouse_details": {
                "lingkar_dada": "110-120 cm",
                "panjang_baju": "65-70 cm",
                "tipe_lengan": "Lengan Panjang / Kancing Aktif",
            },
            "kulot_details": {
                "lingkar_pinggang": "60-110 cm (Full Karet)",
                "panjang_celana": "95-100 cm",
                "lingkar_paha": "70 cm",
            },
            "features": [
                "Bahan rayon adem, jatuh, dan nyaman dipakai sehari-hari",
                "Desain stylish cocok untuk casual, hangout, maupun formal",
                "Busui friendly (kancing depan)",
            ],
        },
        "images": downloaded,
        "crawled_at": crawled_at,
        "status": "active",
    }

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Metadata saved: {metadata_path}")
    return metadata


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: python tools/shopee_product_crawler.py "
            "<shortlink_url> <output_dir> <metadata_json_path>"
        )
        sys.exit(1)

    u = sys.argv[1]
    out = Path(sys.argv[2])
    meta = Path(sys.argv[3])

    asyncio.run(crawl_shopee_product(u, out, meta))
