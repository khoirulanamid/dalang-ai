import asyncio
from playwright.async_api import async_playwright

async def probe():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="id-ID",
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()

        api_calls = []

        async def on_response(resp):
            ct = resp.headers.get("content-type", "")
            if "json" in ct:
                if any(x in resp.url for x in ["item", "product", "pdp", "shop"]):
                    try:
                        data = await resp.json()
                        api_calls.append({"url": resp.url, "data": data})
                    except Exception:
                        pass

        page.on("response", on_response)

        print("Navigating...")
        await page.goto("https://s.shopee.co.id/6L4wk65TN6", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(6)
        print("Current URL:", page.url)
        print("Title:", await page.title())

        # progressive scroll
        for _ in range(4):
            await page.mouse.wheel(0, 800)
            await asyncio.sleep(1.5)

        body_text = await page.inner_text("body")
        print("Body text length:", len(body_text))
        print("Body sample:")
        print(body_text[:1500])

        images = await page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll('img'));
            return imgs.map(i => i.src);
        }""")
        print("Found images on page:", len(images))
        print("API calls count:", len(api_calls))

        with open("tools/probe_data.json", "w", encoding="utf-8") as f:
            import json
            json.dump({
                "url": page.url,
                "title": await page.title(),
                "body": body_text,
                "images": images,
                "api_calls": api_calls
            }, f, indent=2, ensure_ascii=False)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(probe())
