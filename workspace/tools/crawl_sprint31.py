import asyncio
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import httpx
from playwright.async_api import async_playwright

SHORTLINK = "https://s.shopee.co.id/gQbH58w3m"
IMAGE_DIR_1 = Path("product_images/sprint31")
IMAGE_DIR_2 = Path("workspace/product_images/sprint31")
DOCS_PATH = Path("docs/sprint31_campaign.json")

async def crawl_shopee(shortlink: str):
    IMAGE_DIR_1.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR_2.mkdir(parents=True, exist_ok=True)
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)

    captured_api_data: Dict[str, Any] = {}
    network_images: set = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="id-ID",
        )

        page = await context.new_page()

        async def handle_response(response):
            nonlocal captured_api_data
            url = response.url
            if ("cf.shopee.co.id/file/" in url or "down-id.img.susercontent.com/file/" in url) and not any(x in url for x in ["avatar", "badge", "icon", "rating", "seller", "feedback"]):
                clean_img = url.split("?")[0].split("_tn")[0].split("_cov")[0]
                clean_img = re.sub(r'_\d+x\d+.*$', '', clean_img)
                network_images.add(clean_img)

            if any(endpoint in url for endpoint in ["/api/v4/item/get", "/api/v2/item/get", "/api/v4/pdp/get_item", "/api/v4/pdp/get_pc"]):
                try:
                    data = await response.json()
                    captured_api_data = data
                except Exception:
                    pass

        page.on("response", handle_response)

        print(f"Navigating to {shortlink}...")
        try:
            await page.goto(shortlink, wait_until="domcontentloaded", timeout=40000)
        except Exception as e:
            print(f"Goto warning: {e}")

        # Wait for redirects and dynamic render
        print("Waiting for page hydration...")
        await page.wait_for_timeout(8000)

        final_url = page.url
        page_title = await page.title()
        print(f"Current URL: {final_url}")
        print(f"Page title: {page_title}")

        # If on mobile page, try switching to desktop or let mobile page render
        # Let's scroll down to trigger lazy loading
        for _ in range(6):
            await page.mouse.wheel(0, 700)
            await page.wait_for_timeout(1000)

        # Query DOM title
        dom_title = ""
        for sel in ["h1", ".attP6y", ".vR6W_F", ".qaNIZv", "div._44qnta", "div.pdp-mod-product-badge-title", "[data-sqi='title']"]:
            el = await page.query_selector(sel)
            if el:
                txt = (await el.inner_text()).strip()
                if txt and len(txt) > 5:
                    dom_title = txt
                    break

        if not dom_title and page_title:
            dom_title = page_title.split("|")[0].strip()

        # Query DOM price
        dom_price = ""
        for sel in [".pqTWkA", ".Y3D39n", "div._3n5zSv", "div.pdp-price", ".product-price", "[class*='price']"]:
            el = await page.query_selector(sel)
            if el:
                txt = (await el.inner_text()).strip()
                if "rp" in txt.lower():
                    dom_price = txt
                    break

        # Query DOM specs
        specs: Dict[str, str] = {}
        spec_elements = await page.query_selector_all("div.dR8BYJ, div._0Z3Idn, div.product-detail-item, div.k-Fdrf, div[class*='attribute'], .pdp-product-detail tr, .pdp-product-detail div")
        for row in spec_elements:
            try:
                text = (await row.inner_text()).strip()
                if "\n" in text:
                    parts = [p.strip() for p in text.split("\n") if p.strip()]
                    if len(parts) >= 2:
                        specs[parts[0]] = ": ".join(parts[1:])
            except Exception:
                pass

        # Query DOM description
        description = ""
        for sel in ["div.f7a5wb", "div._2u0cpt", "div.product-detail-description", "div[class*='description']", ".pdp-product-desc"]:
            el = await page.query_selector(sel)
            if el:
                txt = (await el.inner_text()).strip()
                if len(txt) > 20:
                    description = txt
                    break

        # Query all images in DOM
        img_elements = await page.query_selector_all("img")
        for el in img_elements:
            src = await el.get_attribute("src")
            if src and any(d in src for d in ["susercontent.com", "shopeemobile.com", "cf.shopee"]):
                if not any(x in src for x in ["avatar", "badge", "icon", "rating", "seller", "feedback"]):
                    clean_img = src.split("?")[0].split("_tn")[0].split("_cov")[0]
                    clean_img = re.sub(r'_\d+x\d+.*$', '', clean_img)
                    network_images.add(clean_img)

        # Screenshot for debugging
        await page.screenshot(path="crawl_sprint31_debug.png", full_page=True)
        html_content = await page.content()
        with open("crawl_sprint31_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        await browser.close()

    print(f"Captured API data present: {bool(captured_api_data)}")
    print(f"Captured raw image URLs: {len(network_images)}")
    print(f"DOM Title: {dom_title}")
    print(f"DOM Price: {dom_price}")

    item_data = captured_api_data.get("data", {}) if "data" in captured_api_data else captured_api_data.get("item", {})
    if not item_data and isinstance(captured_api_data, dict):
        item_data = captured_api_data

    # Product Name
    product_name = item_data.get("name") or dom_title or "Shopee Product"

    # Price handling
    raw_price = item_data.get("price") or item_data.get("price_min") or 0
    if raw_price > 10000000:
        price_num = float(raw_price) / 100000.0
    elif raw_price > 0:
        price_num = float(raw_price)
    else:
        nums = re.findall(r'[\d\.]+', dom_price.replace(".", ""))
        price_num = float(nums[0]) if nums else 0.0

    price_formatted = f"Rp{int(price_num):,}".replace(",", ".") if price_num else dom_price

    # Attributes / specs
    for attr in item_data.get("attributes", []):
        if isinstance(attr, dict):
            k = attr.get("name") or attr.get("key", "")
            v = attr.get("value") or attr.get("val", "")
            if k and v:
                specs[k] = str(v)

    # Images
    hd_image_urls = []
    for img_id in item_data.get("images", []):
        if img_id:
            hd_image_urls.append(f"https://down-id.img.susercontent.com/file/{img_id}")

    for img_url in network_images:
        if img_url not in hd_image_urls:
            hd_image_urls.append(img_url)

    print(f"Total candidate HD images: {len(hd_image_urls)}")

    # Download images
    downloaded_files = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://shopee.co.id/",
    }

    async with httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True) as client:
        count = 1
        for url in hd_image_urls:
            try:
                resp = await client.get(url)
                if resp.status_code == 200 and len(resp.content) > 10000:  # Minimum 10KB
                    filename = f"sprint31_product_{count:02d}.jpg"
                    p1 = IMAGE_DIR_1 / filename
                    p2 = IMAGE_DIR_2 / filename
                    p1.write_bytes(resp.content)
                    p2.write_bytes(resp.content)
                    downloaded_files.append({
                        "filename": filename,
                        "relative_path": str(p1),
                        "size_bytes": len(resp.content),
                        "source_url": url,
                    })
                    print(f"Downloaded {filename} ({len(resp.content)} bytes)")
                    count += 1
                    if count > 8:
                        break
            except Exception as e:
                print(f"Error downloading {url}: {e}")

    now_utc = datetime.now(timezone.utc).isoformat()

    metadata = {
        "campaign_id": "sprint31",
        "task_id": "T-3101",
        "source_shortlink": shortlink,
        "final_url": final_url,
        "crawled_at": now_utc,
        "product_name": product_name,
        "price": {
            "currency": "IDR",
            "amount": price_num,
            "formatted": price_formatted,
        },
        "price_formatted": price_formatted,
        "currency": "IDR",
        "description": description or item_data.get("description", ""),
        "specifications": specs,
        "category": item_data.get("categories", []),
        "images": [item["filename"] for item in downloaded_files],
        "image_details": downloaded_files,
        "status": "crawled",
        "metadata_version": "1.0.0"
    }

    with open(DOCS_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Successfully wrote metadata to {DOCS_PATH}")
    return metadata

if __name__ == "__main__":
    asyncio.run(crawl_shopee(SHORTLINK))
