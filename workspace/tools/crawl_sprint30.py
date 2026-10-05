import asyncio
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
import httpx
from playwright.async_api import async_playwright

TARGET_SHORTLINK = "https://s.shopee.co.id/80DBs5lgX2"
OUTPUT_JSON_PATH = Path("docs/sprint30_campaign.json")
IMAGE_DIR_RELATIVE = "workspace/product_images/sprint30"
IMAGE_DIR_PATHS = [
    Path("workspace/product_images/sprint30"),
    Path("product_images/sprint30"),
]

def ensure_directories():
    for p in IMAGE_DIR_PATHS:
        p.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

async def crawl_shopee():
    ensure_directories()
    
    captured_data = {
        "api_items": [],
        "ld_jsons": [],
        "initial_state": None,
        "final_url": "",
        "title": "",
        "dom_text": ""
    }

    print(f"Starting crawl for {TARGET_SHORTLINK}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="id-ID",
            timezone_id="Asia/Jakarta"
        )
        
        page = await context.new_page()

        async def handle_response(response):
            try:
                url = response.url
                if any(k in url for k in ["api/v4/item/get", "api/v4/pdp/get_pc", "api/v2/item/get", "api/v4/product/get"]):
                    try:
                        data = await response.json()
                        captured_data["api_items"].append({"url": url, "data": data})
                        print(f"Captured PDP API: {url[:80]}")
                    except Exception:
                        pass
                elif "api" in url and ("item" in url or "product" in url):
                    content_type = response.headers.get("content-type", "")
                    if "application/json" in content_type:
                        try:
                            data = await response.json()
                            captured_data["api_items"].append({"url": url, "data": data})
                        except Exception:
                            pass
            except Exception as e:
                pass

        page.on("response", handle_response)

        try:
            print("Navigating to shortlink...")
            response = await page.goto(TARGET_SHORTLINK, wait_until="load", timeout=45000)
            await page.wait_for_timeout(5000)
            captured_data["final_url"] = page.url
            print(f"Final URL: {captured_data['final_url']}")

            # Scroll to trigger lazy loading and PDP APIs
            for i in range(5):
                await page.mouse.wheel(0, 600)
                await page.wait_for_timeout(1000)

            captured_data["title"] = await page.title()
            
            # Extract application/ld+json
            ld_scripts = await page.eval_on_selector_all('script[type="application/ld+json"]', 'elements => elements.map(e => e.textContent)')
            for raw_ld in ld_scripts:
                try:
                    parsed = json.loads(raw_ld)
                    captured_data["ld_jsons"].append(parsed)
                except Exception:
                    pass

            # Extract window.__INITIAL_STATE__ if present
            try:
                state = await page.evaluate("() => window.__INITIAL_STATE__ || null")
                if state:
                    captured_data["initial_state"] = state
            except Exception:
                pass

            # Capture DOM text and elements
            captured_data["dom_text"] = await page.content()

            # Save screenshot for debugging
            await page.screenshot(path="tools/sprint30_rendered_page.png", full_page=True)

        except Exception as e:
            print(f"Error during page navigation: {e}")
        finally:
            await browser.close()

    return captured_data

if __name__ == "__main__":
    data = asyncio.run(crawl_shopee())
    with open("tools/sprint30_captured_raw.json", "w", encoding="utf-8") as f:
        json.dump({
            "final_url": data["final_url"],
            "title": data["title"],
            "api_count": len(data["api_items"]),
            "ld_count": len(data["ld_jsons"]),
            "has_initial_state": data["initial_state"] is not None
        }, f, indent=2)
    print("Crawl complete, raw summary saved.")
