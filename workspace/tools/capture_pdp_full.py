import asyncio
import json
from playwright.async_api import async_playwright

async def capture_full_pdp():
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

        captured_apis = {}
        async def on_response(res):
            url = res.url
            if any(k in url for k in ["get_pc", "item/get", "init"]):
                try:
                    data = await res.json()
                    captured_apis[url] = data
                    print(f"Captured API: {url[:100]}")
                except Exception:
                    pass

        page.on("response", on_response)

        print("Navigating...")
        await page.goto("https://s.shopee.co.id/8AWbWHUOPx", wait_until="domcontentloaded")

        for _ in range(15):
            await page.wait_for_timeout(1000)
            if "product" in page.url and "verify" not in page.url:
                await page.wait_for_timeout(6000)
                break

        print("Page URL:", page.url)
        print("Page Title:", await page.title())

        # Let's inspect rendered text containing "Rp"
        prices = await page.evaluate("""() => {
            const matches = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.children.length === 0 && el.innerText && el.innerText.includes('Rp')) {
                    matches.push(el.innerText.trim());
                }
            });
            return Array.from(new Set(matches));
        }""")
        print("Rendered prices:", prices)

        with open("tools/live_captured_apis.json", "w", encoding="utf-8") as f:
            json.dump(captured_apis, f, indent=2)

        await page.screenshot(path="tools/rendered_product.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_full_pdp())
