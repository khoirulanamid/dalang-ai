import asyncio
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse
import httpx
from playwright.async_api import async_playwright

SHORTLINK = "https://s.shopee.co.id/8AWbWHUOPx"
OUTPUT_DIRS = [
    Path("/root/storage/projects/dalang-ai/workspace/product_images/sprint29"),
    Path("/root/storage/projects/dalang-ai/workspace/workspace/product_images/sprint29")
]
METADATA_PATH = Path("/root/storage/projects/dalang-ai/workspace/docs/sprint29_campaign.json")

async def extract_shopee_product():
    for d in OUTPUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    extracted_data = {
        "shortlink": SHORTLINK,
        "final_url": None,
        "title": None,
        "price": None,
        "price_min": None,
        "price_max": None,
        "currency": "IDR",
        "specifications": {},
        "description": "",
        "images": [],
        "api_raw_item": None
    }

    captured_api_data = {}
    captured_image_urls = set()

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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="id-ID"
        )

        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            try:
                if "api/v4/item/get" in url or "api/v4/pdp/get_pc" in url or "api/v2/item/get" in url:
                    data = await response.json()
                    captured_api_data["pdp_api"] = data
                elif "img.susercontent.com" in url or "cf.shopee.co.id/file" in url:
                    captured_image_urls.add(url)
            except Exception:
                pass

        page.on("response", handle_response)

        print(f"Navigating to shortlink: {SHORTLINK}")
        await page.goto(SHORTLINK, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)

        extracted_data["final_url"] = page.url
        print(f"Final URL: {page.url}")

        # Try to extract from page title / DOM
        page_title = await page.title()
        print(f"Page title: {page_title}")

        # Let's inspect __NEXT_DATA__ or __INITIAL_STATE__
        script_data = await page.evaluate("""() => {
            let res = {};
            if (window.__INITIAL_STATE__) res.initial_state = window.__INITIAL_STATE__;
            if (window.__NEXT_DATA__) res.next_data = window.__NEXT_DATA__;
            return res;
        }""")

        # Extract DOM elements
        # Shopee product title often in h1 or specific class
        dom_title = await page.evaluate("""() => {
            const h1 = document.querySelector('h1') || document.querySelector('._44qnta') || document.querySelector('.WB8f5Q');
            return h1 ? h1.innerText.trim() : null;
        }""")
        if dom_title:
            extracted_data["title"] = dom_title
        elif page_title:
            extracted_data["title"] = page_title.split("|")[0].strip()

        # Extract DOM price
        dom_price = await page.evaluate("""() => {
            const el = document.querySelector('.pqTWkA') || document.querySelector('.IZIdqB') || document.querySelector('.G27fpf');
            return el ? el.innerText.trim() : null;
        }""")
        if dom_price:
            extracted_data["price"] = dom_price

        # Extract DOM specifications & description
        dom_details = await page.evaluate("""() => {
            const specs = {};
            const specRows = document.querySelectorAll('.G6u6EG, .e89t_Q, .f7u3XF');
            specRows.forEach(row => {
                const label = row.querySelector('label, ._0b72j6, .O94TvD');
                const val = row.querySelector('div, a, span, ._1vGqVv');
                if (label && val) {
                    specs[label.innerText.trim()] = val.innerText.trim();
                }
            });
            const descEl = document.querySelector('.f8daCx') || document.querySelector('.irIKVC') || document.querySelector('._07m0zy');
            const desc = descEl ? descEl.innerText.trim() : '';
            return { specs, desc };
        }""")
        if dom_details.get("specs"):
            extracted_data["specifications"].update(dom_details["specs"])
        if dom_details.get("desc"):
            extracted_data["description"] = dom_details["desc"]

        # Intercept DOM images
        dom_images = await page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll('img')).map(i => i.src);
            return imgs.filter(src => src && (src.includes('susercontent.com') || src.includes('shopee.co.id')));
        }""")
        for img in dom_images:
            captured_image_urls.add(img)

        # Check captured_api_data
        if "pdp_api" in captured_api_data:
            extracted_data["api_raw_item"] = captured_api_data["pdp_api"]
            pdp = captured_api_data["pdp_api"].get("data", {})
            if isinstance(pdp, dict):
                item = pdp.get("item", pdp)
                if "name" in item and not extracted_data["title"]:
                    extracted_data["title"] = item["name"]
                if "description" in item and not extracted_data["description"]:
                    extracted_data["description"] = item["description"]
                if "images" in item:
                    for img_hash in item["images"]:
                        full_img_url = f"https://down-id.img.susercontent.com/file/{img_hash}"
                        captured_image_urls.add(full_img_url)

        # Take screenshot for debugging/verification
        await page.screenshot(path="tools/shopee_crawl_preview.png")
        await browser.close()

    print(f"Captured {len(captured_image_urls)} potential image URLs")
    return extracted_data, list(captured_image_urls), captured_api_data

if __name__ == "__main__":
    data, images, raw_api = asyncio.run(extract_shopee_product())
    print("DATA:")
    print(json.dumps({k: v for k, v in data.items() if k != "api_raw_item"}, indent=2))
    print(f"Sample images: {images[:5]}")
