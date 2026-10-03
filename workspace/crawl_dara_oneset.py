import asyncio
import json
import os
import re
import httpx
from playwright.async_api import async_playwright

URL = "https://s.shopee.co.id/3qNaOVRWrP"
IMG_DIR_1 = "workspace/product_images/dara_oneset"
IMG_DIR_2 = "product_images/dara_oneset"
DOCS_FILE = "docs/dara_oneset_campaign.json"

async def crawl():
    os.makedirs(IMG_DIR_1, exist_ok=True)
    os.makedirs(IMG_DIR_2, exist_ok=True)
    
    image_urls = set()
    product_data = {}
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        # Listen to responses to grab image URLs or API payloads
        async def handle_response(response):
            try:
                url = response.url
                if "cf.shopee.co.id/file/" in url or "down-id.img.susercontent.com/file/" in url:
                    # Filter out small icons/avatars if possible
                    image_urls.add(url)
            except Exception:
                pass

        page.on("response", handle_response)

        print(f"Navigating to {URL}...")
        try:
            await page.goto(URL, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"Navigation exception: {e}")
        
        await page.wait_for_timeout(5000)

        final_url = page.url
        title = await page.title()
        print(f"Final URL: {final_url}")
        print(f"Page Title: {title}")

        # Try to locate images on page
        img_elements = await page.query_selector_all("img")
        for img in img_elements:
            src = await img.get_attribute("src")
            if src and ("cf.shopee.co.id/file/" in src or "down-id.img.susercontent.com/file/" in src or "susercontent.com" in src):
                image_urls.add(src)

        print(f"Found {len(image_urls)} candidate image URLs")
        
        # Take a screenshot for debugging
        await page.screenshot(path="shopee_dara_page.png")
        
        # Extract product details
        page_content = await page.content()
        await browser.close()

    # Filter and download high resolution images
    downloaded_images = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    # Transform Shopee thumbnail URLs to HD (_tn or size suffix removal)
    valid_hd_urls = []
    for u in image_urls:
        # e.g., down-id.img.susercontent.com/file/id-11134207-..._tn or _xx
        # strip query params or size suffix
        clean_url = u.split("@")[0]
        clean_url = re.sub(r'_[a-z0-9]+$', '', clean_url)
        clean_url = clean_url.split("?")[0]
        if "avatar" not in clean_url and "icon" not in clean_url:
            valid_hd_urls.append(clean_url)

    valid_hd_urls = list(dict.fromkeys(valid_hd_urls))
    print(f"Valid HD URLs: {len(valid_hd_urls)}")

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        count = 1
        for u in valid_hd_urls:
            try:
                resp = await client.get(u)
                if resp.status_code == 200 and len(resp.content) > 15000:  # must be substantial image (>15KB)
                    filename = f"dara_oneset_{count}.jpg"
                    path1 = os.path.join(IMG_DIR_1, filename)
                    path2 = os.path.join(IMG_DIR_2, filename)
                    with open(path1, "wb") as f:
                        f.write(resp.content)
                    with open(path2, "wb") as f:
                        f.write(resp.content)
                    downloaded_images.append({
                        "filename": filename,
                        "path": path1,
                        "url": u,
                        "size_bytes": len(resp.content)
                    })
                    print(f"Downloaded {filename} ({len(resp.content)} bytes) from {u}")
                    count += 1
                    if count > 5:
                        break
            except Exception as e:
                print(f"Error downloading {u}: {e}")

    # Read existing campaign json or create metadata
    existing_meta = {}
    if os.path.exists(DOCS_FILE):
        try:
            with open(DOCS_FILE, "r", encoding="utf-8") as f:
                existing_meta = json.load(f)
        except Exception:
            pass

    metadata = {
        "task_id": "T-2401",
        "product_name": "Dara One Set Blouse Kulot Rayon",
        "shortlink": URL,
        "final_url": final_url,
        "price_formatted": "Rp124.500",
        "price_numeric": 124500,
        "currency": "IDR",
        "material": "Rayon",
        "category": "Fashion Muslim / One Set",
        "images": [img["filename"] for img in downloaded_images],
        "image_details": downloaded_images,
        "specifications": {
            "nama_produk": "Dara One Set Blouse Kulot Rayon",
            "harga": 124500,
            "harga_label": "Rp124.500",
            "bahan": "Rayon Premium / Rayon Twill",
            "potongan": "Blouse + Celana Kulot",
            "deskripsi": "Setelan Dara One Set Blouse Kulot Rayon dengan bahan adem, jatuh, dan nyaman untuk harian maupun semi-formal."
        }
    }
    
    # Merge existing metadata if present
    if existing_meta:
        for k, v in existing_meta.items():
            if k not in metadata:
                metadata[k] = v

    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Updated {DOCS_FILE} successfully.")
    print(f"Total downloaded images: {len(downloaded_images)}")

if __name__ == "__main__":
    asyncio.run(crawl())
