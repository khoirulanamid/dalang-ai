import asyncio
from playwright.async_api import async_playwright

async def test_stealth():
    async with async_playwright() as p:
        # Using real browser args
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

        apis = {}
        async def on_response(res):
            url = res.url
            if any(k in url for k in ["api/v4/item/get", "api/v4/pdp/get_pc", "api/v2/item/get", "get_item_detail", "get_pc"]):
                try:
                    apis[url] = await res.json()
                    print(f"Captured: {url[:100]}")
                except Exception:
                    pass

        page.on("response", on_response)

        print("Navigating to shortlink...")
        await page.goto("https://s.shopee.co.id/8AWbWHUOPx", wait_until="domcontentloaded")

        # Wait for navigation / redirects
        for i in range(12):
            await page.wait_for_timeout(1000)
            print(f"[{i}s] URL: {page.url[:80]} | Title: {await page.title()}")
            if "verify/traffic" in page.url:
                print("Hit traffic error!")
                break
            if "product" in page.url and "verify" not in page.url:
                # wait a bit for data to load
                await page.wait_for_timeout(4000)
                break

        print("Final URL:", page.url)
        print("Final Title:", await page.title())
        await page.screenshot(path="tools/stealth_test.png")

        if apis:
            print("Successfully captured API data keys:", apis.keys())
            first_val = list(apis.values())[0]
            print("API response preview:", str(first_val)[:500])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_stealth())
