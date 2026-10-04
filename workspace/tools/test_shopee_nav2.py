import asyncio
import json
import httpx
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="id-ID"
        )
        page = await context.new_page()

        api_responses = {}
        async def on_response(response):
            if any(k in response.url for k in ["api/v4/item/get", "api/v4/pdp/get_pc", "api/v2/item/get", "get_item_detail", "get_pc"]):
                try:
                    data = await response.json()
                    api_responses[response.url] = data
                    print("Found API target:", response.url[:120])
                except Exception:
                    pass

        page.on("response", on_response)

        # Go directly or follow
        print("Navigating...")
        await page.goto("https://s.shopee.co.id/8AWbWHUOPx")
        
        # Wait 10 seconds for all redirections and client side loads to finish
        print("Waiting 10s...")
        await asyncio.sleep(10)
        
        # Now try to get URL and title
        print("Current URL:", page.url)
        print("Current Title:", await page.title())

        # Wait for network idle
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            print("wait_for_load_state warning:", e)

        print("Final URL:", page.url)
        print("Final Title:", await page.title())

        content = await page.content()
        with open("tools/page_source.html", "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Captured {len(api_responses)} matching API responses")
        with open("tools/captured_apis.json", "w", encoding="utf-8") as f:
            json.dump(api_responses, f, indent=2)

        await page.screenshot(path="tools/shopee_page.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
