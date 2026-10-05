import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

TARGET_URL = "https://s.shopee.co.id/80DBs5lgX2"

async def run():
    print(f"Opening {TARGET_URL}")
    captured_data = {
        "pdp_api": None,
        "item_api": None,
        "all_apis": [],
        "ld_json": [],
        "title": "",
        "url": "",
        "images": []
    }

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
            viewport={"width": 1440, "height": 900},
            locale="id-ID"
        )
        page = await context.new_page()

        async def on_response(response):
            try:
                url = response.url
                if "api/v4/pdp/get_pc" in url or "api/v4/item/get" in url:
                    print(f"Hit API: {url[:100]}")
                    try:
                        data = await response.json()
                        captured_data["all_apis"].append({"url": url, "data": data})
                        if "api/v4/pdp/get_pc" in url:
                            captured_data["pdp_api"] = data
                        elif "api/v4/item/get" in url:
                            captured_data["item_api"] = data
                    except Exception as ex:
                        print("Json parse error:", ex)
            except Exception:
                pass

        page.on("response", on_response)

        # domcontentloaded is reliable and fast
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        print("Page DOM loaded. Current URL:", page.url)

        # Wait for Shopee to execute JS and fetch data
        await page.wait_for_timeout(8000)
        captured_data["url"] = page.url
        captured_data["title"] = await page.title()
        print("Title after wait:", captured_data["title"])

        # Try to extract LD+JSON
        try:
            ld_scripts = await page.eval_on_selector_all(
                'script[type="application/ld+json"]',
                'elements => elements.map(e => e.textContent)'
            )
            for raw_ld in ld_scripts:
                try:
                    captured_data["ld_json"].append(json.loads(raw_ld))
                except Exception:
                    pass
            print(f"Extracted {len(captured_data['ld_json'])} ld+json elements")
        except Exception as e:
            print("Error extracting ld_json:", e)

        # If pdp_api wasn't captured, scroll down to trigger PDP request
        if not captured_data["pdp_api"]:
            print("Scrolling down to trigger more requests...")
            for _ in range(3):
                await page.mouse.wheel(0, 500)
                await page.wait_for_timeout(2000)

        # Take screenshot
        await page.screenshot(path="tools/sprint30_page_preview.png")

        # Extract images from DOM
        try:
            img_srcs = await page.eval_on_selector_all(
                'img',
                'elements => elements.map(e => e.src)'
            )
            captured_data["images"] = list(set([src for src in img_srcs if src]))
            print(f"Extracted {len(captured_data['images'])} images from DOM")
        except Exception as e:
            print("Error extracting img srcs:", e)

        await browser.close()

    with open("tools/sprint30_crawl_result.json", "w", encoding="utf-8") as f:
        json.dump(captured_data, f, indent=2, ensure_ascii=False)
    print("Done. Saved sprint30_crawl_result.json")

if __name__ == "__main__":
    asyncio.run(run())
