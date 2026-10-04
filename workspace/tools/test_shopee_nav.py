import asyncio
import json
import httpx
from playwright.async_api import async_playwright

async def inspect_page():
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
            if "api/v4" in response.url or "api/v2" in response.url:
                try:
                    data = await response.json()
                    api_responses[response.url] = data
                except Exception:
                    pass

        page.on("response", on_response)

        print("Navigating...")
        await page.goto("https://s.shopee.co.id/8AWbWHUOPx", wait_until="commit", timeout=60000)
        
        # Wait until redirection settles
        for _ in range(15):
            await page.wait_for_timeout(1000)
            cur_url = page.url
            print(f"Current URL: {cur_url[:80]}... Title: {await page.title()}")
            if "Loading" not in await page.title() and ("product" in cur_url or "item" in cur_url or "shopee.co.id" in cur_url):
                # Check if page has rendered content
                body_len = await page.evaluate("() => document.body.innerText.length")
                if body_len > 100:
                    break

        await page.wait_for_timeout(3000)
        final_url = page.url
        title = await page.title()
        print(f"Settled URL: {final_url}")
        print(f"Settled Title: {title}")

        # Check API responses captured
        print(f"Captured {len(api_responses)} API responses")
        for u in api_responses.keys():
            print("Captured API URL:", u[:100])

        # Evaluate body text sample
        body_text = await page.evaluate("() => document.body.innerText.slice(0, 1000)")
        print("Body text sample:\n", body_text[:500])

        await page.screenshot(path="tools/shopee_settled.png")
        await browser.close()
        return api_responses

if __name__ == "__main__":
    asyncio.run(inspect_page())
