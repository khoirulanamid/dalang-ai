import asyncio
import json
from playwright.async_api import async_playwright

async def get_shopee_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1920,1080"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
        )
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)

        page = await context.new_page()

        api_future = asyncio.Future()

        async def on_response(res):
            if "api/v4/pdp/get_pc" in res.url or "api/v4/item/get" in res.url:
                try:
                    data = await res.json()
                    print(f"Captured response from {res.url[:80]} with status {res.status}")
                    if not api_future.done():
                        api_future.set_result(data)
                except Exception as e:
                    print("Error parsing json:", e)

        page.on("response", on_response)

        print("Navigating...")
        await page.goto("https://s.shopee.co.id/8AWbWHUOPx", wait_until="domcontentloaded")

        try:
            pdp_data = await asyncio.wait_for(api_future, timeout=20.0)
            print("Successfully received PDP response!")
            with open("tools/live_pdp_get_pc.json", "w", encoding="utf-8") as f:
                json.dump(pdp_data, f, indent=2)
        except asyncio.TimeoutError:
            print("Timed out waiting for pdp response")

        # Also wait a few seconds and extract rendered text
        await page.wait_for_timeout(4000)
        
        # Extract title and price from DOM
        dom_info = await page.evaluate("""() => {
            const h1 = document.querySelector('h1') || document.querySelector('.WB8f5Q');
            // Look for price elements
            const priceTexts = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.children.length === 0 && el.innerText && (el.innerText.includes('Rp') || el.innerText.includes('rb'))) {
                    priceTexts.push(el.innerText.trim());
                }
            });
            return {
                title: h1 ? h1.innerText : document.title,
                prices: Array.from(new Set(priceTexts))
            };
        }""")
        print("DOM Info:", dom_info)

        await page.screenshot(path="tools/rendered_product.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_shopee_data())
